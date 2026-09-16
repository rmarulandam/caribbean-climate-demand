# Contributing

Clone this repository and use scientific tools of your choice. Create a descriptive branch,
submit reviewable pull requests, and obtain human code/scientific review. No private tool
or other repository is required to understand or contribute.

Inspect `git status` first and preserve others' changes. Do not commit raw/private data,
credentials, large outputs or local paths. Reference exact data releases and RUN manifests.
Use [portable paths](config/paths.example.toml).

PRs describe objective, research task, proposal/design implication, changed code, data
release, external computations actually performed, RUN IDs, output changes, checks and
limitations. State when no computation occurred. Tests do not imply scientific approval.
Resolve scientific disagreements through [decisions](docs/DECISIONS.md) and the owner;
preserve evidence and competing positions. Resolve Git conflicts with authors; do not
silently discard work or rewrite history.

Read [gates](docs/SCIENTIFIC_GATES.md) and [reproducibility](docs/REPRODUCIBILITY_POLICY.md).
Reviewers report evidence, severity and residual risk; authors implement changes separately.
Keep primary, robustness and exploratory analyses distinguishable.
