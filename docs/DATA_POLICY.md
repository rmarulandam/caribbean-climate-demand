# Data policy

| Zone | Contents | Control |
|---|---|---|
| 0 RAW | Original source bytes | Immutable external storage, access controlled |
| 1 INTERMEDIATE | Parsed/harmonized/transformed data | Rebuildable from code/manifests |
| 2 ANALYSIS RELEASES | Reviewed estimation datasets | Versioned/checksummed; immutable after human approval |
| 3 RESULTS | Estimates, covariance, diagnostics, figures | RUN/specification-linked; releases immutable |

Git stores dictionaries, schemas, manifests and reviewed disclosure-safe fixtures, not
raw/private/large datasets. Record source/version, retrieval date, license/access rules,
checksum, coverage, units, transformations and joins. Archive references must not contain
credentials, personal identifiers or machine paths. Never change source bytes to pass checks.

Copy [paths.example.toml](../config/paths.example.toml) to ignored `config/paths.local.toml`.
Relative paths resolve from the repository root; absolute machine paths exist only in the
ignored copy. Code accepts a config argument or documented environment override. Do not
publish private path values in run environments. Data approval and design freeze are distinct.
