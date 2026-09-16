# Next research task: source audit and harmonization

Status: PROPOSED plan; not an issued HREQ, performed audit or approved dataset.

Objective: establish whether a defensible subscriber–billing-cycle panel can be built
before selecting an estimation window or modeling electricity outcomes.

Inventory SUI TC1/1732, TC2/1743 and historical reporting formats; record access, source
versions, rights and checksums. Audit NIU/provider key stability, duplicate periods,
residential classification, billing start/end and days, readings, units, missingness,
stratum consistency, DANE geography, provider changes and privacy constraints. Produce
coverage/attrition tables by source regime, municipality and period without selecting
samples based on estimated weather effects.

For ERA5-Land audit time zone and daylight convention, temperature/dew-point units,
radiation accumulation, missing hours, grid assignment and aggregation to billing periods.
Do not fabricate household coordinates or treat coarse weather as precise household exposure.

Deliver source inventory, proposed dictionary, harmonization crosswalk, exception report,
coverage tables and candidate inclusion rules. Human decisions: access authorization,
acceptable linkage/coverage, geographic scope and viable period. Prepare exact code/commands
and a pinned commit before issuing a real HREQ. Acceptance criterion: reviewers can trace
all inclusion rules and transformations without fitting an outcome-selected primary model.
