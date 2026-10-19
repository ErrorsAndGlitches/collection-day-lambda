use thiserror::Error;

/// Errors produced while fetching or interpreting the collection calendar.
#[derive(Debug, Error)]
pub enum CalendarError {
    #[error("HTTP request failed: {0}")]
    Http(#[from] reqwest::Error),

    #[error("unexpected response for {request}: status {status}")]
    BadStatus { request: &'static str, status: u16 },

    #[error("missing or malformed field `{0}` in response")]
    MissingField(&'static str),

    #[error("could not parse date `{value}`: {source}")]
    DateParse {
        value: String,
        source: chrono::ParseError,
    },

    #[error("no pickup date on or after {0}")]
    NoUpcomingPickup(chrono::NaiveDate),
}
