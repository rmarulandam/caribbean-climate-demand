# Reproducibility policy

Link results to exact code commit, data release/checksums, specification version,
software/environment, commands and RUN record. Record seeds and nondeterminism. External
human execution is valid; a proposed command is not a completed run. Exit zero alone
is not scientific acceptance. Preserve failures, deviations and inconvenient findings.

Authoritative numbers follow analysis → CSV/JSON/Parquet/generated LaTeX → generation
script → manuscript. Manually transcribed values are not authoritative. For unavoidable
historical print sources label transcription, cite the page, retain a second-person check
and uncertainty; do not claim independent reproduction.

Review checks provenance, output hashes, units, sample, specification and manuscript claims.
Large logs/results may be archived with hashes. Redact secrets/identifiers without hiding
method deviations. See [provenance](PROVENANCE.md) and [contributing](../CONTRIBUTING.md).
