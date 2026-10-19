use crate::calendar::ServiceCalendar;
use crate::error::CalendarError;
use chrono::NaiveDate;
use serde::Deserialize;
use serde_json::json;

const DATE_FORMAT: &str = "%m/%d/%Y";

/// Client for the Seattle (myutilities) solid-waste calendar API.
///
/// Mirrors the five-step flow of the original Python implementation:
/// find address -> find account -> guest token -> summary -> calendar.
/// The base URL is injectable so tests can point it at a mock server.
pub struct CollectionCalendarClient {
    http: reqwest::Client,
    base_url: String,
}

impl CollectionCalendarClient {
    /// Client against the live myutilities endpoint.
    pub fn new() -> Self {
        Self::with_base_url("https://myutilities.seattle.gov")
    }

    /// Client against an arbitrary base URL (used by tests).
    pub fn with_base_url(base_url: impl Into<String>) -> Self {
        Self {
            http: reqwest::Client::new(),
            base_url: base_url.into(),
        }
    }

    fn url(&self, path: &str) -> String {
        format!("{}{}", self.base_url, path)
    }

    /// Fetches every service's pickup calendar for `address`.
    pub async fn service_calendars(
        &self,
        address: &str,
    ) -> Result<Vec<ServiceCalendar>, CalendarError> {
        let prem_code = self.find_address(address).await?;
        let account = self.find_account(&prem_code).await?;
        let token = self.guest_token().await?;
        let summary = self
            .solid_waste_summary(&token, &account.account_number)
            .await?;
        self.solid_waste_calendar(&token, &account, &summary).await
    }

    async fn find_address(&self, address: &str) -> Result<String, CalendarError> {
        let body = json!({
            "address": { "addressLine1": address, "city": "", "zip": "" }
        });
        let resp = self
            .post_json(
                "/rest/serviceorder/findaddress",
                "find_address",
                &body,
                None,
            )
            .await?;
        let parsed: FindAddressResponse = parse(resp, "find_address").await?;
        parsed
            .address
            .into_iter()
            .next()
            .map(|a| a.prem_code)
            .ok_or(CalendarError::MissingField("address[0].premCode"))
    }

    async fn find_account(&self, prem_code: &str) -> Result<Account, CalendarError> {
        let body = json!({ "address": { "premCode": prem_code } });
        let resp = self
            .post_json(
                "/rest/serviceorder/findAccount",
                "find_account",
                &body,
                None,
            )
            .await?;
        let parsed: FindAccountResponse = parse(resp, "find_account").await?;
        Ok(parsed.account)
    }

    async fn guest_token(&self) -> Result<String, CalendarError> {
        let resp = self
            .post_json("/rest/auth/guest", "token", &json!({}), None)
            .await?;
        let parsed: TokenResponse = parse(resp, "token").await?;
        Ok(format!("{} {}", parsed.token_type, parsed.access_token))
    }

    async fn solid_waste_summary(
        &self,
        auth: &str,
        account_number: &str,
    ) -> Result<Summary, CalendarError> {
        let body = json!({
            "customerId": "guest",
            "accountContext": {
                "accountNumber": account_number,
                "personId": null,
                "companyCd": null,
                "serviceAddress": null
            }
        });
        let resp = self
            .post_json("/rest/guest/swsummary", "summary", &body, Some(auth))
            .await?;
        let parsed: SummaryResponse = parse(resp, "summary").await?;
        let account_summary = parsed.account_summary_type;
        let services = account_summary
            .sw_services
            .into_iter()
            .next()
            .map(|s| s.services)
            .unwrap_or_default();
        Ok(Summary {
            person_id: account_summary.person_id,
            endpoints: services
                .into_iter()
                .map(|s| ServiceEndpoint {
                    id: s.service_point_id,
                    description: s.description,
                })
                .collect(),
        })
    }

    async fn solid_waste_calendar(
        &self,
        auth: &str,
        account: &Account,
        summary: &Summary,
    ) -> Result<Vec<ServiceCalendar>, CalendarError> {
        let body = json!({
            "customerId": "guest",
            "accountContext": {
                "accountNumber": account.account_number,
                "personId": summary.person_id,
                "companyCd": account.company_cd
            },
            "servicePoints": summary.endpoints.iter().map(|e| &e.id).collect::<Vec<_>>()
        });
        let resp = self
            .post_json("/rest/solidwastecalendar", "calendar", &body, Some(auth))
            .await?;
        let parsed: CalendarResponse = parse(resp, "calendar").await?;

        summary
            .endpoints
            .iter()
            .map(|endpoint| {
                let raw_dates = parsed
                    .calendar
                    .get(&endpoint.id)
                    .ok_or(CalendarError::MissingField("calendar.<servicePointId>"))?;
                let dates = raw_dates
                    .iter()
                    .map(|s| {
                        NaiveDate::parse_from_str(s, DATE_FORMAT).map_err(|source| {
                            CalendarError::DateParse {
                                value: s.clone(),
                                source,
                            }
                        })
                    })
                    .collect::<Result<Vec<_>, _>>()?;
                Ok(ServiceCalendar::new(endpoint.description.clone(), dates))
            })
            .collect()
    }

    async fn post_json(
        &self,
        path: &str,
        request_name: &'static str,
        body: &serde_json::Value,
        auth: Option<&str>,
    ) -> Result<reqwest::Response, CalendarError> {
        let mut req = self.http.post(self.url(path)).json(body);
        if let Some(auth) = auth {
            req = req.header("Authorization", auth);
        }
        let resp = req.send().await?;
        if resp.status().as_u16() != 200 {
            return Err(CalendarError::BadStatus {
                request: request_name,
                status: resp.status().as_u16(),
            });
        }
        Ok(resp)
    }
}

impl Default for CollectionCalendarClient {
    fn default() -> Self {
        Self::new()
    }
}

async fn parse<T: for<'de> Deserialize<'de>>(
    resp: reqwest::Response,
    request_name: &'static str,
) -> Result<T, CalendarError> {
    // The API advertises JSON but the exact content-type is not relied upon;
    // deserialize from the response body directly.
    let bytes = resp.bytes().await?;
    serde_json::from_slice(&bytes).map_err(|_| CalendarError::MissingField(request_name))
}

/// A service point id paired with its human description.
struct ServiceEndpoint {
    id: String,
    description: String,
}

/// Flattened summary data needed by the calendar request.
struct Summary {
    person_id: Option<String>,
    endpoints: Vec<ServiceEndpoint>,
}

#[derive(Deserialize)]
struct FindAddressResponse {
    address: Vec<AddressEntry>,
}

#[derive(Deserialize)]
struct AddressEntry {
    #[serde(rename = "premCode")]
    prem_code: String,
}

#[derive(Deserialize)]
struct FindAccountResponse {
    account: Account,
}

#[derive(Deserialize)]
struct Account {
    #[serde(rename = "accountNumber")]
    account_number: String,
    #[serde(rename = "companyCd")]
    company_cd: String,
}

#[derive(Deserialize)]
struct TokenResponse {
    access_token: String,
    token_type: String,
}

#[derive(Deserialize)]
struct SummaryResponse {
    #[serde(rename = "accountSummaryType")]
    account_summary_type: AccountSummaryType,
}

#[derive(Deserialize)]
struct AccountSummaryType {
    #[serde(rename = "personId")]
    person_id: Option<String>,
    #[serde(rename = "swServices")]
    sw_services: Vec<SwService>,
}

#[derive(Deserialize)]
struct SwService {
    services: Vec<Service>,
}

#[derive(Deserialize)]
struct Service {
    #[serde(rename = "servicePointId")]
    service_point_id: String,
    description: String,
}

#[derive(Deserialize)]
struct CalendarResponse {
    calendar: std::collections::HashMap<String, Vec<String>>,
}
