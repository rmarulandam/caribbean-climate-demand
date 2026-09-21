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
descriptor carrying immutable URI/hash/access information, or Git LFS tracked relative paths
(e.g., under `data/intermediate/` or `data/releases/`). `log_archive` is a local
relative file or an immutable HTTPS archive URL, always accompanied by `log_sha256`.
Use ISO timestamps with UTC offsets. Before release, runs must pin a clean code commit,
match the HREQ and record `review_status: accepted` plus owner acceptance evidence.
A scientific deviation requires a revised reviewed request and a newly pinned execution.

---

## 2021–2024 SUI & Weather Pipeline Sequence Examples

To facilitate assignment across the 3 research team members, standardized human execution requests (HREQs) correspond to the sequential processing stages:

### Stage 1: Raw Ingestion & Integrity Check (Colaborador 1)
* **Request Reference:** `collaborator_requests/HREQ-0001.yml`
* **Objective:** Synchronize and verify raw CREG 015/2018 SUI archives (TC1 1732, TC2 1743) and ERA5-Land NetCDF downloads against `data/manifests/sui_2021_2024_manifest.json` and `data/manifests/era5_land_manifest.json`.
* **Execution Command:** `python src/data/01_sync_from_drive.py`
* **Expected Output:** Raw archives populated in local raw store (`data/raw/sui/`, `data/raw/era5/`), confirmed with matching SHA-256 hashes.

### Stage 2: Caribbean Microdata Extraction & Filtering (Colaborador 1)
* **Request Reference:** `collaborator_requests/HREQ-0002.yml`
* **Objective:** Stream multi-gigabyte national SUI archives to isolate Caribbean regional operators (Afinia / CaribeMar and Air-e).
* **Execution Command:** `python src/data/02_filter_caribe_sui.py`
* **Expected Outputs (Google Drive `03_intermediate/` & `data/intermediate/`):**
  - `sui_caribe_tc1_raw.parquet`
  - `sui_caribe_tc2_raw.parquet`
* **Validation Checks:** Zero records outside Caribbean department codes (`08, 13, 20, 23, 44, 47, 70`) or non-target companies.

### Stage 3: Econometric Quality Depuration (Colaborador 2 & 3)
* **Request Reference:** `collaborator_requests/HREQ-0003.yml`
* **Objective:** Enforce quality standards on subscriber billing cycles and technical attributes.
* **Execution Command:** `python src/data/03_clean_sui.py`
* **Filtering Criteria:**
  - `TIPO_LECTURA == 'REAL'` (eliminate estimated/proxy readings).
  - Billing cycle duration `CAR_T1743_DIAS_FACTURADOS` $\in [25, 35]$ days.
  - Positive consumption $> 0$ kWh and residential strata ($1$ to $6$).
  - Daily normalized consumption calculation: $Y_{it} = \text{CONS\_USUARIO}_{it} / \text{DIAS\_FACTURADOS}_{it}$.
* **Expected Outputs (Google Drive `03_intermediate/` & `data/intermediate/`):**
  - `sui_caribe_tc1_clean.parquet`
  - `sui_caribe_tc2_clean.parquet`

### Stage 4: Climate Exposure & Spatial Aggregation (Colaborador 2 & 3)
* **Request Reference:** `collaborator_requests/HREQ-0004.yml`
* **Objective:** Intersect hourly ERA5-Land climate reanalysis with DANE municipality polygons (`data/spatial/mgn_caribe_municipios.gpkg`) and aggregate exposure over each subscriber's exact billing window (`FCH_LECTURA_ANT` to `FCH_LECTURA_ACT`).
* **Execution Command:** `python src/data/04_aggregate_weather.py`
* **Expected Outputs (Google Drive `03_intermediate/` & `data/intermediate/`):**
  - `weather_billing_exposure.parquet` (containing CDD base 24°C, temperature bins, and NOAA Heat Index).

### Stage 5: Tariff Deflation & Price Integration (Colaborador 1 & 2)
* **Request Reference:** `collaborator_requests/HREQ-0005.yml`
* **Objective:** Merge official monthly CREG unit costs ($CU_{v,m}$) from `data/tariffs/CREG_CU_Tarifas_2021_2024.xlsx` and deflate using DANE IPC series (`data/tariffs/dane_ipc_2021_2024.csv`).
* **Execution Command:** `python src/data/05_merge_tariffs.py`
* **Expected Outputs (Google Drive `03_intermediate/` & `data/intermediate/`):**
  - `tariffs_deflated_clean.parquet`

### Stage 6: Master Estimation Panel Release (Gate E2 Data Approval)
* **Request Reference:** `collaborator_requests/HREQ-0006.yml`
* **Objective:** Join cleaned SUI microdata, billing-cycle climate exposure, and deflated CREG tariffs into the final regression-ready panel.
* **Execution Command:** `python src/data/06_build_release_panel.py`
* **Expected Release Output (`data/releases/` via Git LFS):**
  - `panel_caribe_2021_2024_v1.parquet`
* **Gate Decision:** Formal review by `econ-data-auditor` and human project owner sign-off using `collaboration/templates/gate-decision.yml` for **Gate E2 Data Release Approval**.
