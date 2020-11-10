from argparse import ArgumentParser
import boto3

from sbp.sbp_reserve_fitness_notifications import check_fitness_reservations_for_openings

DEFAULT_AWS_REGION = 'us-west-2'


def args():
    parser = ArgumentParser(description='Run sbp reserve fitness notifications locally')

    # required
    parser.add_argument('--date', required=True, help='Date of reservation in YYYY-MM-DD format.')
    parser.add_argument('--start-time', required=True, help='Start time in HH:MM format to search for. Inclusive.')
    parser.add_argument('--end-time', required=True, help='End time in HH:MM format to search for. Inclusive.')
    parser.add_argument('--from-email', required=True, help='Address of email sender.')
    parser.add_argument('--to-email', required=True, help='Address of email recipient.')

    # optional
    parser.add_argument('--reservation-type', required=False, default='fitness',
                        help='Reservation type. "climbing" or "fitness". Default: "fitness"')
    parser.add_argument('--aws-profile', required=False, help='AWS profile to use for credentials')
    parser.add_argument(
        '--aws-region', required=False, default=DEFAULT_AWS_REGION,
        help='AWS region to use; Default: {}'.format(DEFAULT_AWS_REGION)
    )

    return parser.parse_args()


def main():
    cli_args = args()

    boto3.setup_default_session(profile_name=cli_args.aws_profile, region_name=cli_args.aws_region)
    check_fitness_reservations_for_openings(
        cli_args.date,
        cli_args.start_time,
        cli_args.end_time,
        cli_args.from_email,
        cli_args.to_email,
        cli_args.reservation_type,
        boto3.client('ses')
    )


if __name__ == '__main__':
    main()
