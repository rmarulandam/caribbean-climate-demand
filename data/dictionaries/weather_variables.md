# Diccionario de Variables Climáticas (ERA5-Land Reanalysis)

Este documento detalla las variables climáticas horarias derivadas del reanálisis **ERA5-Land** del Centro Europeo de Previsiones Meteorológicas a Plazo Medio (ECMWF / Copernicus Climate Change Service) para el dominio espacial del Caribe colombiano.

---

## 1. Variables Físicas Base

| Variable | Nombre ERA5-Land | Unidades Crudas | Unidades Objetivo | Conversión / Fórmula |
| :--- | :--- | :--- | :--- | :--- |
| **Temperatura a 2m** | `t2m` | Kelvin ($K$) | Grados Celsius ($^\circ\text{C}$) | $T(^\circ\text{C}) = \text{t2m} - 273.15$ |
| **Punto de Rocío a 2m** | `d2m` | Kelvin ($K$) | Grados Celsius ($^\circ\text{C}$) | $T_{\text{dew}}(^\circ\text{C}) = \text{d2m} - 273.15$ |
| **Radiación Solar Descendente** | `ssrd` | Joules por metro cuadrado ($J/\text{m}^2$) | Vatios por metro cuadrado ($W/\text{m}^2$) | $R = \frac{\text{ssrd}}{3600\text{ s}}$ |
| **Precipitación Total** | `tp` | Metros ($m$) | Milímetros ($mm$) | $P = \text{tp} \times 1000$ |

---

## 2. Variables Biometeorológicas Derivadas

### A. Humedad Relativa ($RH$, \%)
Calculada a partir de la temperatura del aire ($T$) y del punto de rocío ($T_{\text{dew}}$) mediante la aproximación de Magnus-Tetens para presiones de vapor de saturación:

$$RH = 100 \times \frac{\exp\left(\frac{17.27 \times T_{\text{dew}}}{237.7 + T_{\text{dew}}}\right)}{\exp\left(\frac{17.27 \times T}{237.7 + T}\right)}$$

### B. Índice de Calor / Sensación Térmica (*Heat Index* - $HI$, $^\circ\text{C}$)
En el Caribe tropical, la humedad relativa elevada inhibe la evaporación del sudor, multiplicando la necesidad de refrigeración (aire acondicionado y ventiladores).
Se implementa el polinomio de regresión múltiple de Rothfusz (utilizado por la Administración Nacional Oceánica y Atmosférica de EE. UU. - NOAA):

$$HI = c_1 + c_2 T + c_3 RH + c_4 T \cdot RH + c_5 T^2 + c_6 RH^2 + c_7 T^2 \cdot RH + c_8 T \cdot RH^2 + c_9 T^2 \cdot RH^2$$

---

## 3. Agregación Temporal al Ciclo de Facturación del Suscriptor

Dado que cada suscriptor $i$ tiene un ciclo de facturación propio delimitado por $[t_{\text{ini}}, t_{\text{fin}}] = [\text{\texttt{FCH\_LECTURA\_ANT}}_i, \text{\texttt{FCH\_LECTURA\_ACT}}_i]$ con duración de $D_i$ días:

1. **Grados-Día de Enfriamiento (Cooling Degree Days - CDD):**
   $$\text{CDD}_i = \sum_{d \in [t_{\text{ini}}, t_{\text{fin}}]} \max(0, T_{\text{mean}, d} - T_{\text{base}}), \quad T_{\text{base}} = 24^\circ\text{C}$$
2. **Bins de Exposición No Lineal:** Conteo de horas totales durante el ciclo en que la temperatura (o índice de calor) estuvo en intervalos discretos:
   * Horas en $[24^\circ\text{C}, 26^\circ\text{C})$
   * Horas en $[26^\circ\text{C}, 28^\circ\text{C})$
   * Horas en $[28^\circ\text{C}, 30^\circ\text{C})$
   * Horas en $[30^\circ\text{C}, 32^\circ\text{C})$
   * Horas en $\ge 32^\circ\text{C}$
