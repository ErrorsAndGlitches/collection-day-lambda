use crate::error::CalendarError;
use chrono::NaiveDate;

/// A single collection service (e.g. Garbage, Recycle) and the dates on which
/// it is picked up.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ServiceCalendar {
    description: String,
    pickup_dates: Vec<NaiveDate>,
}

impl ServiceCalendar {
    pub fn new(description: impl Into<String>, pickup_dates: Vec<NaiveDate>) -> Self {
        Self {
            description: description.into(),
            pickup_dates,
        }
    }

    pub fn description(&self) -> &str {
        &self.description
    }

    /// The first pickup date on or after `current_date`.
    pub fn earliest_date(&self, current_date: NaiveDate) -> Result<NaiveDate, CalendarError> {
        self.pickup_dates
            .iter()
            .copied()
            .find(|&d| d >= current_date)
            .ok_or(CalendarError::NoUpcomingPickup(current_date))
    }

    pub fn has_pickup(&self, date: NaiveDate) -> bool {
        self.pickup_dates.contains(&date)
    }
}

/// Builds the next-pickup message across all services, matching the format
/// produced by the original Python implementation, e.g.
/// `Next pick up will be on Thu 14 Jan 2021 and will include [Garbage,Recycle]`.
pub fn next_collection_msg(
    calendars: &[ServiceCalendar],
    today: NaiveDate,
) -> Result<String, CalendarError> {
    let earliest = calendars
        .iter()
        .map(|c| c.earliest_date(today))
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .min()
        .ok_or(CalendarError::NoUpcomingPickup(today))?;

    let pickup_items: Vec<&str> = calendars
        .iter()
        .filter(|c| c.has_pickup(earliest))
        .map(|c| c.description())
        .collect();

    Ok(format!(
        "Next pick up will be on {} and will include [{}]",
        earliest.format("%a %d %b %Y"),
        pickup_items.join(",")
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn d(y: i32, m: u32, day: u32) -> NaiveDate {
        NaiveDate::from_ymd_opt(y, m, day).unwrap()
    }

    fn recycle() -> ServiceCalendar {
        ServiceCalendar::new(
            "Recycle",
            vec![d(2020, 12, 31), d(2021, 1, 14), d(2021, 1, 28)],
        )
    }

    #[test]
    fn earliest_date_returns_first_on_or_after() {
        let c = recycle();
        assert_eq!(c.earliest_date(d(2021, 1, 7)).unwrap(), d(2021, 1, 14));
        assert_eq!(c.earliest_date(d(2021, 1, 13)).unwrap(), d(2021, 1, 14));
        assert_eq!(c.earliest_date(d(2021, 1, 14)).unwrap(), d(2021, 1, 14));
        assert_eq!(c.earliest_date(d(2021, 1, 15)).unwrap(), d(2021, 1, 28));
    }

    #[test]
    fn earliest_date_missing_is_error() {
        assert!(recycle().earliest_date(d(2021, 1, 29)).is_err());
    }

    #[test]
    fn has_pickup() {
        let c = recycle();
        assert!(c.has_pickup(d(2021, 1, 14)));
        assert!(c.has_pickup(d(2021, 1, 28)));
        assert!(!c.has_pickup(d(2021, 1, 13)));
        assert!(!c.has_pickup(d(2021, 1, 15)));
    }

    fn all_services() -> Vec<ServiceCalendar> {
        vec![
            ServiceCalendar::new(
                "Garbage",
                vec![
                    d(2020, 12, 31),
                    d(2021, 1, 7),
                    d(2021, 1, 14),
                    d(2021, 1, 21),
                    d(2021, 1, 28),
                ],
            ),
            ServiceCalendar::new(
                "Recycle",
                vec![d(2020, 12, 31), d(2021, 1, 14), d(2021, 1, 28)],
            ),
            ServiceCalendar::new(
                "Food/Yard Waste",
                vec![
                    d(2020, 12, 31),
                    d(2021, 1, 7),
                    d(2021, 1, 14),
                    d(2021, 1, 21),
                    d(2021, 1, 28),
                ],
            ),
        ]
    }

    #[test]
    fn message_includes_all_services_on_shared_date() {
        let msg = next_collection_msg(&all_services(), d(2021, 1, 13)).unwrap();
        assert_eq!(
            msg,
            "Next pick up will be on Thu 14 Jan 2021 and will include [Garbage,Recycle,Food/Yard Waste]"
        );
    }

    #[test]
    fn message_excludes_services_without_pickup_on_date() {
        let msg = next_collection_msg(&all_services(), d(2021, 1, 15)).unwrap();
        assert_eq!(
            msg,
            "Next pick up will be on Thu 21 Jan 2021 and will include [Garbage,Food/Yard Waste]"
        );
    }
}
