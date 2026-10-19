# Build the Rust Lambda as a container image for the AWS Lambda custom runtime.
#
# Built for arm64 (Lambda `architecture: arm64`). CodeBuild must run this on an
# ARM compute image so the compile targets aarch64 natively — no emulation.

# ---- build stage ----
FROM public.ecr.aws/docker/library/rust:1-bookworm AS build

WORKDIR /app

# Cache dependencies: copy manifests first, then the real sources.
COPY Cargo.toml Cargo.lock ./
COPY crates/cdl-core/Cargo.toml crates/cdl-core/Cargo.toml
COPY crates/cdl-lambda/Cargo.toml crates/cdl-lambda/Cargo.toml
COPY crates crates

RUN cargo build --release --bin bootstrap

# ---- runtime stage ----
FROM public.ecr.aws/lambda/provided:al2023

# The provided runtime execs ${LAMBDA_RUNTIME_DIR}/bootstrap.
COPY --from=build /app/target/release/bootstrap ${LAMBDA_RUNTIME_DIR}/bootstrap

CMD [ "bootstrap" ]
