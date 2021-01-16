from argparse import ArgumentParser
import boto3

from cdl.cdl import send_collection_day_notification
from cdl.notifications import SnsNotification, StdoutNotification

DEFAULT_AWS_REGION = 'us-west-2'


def args():
    parser = ArgumentParser(description='Run collection handler locally')
    parser.add_argument('--aws-profile', required=True, help='AWS profile to use for credentials')
    parser.add_argument(
        '--aws-region', required=False, default=DEFAULT_AWS_REGION,
        help='AWS region to use; Default: {}'.format(DEFAULT_AWS_REGION)
    )
    parser.add_argument('--address', required=True, help='Address to look up the collection for')
    parser.add_argument(
        '--phone-numbers', required=False, nargs='+', default=[], help='Phone numbers to send the text message to'
    )
    parser.add_argument(
        '--print', required=False, action='store_true', help='Only print the message, do not send SNS messages'
    )
    return parser.parse_args()


def main():
    cli_args = args()

    if cli_args.print:
        notification = StdoutNotification(cli_args.address)
    else:
        boto3.setup_default_session(profile_name=cli_args.aws_profile, region_name=cli_args.aws_region)
        notification = SnsNotification(boto3.client('sns'), cli_args.phone_numbers)

    send_collection_day_notification(notification, cli_args.address)


if __name__ == '__main__':
    main()
