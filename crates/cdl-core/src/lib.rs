//! Core logic for the collection-day Lambda: querying the Seattle utilities
//! calendar API and formatting the next-pickup message.
//!
//! The crate is split into a pure domain layer (`calendar`) and an HTTP layer
//! (`client`) so the formatting logic can be unit-tested without network access
//! and the request flow can be tested against a mock server. The
//! `notifications` layer delivers the formatted message.

mod calendar;
mod client;
mod error;
mod notifications;

use chrono::NaiveDate;

pub use calendar::{next_collection_msg, ServiceCalendar};
pub use client::CollectionCalendarClient;
pub use error::CalendarError;
pub use notifications::{Notification, SnsNotification, StdoutNotification};

/// Fetches the next collection for `address` and delivers it through
/// `notification`. The single entrypoint shared by the CLI and Lambda handler.
pub async fn send_collection_day_notification(
    client: &CollectionCalendarClient,
    notification: &dyn Notification,
    address: &str,
    today: NaiveDate,
) -> Result<(), CalendarError> {
    let calendars = client.service_calendars(address).await?;
    let msg = next_collection_msg(&calendars, today)?;
    notification.send(&msg).await
}
