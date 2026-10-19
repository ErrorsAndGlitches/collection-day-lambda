# Collection Day Lambda

Sends a reminder the day before a Seattle solid-waste collection, including
which services are collected (garbage, recycling, food/yard waste). An AWS
Lambda queries the [Seattle Public Utilities collection calendar][spu] on a
schedule and sends the reminder by SMS.

[spu]: https://www.seattle.gov/utilities/services/garbage/look-up-collection-day

## Layout

A Cargo workspace with two crates:

- `crates/cdl-core` — the calendar client (the requests to the utilities API,
  response parsing, and next-pickup message formatting) and the notification
  sinks (SNS and stdout).
- `crates/cdl-lambda` — the `bootstrap` binary. Runs as the Lambda handler by
  default, or as a local CLI when invoked with `--address`.

## Build and test

```bash
cargo build
cargo test
```

The integration test in `crates/cdl-core/tests` replays the JSON fixtures in
`tests/` through a mock HTTP server, so the full flow is exercised offline.

## Run locally

```bash
# Print the next pickup without sending anything.
cargo run --bin bootstrap -- --address "987 Example St" --print

# Send via SNS using a named AWS profile.
cargo run --bin bootstrap -- \
  --address "987 Example St" \
  --phone-numbers "+12223334444" "+15556667777" \
  --aws-profile my-profile
```

## Container image

The Lambda is packaged as an arm64 container image on the `provided.al2023`
base. The image is built and pushed to ECR by CI, not by hand:

```bash
docker build -t collection-day-lambda .
```

`buildspec.yml` defines the CodeBuild build that produces the image and pushes
it to ECR tagged with the commit SHA.

## Deployment

Infrastructure and deployment live in the separate
[collection-day-lambda-cdk][cdk] repository, a self-mutating CDK pipeline that
builds the image, deploys the function from ECR, grants it SNS publish
permission, and schedules it with EventBridge. The function's `ADDRESS` and
`PHONE_NUMBERS` are set there.

[cdk]: https://github.com/ErrorsAndGlitches/collection-day-lambda-cdk
