# Human scientific gates

| Gate | Packet and owner decision | Status flag |
|---|---|---|
| E1 Design | Question, estimand, population, period, exposure definitions and identification threats | design_freeze |
| E2 Data release | Source access, cleaning, geography, missingness, linkage and sample audit with checksums | approval recorded for the exact data release |
| E3 Primary specification | FE, exposure representation, inference/clustering, heterogeneity, primary and principal robustness specifications | analysis_freeze |
| E4 Interpretation | Findings, causal language, limitations, manuscript and claim provenance | interpretation_freeze |

All gates are pending. Only the owner may approve. E1/E3/E4 freeze scientific items;
E2 approves a dataset and must not be conflated with an analysis freeze. Before E1 the
design is mutable; before E3 the primary model is mutable. Exploratory data audit and
method development can proceed labeled accordingly. Released primary results require
all four gates and separate release approval.

Prepare the [gate template](../collaboration/templates/gate-decision.yml) with evidence
and unresolved objections. Preserve the owner's actual decision in an ordinary file,
then record `human_approvals.E1` (or E2/E3/E4) with by/role/date/evidence in
[status](PROJECT_STATUS.yml). Freeze flags require corresponding evidence.
Use [decision amendments](DECISIONS.md) for UNFREEZE/reapproval; never erase prior approvals.
