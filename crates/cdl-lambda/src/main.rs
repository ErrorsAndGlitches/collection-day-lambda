//! Lambda entrypoint binary.
//!
//! The binary is named `bootstrap` (see Cargo.toml `[[bin]]`) so the
//! `provided.al2023` Lambda base image can exec it directly.
//!
//! Phase 0 scaffold — the `lambda_runtime` handler and CLI land here in a
//! later phase.

fn main() {
    println!("{}", cdl_core::placeholder());
}
