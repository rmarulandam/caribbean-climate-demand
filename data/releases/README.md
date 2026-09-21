# Analysis Releases (Gate E2 Data Releases)

This directory stores approved, immutable estimation datasets for econometrics estimation in accordance with the project's **Gate E2 Data Approval**.

## Tracking Rule
* Release Parquet files in this directory (`data/releases/*.parquet`) are tracked via **Git LFS**.
* Releases are strictly read-only and immutable once approved by the project owner.

## Target Releases:
* `panel_caribe_2021_2024_v1.parquet`: Regression-ready micro-panel uniting:
  - Cleaned SUI billing & subscriber attributes (`data/intermediate/`)
  - Hourly climate exposure bins and CDD (`data/intermediate/weather_billing_exposure.parquet`)
  - CREG monthly unit cost rates & DANE IPC deflators (`data/tariffs/`)

## Release Verification Checklist (Gate E2):
- [ ] Source data SHA-256 hashes recorded in `data/manifests/`
- [ ] 100% of observations derived from validated real meter readings (`TIPO_LECTURA == 'REAL'`)
- [ ] Billing cycles strictly bounded between 25 and 35 days
- [ ] Sample attrition and exclusion counts fully documented
- [ ] Explicit human data approval recorded in `docs/PROJECT_STATUS.yml`
