//! Core logic for the collection-day Lambda: querying the Seattle utilities
//! calendar API and formatting the next-pickup message.
//!
//! The crate is split into a pure domain layer (`calendar`) and an HTTP layer
//! (`client`) so the formatting logic can be unit-tested without network access
//! and the request flow can be tested against a mock server.

mod calendar;
mod client;
mod error;

pub use calendar::{next_collection_msg, ServiceCalendar};
pub use client::CollectionCalendarClient;
pub use error::CalendarError;
