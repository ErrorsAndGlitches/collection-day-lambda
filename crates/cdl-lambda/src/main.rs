//! Lambda entrypoint binary, named `bootstrap` so the `provided.al2023` base
//! image can exec it directly.
//!
//! Runs as an AWS Lambda handler by default, or as a local CLI when invoked
//! with the `--address` flag.

use cdl_core::{
    send_collection_day_notification, CalendarError, CollectionCalendarClient, Notification,
    SnsNotification,
};
use chrono::NaiveDate;
use chrono_tz::America::Los_Angeles;
use lambda_runtime::{service_fn, Error, LambdaEvent};
use serde_json::{json, Value};

mod cli;

/// "Today" in the collection service's `America/Los_Angeles` timezone.
fn today_pacific() -> NaiveDate {
    chrono::Utc::now().with_timezone(&Los_Angeles).date_naive()
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    if std::env::args().any(|a| a == "--address") {
        return cli::run().await;
    }
    lambda_runtime::run(service_fn(handler)).await
}

/// Lambda handler: reads `ADDRESS` and `PHONE_NUMBERS` from the environment,
/// sends the SMS, and returns a success payload.
async fn handler(_event: LambdaEvent<Value>) -> Result<Value, Error> {
    let address = std::env::var("ADDRESS").map_err(|_| "ADDRESS env var is required")?;
    let phone_numbers: Vec<String> = std::env::var("PHONE_NUMBERS")
        .map_err(|_| "PHONE_NUMBERS env var is required")?
        .split(',')
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
        .collect();

    let config = aws_config::load_defaults(aws_config::BehaviorVersion::latest()).await;
    let sns = aws_sdk_sns::Client::new(&config);
    let notification = SnsNotification::new(sns, phone_numbers);

    run_notification(&notification, &address).await?;
    Ok(json!({ "result": "success" }))
}

/// Shared send path used by both the handler and the CLI.
pub(crate) async fn run_notification(
    notification: &dyn Notification,
    address: &str,
) -> Result<(), CalendarError> {
    let client = CollectionCalendarClient::new();
    send_collection_day_notification(&client, notification, address, today_pacific()).await
}
