# Research decisions

No scientific freeze or approved result is recorded. The ACTIVE bootstrap record is
administrative only; proposal scientific commitments remain PROPOSED.

| State | Meaning |
|---|---|
| PROPOSED | Candidate awaiting evaluation |
| ACTIVE | Current working choice, not necessarily frozen |
| SUPERSEDED | Replaced; link successor and retain reasons |
| FROZEN | Explicit owner-approved scoped scientific commitment |
| REJECTED | Not retained; preserve reasons/evidence |
| EXPLORATORY | Outside the primary approved plan |

Before changing question, estimand, sample, exposure bins, clustering, primary model,
functional unit, boundary, emissions method, hypothesis, theory, publication-driven design,
or primary/robustness classification, write a plan here or link a dedicated plan.
Fields: ID, date, author, motivation, original proposal position, current rule, proposed
change, evidence, scientific consequences, affected artifacts, gate reapproval needed,
status, supersedes, human decision/evidence. Pure formatting/refactoring needs no gate.

Mirror IDs/states in [PROJECT_STATUS.yml](PROJECT_STATUS.yml). Only the owner can set a
freeze true or mark a decision FROZEN. Approval requires `by`, `role: project_owner`, ISO
`date` and repository-relative `evidence` pointing to an actual owner decision with scope
and artifact version. An agent's assertion, reviewer recommendation or silence is not approval.

To amend/unfreeze: preserve the old record and approval, document motivation, obtain an
explicit owner action, mark affected gates/releases stale, rerun/review impacted work,
and obtain reapproval before primary/downstream use. Link history in
[PROPOSAL_EVOLUTION.md](PROPOSAL_EVOLUTION.md).

## Register of Decisions

### DECISION-E-DUAL-TRACK
* **Date:** 2026-09-19
* **Author:** Research Team / Colaborador Rafael Marulanda
* **Status:** PROPOSED
* **Motivation:** Incomplete public availability of national SUI 1743/1732 batches for 2021, 2022, and 2024 on open portals, while formal petition (*derecho de petición*) is pending.
* **Original Position:** Solely estimated on CREG 015/2018 (2021–2024) with Afinia and Air-e.
* **Proposed Change:** Adopt a parallel dual strategy: (i) Track A (CREG 015/2018 / 2021–2024) maintained pending institutional response to derecho de petición; (ii) Track B (CREG 097/2008 / 2018–2020 and historical series) executed immediately using Formato 2 (SUI 439) and Formato 1 (SUI 438) for *Electricaribe*.
* **Evidence:** Direct audit of SUI Formato 2 archives (`Energia_439_M_1_2020.csv.zip`) confirming availability of `Tipo de Lectura`, `Estrato`, `Consumos`, `Dias Facturados`, and DANE geography.
* **Affected Artifacts:** `docs/plan_depuracion_sui.tex`, `data/manifests/sui_2018_2020_manifest.json`, `data/README.md`.
* **Gate Reapproval Needed:** Gate E1 (Design), Gate E2 (Data).

