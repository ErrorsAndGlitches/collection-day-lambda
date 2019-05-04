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


## Running on AWS

### Building the Lamba Tarball

AWS Lambda functions run on Amazon Linux. Hence, if there are any dependencies that are natively compiled e.g. **pyjq**,
then if you are installing these dependencies on a Mac and including them in the AWS Lamba Tarball, they will not work.
To create a consistent tarball, we have opted to use Docker, which will create a standard build environment. The
Dockerfile in this project builds the zip file in the image. The zip file then needs to be copied to the local host for
uploading to AWS Lambda. In the future, this will be automated and part of a **setup.py** command.

```bash
# build the Docker image
docker build -t collection-day-lambda:latest .
# create a container
container_id=$(docker create collection-day-lambda:latest)
# copy the AWS Lambda Tarball from the image
docker cp ${container_id}:/opt/lambda-archive-collection-day-lambda.zip .
# delete the container
docker rm ${container_id}
```

### Configuring the Lambda Function

Environment variables that must be defined in the Lambda context:

* **ADDRESS**: address to look up the collection for. Only needs to be the street address i.e. no city or zip code.
* **PHONE_NUMBERS**: comma separated list of phone numbers to send the messages to. Must have the form "+10123456789"

The Lambda needs permissions to hit SNS to send the SMS messages. The role the Lambda runs under must have these
permissions.

After creating the AWS Lambda function, configure it and upload the tarball via the following:

```bash
# update the function configuration
aws lambda update-function-configuration \
  --function-name 'collection-day-lambda' \
  --handler cdl.cdl.collection_day_lambda_handler \
  --environment Variables='{ADDRESS=987 Made Up Address St,PHONE_NUMBERS="+12223334444,+15556667777"}' \
  --runtime 'python3.7' \
  --timeout 1
# upload the build Lambda tarball
aws lambda update-function-code \
  --function-name 'collection-day-lambda' \
  --zip-file fileb://lambda-archive-collection-day-lambda.zip
```

As a final step, you can use CloudWatch to generate events to trigger the Lambda at a weekly interval.


## Design Overview

> todo


## Development

> todo
