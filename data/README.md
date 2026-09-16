# Data

Keep raw/private/large data outside Git. Commit only documentation, schemas, dictionaries, checksums/manifests, and explicit small disclosure-safe examples when appropriate.

See [four-zone policy](../docs/DATA_POLICY.md). `dictionaries/` holds variable
meanings; `manifests/` inventories source/checksums; `schemas/` holds validation rules;
`releases/` holds metadata only. No approved dataset is recorded. Small fixtures need a
README and disclosure review; an ignore exception is not data approval.
