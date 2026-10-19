//! Core logic for the collection-day Lambda: querying the Seattle utilities
//! calendar API and formatting the next-pickup message.
//!
//! Phase 0 scaffold — ports of `collection_calendar.py` and `notifications.py`
//! land here in later phases.

/// Placeholder to verify the workspace builds and tests run.
/// Removed once real modules are added.
pub fn placeholder() -> &'static str {
    "cdl-core"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn placeholder_returns_crate_name() {
        assert_eq!(placeholder(), "cdl-core");
    }
}
