## Collection Day Lambda

This project provides users with a reminder the day before their collection day as well as providing information on
which type of collection will occur e.g. regular trash, compost, or recycling etc. This project uses AWS Lambda to
make a request to the [King County Collection Day Tool][].
 
The Lambda function is configured to run on a specific day at a specific time that the user configures for the
notification to be sent. This is to reduce the number of calls to the King County website as well as a cost saving
mechanism.

[King County Collection Day Tool]: https://www.seattle.gov/utilities/services/garbage/look-up-collection-day


## Running Locally

One can run the tool from the command line for testing by running:
```bash
python -m cdl [options...]
```


## Set Up

Environment variables that must be defined in the Lambda context:

* **ADDRESS**: address to look up the collection for. Only needs to be the street address i.e. no city or zip code.
* **PHONE_NUMBERS**: comma separated list of phone numbers to send the messages to. Must have the form "+10123456789"

The Lambda needs permissions to hit SNS to send the SMS messages. The role the Lambda runs under must have these
permissions.

[List of tz database time zones Wiki]: https://www.wikiwand.com/en/List_of_tz_database_time_zones


## Design Overview

> todo


## Development

> todo
