//! Integration test for the full calendar flow, mocked with `wiremock` and
//! driven by the JSON fixtures in the repository-root `tests/` directory.

use cdl_core::{next_collection_msg, CollectionCalendarClient};
use chrono::NaiveDate;
use wiremock::matchers::{method, path};
use wiremock::{Mock, MockServer, ResponseTemplate};

/// Fixtures live in the repository-root `tests/` directory;
/// `CARGO_MANIFEST_DIR` is `crates/cdl-core`.
fn fixture(name: &str) -> String {
    let path = format!("{}/../../tests/{}", env!("CARGO_MANIFEST_DIR"), name);
    std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("reading {path}: {e}"))
}

async fn mock_server() -> MockServer {
    let server = MockServer::start().await;
    let routes = [
        (
            "/rest/serviceorder/findaddress",
            "find-address-response.json",
        ),
        (
            "/rest/serviceorder/findAccount",
            "find-account-response.json",
        ),
        ("/rest/auth/guest", "token-response.json"),
        ("/rest/guest/swsummary", "solid-waste-summary-response.json"),
        (
            "/rest/solidwastecalendar",
            "solid-waste-calendar-response.json",
        ),
    ];
    for (route, file) in routes {
        Mock::given(method("POST"))
            .and(path(route))
            .respond_with(
                ResponseTemplate::new(200).set_body_raw(fixture(file), "application/json"),
            )
            .mount(&server)
            .await;
    }
    server
}

fn d(y: i32, m: u32, day: u32) -> NaiveDate {
    NaiveDate::from_ymd_opt(y, m, day).unwrap()
}

#[tokio::test]
async fn full_flow_shared_pickup_date() {
    let server = mock_server().await;
    let client = CollectionCalendarClient::with_base_url(server.uri());

    let calendars = client.service_calendars("STREET ADDRESS").await.unwrap();
    let msg = next_collection_msg(&calendars, d(2021, 1, 13)).unwrap();

    assert_eq!(
        msg,
        "Next pick up will be on Thu 14 Jan 2021 and will include [Garbage,Recycle,Food/Yard Waste]"
    );
}

#[tokio::test]
async fn full_flow_excludes_recycle_off_week() {
    let server = mock_server().await;
    let client = CollectionCalendarClient::with_base_url(server.uri());

    let calendars = client.service_calendars("STREET ADDRESS").await.unwrap();
    let msg = next_collection_msg(&calendars, d(2021, 1, 15)).unwrap();

    assert_eq!(
        msg,
        "Next pick up will be on Thu 21 Jan 2021 and will include [Garbage,Food/Yard Waste]"
    );
}
