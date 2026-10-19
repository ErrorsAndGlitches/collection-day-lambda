//! Local command-line entrypoint, mirroring the original Python `__main__`.
//!
//! Lets the tool be run from a developer machine, either printing the message
//! (`--print`) or sending it via SNS using a named AWS profile/region.

use crate::run_notification;
use cdl_core::{SnsNotification, StdoutNotification};
use clap::Parser;
use lambda_runtime::Error;

const DEFAULT_AWS_REGION: &str = "us-west-2";

#[derive(Parser)]
#[command(about = "Run collection handler locally")]
struct Args {
    /// Address to look up the collection for.
    #[arg(long)]
    address: String,

    /// Phone numbers to send the text message to.
    #[arg(long, num_args = 0.., value_delimiter = ' ')]
    phone_numbers: Vec<String>,

    /// AWS profile to use for credentials (SNS mode).
    #[arg(long)]
    aws_profile: Option<String>,

    /// AWS region to use.
    #[arg(long, default_value = DEFAULT_AWS_REGION)]
    aws_region: String,

    /// Only print the message; do not send SNS messages.
    #[arg(long)]
    print: bool,
}

pub async fn run() -> Result<(), Error> {
    let args = Args::parse();

    if args.print {
        let notification = StdoutNotification::new(&args.address);
        run_notification(&notification, &args.address).await?;
    } else {
        let mut loader = aws_config::defaults(aws_config::BehaviorVersion::latest())
            .region(aws_config::Region::new(args.aws_region));
        if let Some(profile) = &args.aws_profile {
            loader = loader.profile_name(profile);
        }
        let config = loader.load().await;
        let sns = aws_sdk_sns::Client::new(&config);
        let notification = SnsNotification::new(sns, args.phone_numbers);
        run_notification(&notification, &args.address).await?;
    }
    Ok(())
}
