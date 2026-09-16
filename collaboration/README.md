# External human execution

This protocol works with ordinary Git and any scientific software, workstation or HPC.
A collaborator needs only this repository, authorized data and the agreed environment.

1. Prepare `collaborator_requests/HREQ-NNNN.yml` from the [request template](templates/human-execution-request.yml).
   Use a unique ID such as HREQ-0001 only when issuing a real request. Pin the exact
   commit, data release, specification, commands, expected files/checks and allowed deviations.
2. The named human records acceptance, checks access/environment, and executes externally.
   Stop and report deviations; do not silently improve or change scientific specifications.
3. Return `runs/RUN-NNNN/manifest.yml` from the [run template](templates/run-manifest.yml),
   with command.txt, environment.txt, run.log and checksums.sha256 or checksum-pinned archive
   references. Record failed runs as well. Environment exports must redact secrets/local paths.
4. An independent reviewer checks request-versus-run, commit/data/specification, timing,
   exit status, output hashes, diagnostics and deviations. Reproduce quantitative claims
   when possible; document inability, rather than asserting success.
5. The scientific owner accepts/rejects the run with a dated evidence record. Run acceptance
   is distinct from data approval, design freeze and release approval. Only accepted results
   enter a release candidate; primary designation additionally requires scientific gates.

No request has been issued and no run has occurred in this bootstrap. Templates are not runs.

## Record field conventions

RUN `environment` and `command_file` are paths relative to the RUN directory;
`output_files` lists `{path, sha256}` entries there. Large outputs may use a local archive
descriptor carrying immutable URI/hash/access information. `log_archive` is a local
relative file or an immutable HTTPS archive URL, always accompanied by `log_sha256`.
Use ISO timestamps with UTC offsets. Before release, runs must pin a clean code commit,
match the HREQ and record `review_status: accepted` plus owner acceptance evidence.
A scientific deviation requires a revised reviewed request and a newly pinned execution.
