# Estimands and interpretation

Status: PROPOSED quantities and current methodological safeguards.

Let Y_i,c(w) denote kWh per valid billing day for subscriber i in cycle c under
hourly weather sequence w. A candidate estimand is the target-population average of
Y_i,c(w) - Y_i,c(w_ref), with a common period and explicit short-run institutional,
building and appliance context. This notation does not establish identification.

| Dimension | Current candidate / unresolved issue |
|---|---|
| Population | Residential subscribers in selected Caribbean municipalities; dates/coverage unset |
| Unit | Subscriber–billing cycle; geographic resolution must be defensible |
| Outcome | kWh per valid billing day; logs, zeros and duration treatment unresolved |
| Exposure | Hourly temperature, humidity metric and radiation over actual billing periods |
| Identification | Within-unit variation with fixed effects; exogeneity, overlap and measurement require review |
| Inference | Spatial/serial dependence, weather-assignment unit and cluster counts unresolved |
| Primary versus exploratory | No primary specification frozen; label pre-freeze modeling exploratory and record candidate primary/robustness families before E3 |

Observed electricity is neither thermal need, cooling load, welfare nor Bitcoin-adoption
effect. Short-run weather coefficients do not identify long-run climate adaptation.
Prediction diagnostics are not causal identification. Correlated meteorological
coefficients are not automatically independent structural channels. Project M's proposed
2016–2023 window and detailed fixed effects are not instructions binding E.
