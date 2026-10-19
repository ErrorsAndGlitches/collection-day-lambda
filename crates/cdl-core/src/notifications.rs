use crate::error::CalendarError;
use async_trait::async_trait;

/// A sink for the formatted collection message. Lets the CLI and Lambda
/// handler share a single send path regardless of destination.
#[async_trait]
pub trait Notification {
    async fn send(&self, msg: &str) -> Result<(), CalendarError>;
}

/// Prints the message to stdout. Used by the CLI `--print` mode.
pub struct StdoutNotification {
    address: String,
}

impl StdoutNotification {
    pub fn new(address: impl Into<String>) -> Self {
        Self {
            address: address.into(),
        }
    }
}

#[async_trait]
impl Notification for StdoutNotification {
    async fn send(&self, msg: &str) -> Result<(), CalendarError> {
        println!("Pick up status for \"{}\":", self.address);
        println!("{msg}");
        Ok(())
    }
}

/// Sends the message as a transactional SMS to each phone number via SNS.
pub struct SnsNotification {
    client: aws_sdk_sns::Client,
    phone_numbers: Vec<String>,
}

impl SnsNotification {
    pub fn new(client: aws_sdk_sns::Client, phone_numbers: Vec<String>) -> Self {
        Self {
            client,
            phone_numbers,
        }
    }
}

#[async_trait]
impl Notification for SnsNotification {
    async fn send(&self, msg: &str) -> Result<(), CalendarError> {
        use aws_sdk_sns::types::MessageAttributeValue;

        let sms_type = MessageAttributeValue::builder()
            .data_type("String")
            .string_value("Transactional")
            .build()
            .map_err(|e| CalendarError::Notification(format!("building SMS attribute: {e}")))?;

        for phone_number in &self.phone_numbers {
            self.client
                .publish()
                .phone_number(phone_number)
                .message(msg)
                .message_attributes("AWS.SNS.SMS.SMSType", sms_type.clone())
                .send()
                .await
                .map_err(|e| {
                    CalendarError::Notification(format!("SNS publish to {phone_number}: {e}"))
                })?;
        }
        Ok(())
    }
}
