//! Lambda entrypoint binary.
//!
//! The binary is named `bootstrap` (see Cargo.toml `[[bin]]`) so the
//! `provided.al2023` Lambda base image can exec it directly.
//!
//! Phase 1 placeholder — the `lambda_runtime` handler, notifications, and CLI
//! land in Phase 2. For now this exercises the core client end-to-end when run
//! directly with an address argument.

use cdl_core::{next_collection_msg, CollectionCalendarClient};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let address = std::env::args()
        .nth(1)
        .ok_or("usage: bootstrap <address>")?;
    let today = chrono::Local::now().date_naive();

    let calendars = CollectionCalendarClient::new()
        .service_calendars(&address)
        .await?;
    println!("{}", next_collection_msg(&calendars, today)?);
    Ok(())
}
