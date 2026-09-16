# Econometric scientific releases

No actual release exists. `templates/` and `schemas/` are a framework, never results.
A future release directory such as `econ-vX.Y/` holds RELEASE.md, MANIFEST.yml,
estimand.md, sample.md, robustness_summary.md and disclosure-safe outputs or hash-pinned
archives. Temperature/humidity/radiation responses, joint surface, heterogeneity,
covariance, uncertainty and figures are included only when actually estimated and reviewed.
Absent outputs are declared absent; do not fabricate empty empirical artifacts.

Candidate workflow: accepted RUNs + pinned data/specification → independent reproduction,
identification and interpretation review → E1–E4 evidence → owner release decision.
Candidates cannot be used downstream. A real approved manifest follows
[release.schema.json](schemas/release.schema.json); record its ID in project status only
after approval. All artifact paths are relative to this release directory and checksummed.
For large external artifacts commit an archive descriptor with immutable URI/hash and
access instructions without secrets; archive availability still needs human verification.

The source commit identifies analysis code. The subsequent release commit contains the
manifest and approval; this avoids a self-referential Git hash. Accepted RUN records pin
the same analysis commit/data/specification. Never edit approved release bytes; correct
through a new release and documented supersession/withdrawal. Do not silently change old
locks. Authorize downstream uses narrowly; no default cooling-load/welfare/adoption claim.
