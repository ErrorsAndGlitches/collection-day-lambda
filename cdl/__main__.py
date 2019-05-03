from argparse import ArgumentParser
import boto3

from cdl.cdl import send_collection_day_notification

DEFAULT_AWS_REGION = 'us-west-2'


def args():
    parser = ArgumentParser(description='Run collection handler locally')

    parser.add_argument('--aws-profile', required=True, help='AWS profile to use for credentials')
    parser.add_argument(
        '--aws-region', required=False, default=DEFAULT_AWS_REGION,
        help='AWS region to use; Default: {}'.format(DEFAULT_AWS_REGION)
    )
    parser.add_argument('--address', required=True, help='Address to look up the collection for')
    parser.add_argument('--phone-numbers', required=True, nargs='+', help='Phone numbers to send the text message to')

    return parser.parse_args()


def main():
    cli_args = args()

    boto3.setup_default_session(profile_name=cli_args.aws_profile, region_name=cli_args.aws_region)
    sns_client = boto3.client('sns')

    send_collection_day_notification(sns_client, cli_args.address, cli_args.phone_numbers)


if __name__ == '__main__':
    main()
