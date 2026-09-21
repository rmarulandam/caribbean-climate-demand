# Diccionario de Tarifas CREG e Índices Macroeconómicos

Este documento detalla la estructura económica del Costo Unitario de Prestación del Servicio de Energía Eléctrica ($CU$) regulado por la Comisión de Regulación de Energía y Gas (CREG) en Colombia, y su aplicación en la demanda residencial del Caribe (Afinia y Air-e).

---

## 1. Componentes del Costo Unitario ($CU_{v,m,i,t}$)

Bajo la fórmula tarifaria de la Resolución CREG 119 de 2007 y CREG 015 de 2018, la tarifa monomia por kilovatio-hora se descompone aditivamente en:

$$CU_{m,t} = G_{m,t} + T_{t} + D_{n,m,t} + C_{v,m,t} + P_{n,m,t} + R_{m,t}$$

Donde:
* **$G$ (Generación):** Costo de compras de energía en contratos bilaterales y bolsa spot.
* **$T$ (Transmisión):** Cargo por uso del Sistema de Transmisión Nacional (STN).
* **$D$ (Distribución):** Remuneración de activos de las redes de media y baja tensión (STR/SDL).
* **$C$ (Comercialización):** Margen de gestión comercial, lectura, facturación y recaudo.
* **$P$ (Pérdidas Reconocidas):** Costo eficiente de pérdidas técnicas y no técnicas en redes.
* **$R$ (Restricciones):** Sobrecostos operativos del Sistema Interconectado Nacional (SIN) por redespacho y alivios.

---

## 2. Régimen de Subsidios y Contribuciones

* **Consumo de Subsistencia (CS):** En municipios ubicados por debajo de los 1,000 metros sobre el nivel del mar (clima cálido, aplicable a prácticamente todo el Caribe urbano), el límite subsidiable es de **$173\text{ kWh/mes}$**. (Por encima de $1,000\text{ msnm}$ es de $130\text{ kWh/mes}$).
* **Estratificación y Facturación Efectiva:**
  * **Estrato 1:** Subsidio legal de hasta el $60\%$ (o $50\%$) sobre el $CU$ aplicable hasta el consumo de subsistencia ($173\text{ kWh}$). El consumo excedente ($> 173\text{ kWh}$) paga la tarifa plena ($100\% \times CU$).
  * **Estrato 2:** Subsidio de hasta el $50\%$ (o $40\%$) hasta $173\text{ kWh}$; exceso a tarifa plena.
  * **Estrato 3:** Subsidio del $15\%$ hasta $173\text{ kWh}$; exceso a tarifa plena.
  * **Estrato 4:** Tarifa neutra ($100\% \times CU$, sin subsidio ni contribución).
  * **Estratos 5 y 6:** Pago de tarifa plena más una sobretasa de contribución de solidaridad del $+20\%$.

---

## 3. Deflactores Macroeconómicos

* **Índice de Precios al Consumidor (IPC DANE):** Serie mensual base 2018 para deflactar las tarifas nominales y expresar los precios en pesos colombianos constantes de diciembre de 2023.
