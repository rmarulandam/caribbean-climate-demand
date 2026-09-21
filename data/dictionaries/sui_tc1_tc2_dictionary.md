# Diccionario de Variables SUI: TC1 y TC2 (Resolución CREG 015 de 2018)

Este documento define la estructura, codificación y reglas de validación para los formatos **TC1 (SUI 1732)** y **TC2 (SUI 1743)** de la Superintendencia de Servicios Públicos Domiciliarios (SSPD).

---

## 1. Formato TC1 (SUI 1732): Parámetros Técnicos y Ubicación

* **Granularidad:** Suscriptor / Punto de Conexión (\texttt{NIU}).
* **Delimitador estándar:** Barra vertical (\texttt{|}).

| Variable | Tipo | Descripción | Regla de Validación / Dominio |
| :--- | :--- | :--- | :--- |
| `NIU` | String (Alfanumérico) | Número de Identificación del Usuario. Llave primaria única del suscriptor. | Invariante temporal en el panel. |
| `CODIGO_CONEXION` | String | Identificador del punto de conexión a la red. | |
| `NIVEL_TENSION` | Entero (1 a 4) | Nivel de tensión del servicio. Nivel 1: baja tensión ($< 1\text{ kV}$). | Requerido $= 1$ para residencial estándar. |
| `CONEXION_RED` | String | Tipo de red (Aéreo / Subterráneo). | |
| `COMERCIALIZADOR` | String | Razón social de la empresa comercializadora. | Afinia / Air-e en la región Caribe. |
| `ID_MERCADO` | Entero | Identificador del mercado de comercialización. | |
| `COD_CIRCUITO_LINEA`| String | Código del circuito de media tensión que alimenta al usuario. | Enlace para topología espacial y GIS. |
| `COD_TRANSFORMADOR` | String | Código del transformador de distribución nivel 2/1. | Enlace micro-espacial. |
| `DANE_NIU` | String (5 u 8 dígitos) | Código DANE de localización geográfica (municipio o centro poblado). | Códigos de departamentos del Caribe: `08, 13, 20, 23, 44, 47, 70`. |
| `UBICACION` | String | Cabecera Municipal (`U`) o Rural / Rural Disperso (`R`). | Usado para heterogeneidad urbana/rural. |
| `ESTRATO_SECTOR` | Entero / String | Estratificación socioeconómica (1 a 6) o sector no residencial. | **Filtro Primario:** Residencial Estratos 1, 2, 3, 4, 5 y 6. |

---

## 2. Formato TC2 (SUI 1743): Facturación y Consumos Mensuales

* **Granularidad:** Transacción mensual de facturación por suscriptor (\texttt{NIU}).
* **Delimitador estándar:** Coma (\texttt{,}).

| Variable | Tipo | Descripción | Regla de Calidad Econométrica |
| :--- | :--- | :--- | :--- |
| `NIU` | String | Identificador del usuario. Llave de cruce con TC1. | Debe existir en TC1. |
| `ID_FACTURA` | String | Número consecutivo de la factura. | |
| `FCH_INI_PER_FACT` | Fecha (`DD-MM-YYYY`) | Fecha inicial del periodo facturado. | |
| `FCH_LECTURA_ANT` | Fecha (`DD-MM-YYYY`) | Fecha de la lectura anterior del medidor. | Inicio exacto de la ventana climática. |
| `FCH_LECTURA_ACT` | Fecha (`DD-MM-YYYY`) | Fecha de la lectura actual del medidor. | Fin exacto de la ventana climática. |
| `CAR_T1743_DIAS_FACTURADOS` | Entero | Número de días facturados en el ciclo. | **Filtro Estricto:** $\in [25, 35]$ días. Coincidente con $\Delta(\text{Lecturas}) \pm 1$. |
| `TIPO_LECTURA` | String (`REAL`, `ESTIMADA`, `PROMEDIO`, etc.) | Mecanismo de captura de la lectura del medidor. | **Filtro Mandatorio:** Mantener **únicamente** `REAL`. Descartar estimadas. |
| `CONS_USUARIO` | Numérico ($\text{kWh}$) | Consumo activo medido total del periodo facturado. | **Filtro:** $> 0$ kWh. Descartar lecturas negativas o anómalas. |
| `CONS_SUBSIST` | Numérico ($\text{kWh}$) | Consumo subsidiable facturado (hasta el límite de subsistencia). | Límite cálido: 173 kWh/mes. |
| `VAL_FACT_CU` | Numérico ($\$$) | Costo Unitario de Prestación del Servicio aplicado ($\$/\text{kWh}$). | Cruzado con resoluciones CREG. |
| `VAL_TOTAL_FACT` | Numérico ($\$$) | Valor total liquidado de la factura. | |
