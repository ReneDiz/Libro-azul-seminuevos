# Bitácora de cambios

Cada cambio de método, parámetro o fuente se registra aquí: fecha, qué cambió, valor anterior, valor nuevo y por qué.

## v2-prueba · 2026-11-05 (revisión 2)

- **Se quitó la sección de compra y los datos para el CR.** La página queda solo como guía de mercado; el margen se mide en el CR Sencillo V2.
- **Configuración:** se extraen cabina (dormitorio o cabina corta, y pulgadas), tracción (6x4, 6x2, 4x2) y potencia del texto de cada ficha, sin suponer lo que el anuncio no dice. Nuevos filtros de cabina y tracción, y la tabla «Qué tan parecidos son los comparables», que cuenta cuántos coinciden, cuántos difieren y cuántos no traen el dato.
- **Motor por familia:** PACCAR (MX-13), Cummins (ISX, ISX15, X15), Detroit DD13 y DD15.
- **IVA:** lo que declare el anuncio manda. Si no lo declara: particular = exento (LIVA art. 9 fr. IV; neto = publicado) y distribuidor = IVA incluido (LFPC art. 7 Bis; neto = publicado ÷ 1.16). Antes se dividía todo entre 1.16. Presunción por validar con Fiscal; la confianza sigue en «baja» cuando se usa.
- **Prueba de IVA:** regresión del precio publicado con modelo, año, km y tipo de vendedor. Al corte: distribuidores +22.3 % sobre particulares (t = 3.2), consistente con que los distribuidores publiquen con IVA incluido.
- **Colores:** paleta «marino» (azul marino sobre fondo cálido con acento dorado).

## v2-prueba · 2026-11-05

**Base y fuentes**
- Nueva base unificada `data/base.json`, generada por `homologar.py`, con una fila por anuncio y los campos del Observatorio: fuente, URL, VIN o stock, año, km, motor, transmisión, precio publicado, moneda, base de IVA, tipo de precio, fecha de consulta, estado y motivos de no elegibilidad.
- Lectura automática (`python3 -m recolectar`) de 8 fuentes: Mercado Libre, SelecTrucks Zapata, Go On Zapata, Panamotors, NASTRAC, Quality Trucks, Scania Seminuevos y Seminuevos.com.
- Se integran como captura previa los 46 registros de T680, Cascadia 2021–2025 e International LT 2021–2025 del Observatorio 1.2 (incluye Tractos) y los 97 anuncios de la versión 1 (incluye TTM y Del Norte).
- Duplicados entre portales por VIN o por la misma unidad (año + km; con km redondo, también el precio).
- Correcciones manuales en `data/correcciones.json` (heredadas de la v1: caja seca, accidentado, precio inconsistente, duplicados).

**Método (igual que el Observatorio 1.2)**
- Precio neto sin IVA: «IVA incluido» ÷ 1.16; «más IVA» tal cual; IVA desconocido: excluir o simular (por defecto se simula como incluido y la confianza baja).
- Directos: mismo año, motor y transmisión si se eligen, km ±25 %. Ajustables: ±2 años. Con 3 o más directos solo se usan directos.
- Atípicos fuera de Q1 − 1.5×IQR y Q3 + 1.5×IQR cuando hay 5 o más.
- Valor de mercado = mediana neta. Confianza insuficiente, baja, media o alta con las reglas del Observatorio, más un aviso si más de la mitad de los comparables son de un mismo vendedor.
- Se eliminó el ajuste de la v1 de +12 % por año y +18 % por distribuidor: no estaba autorizado.

**Compra y venta**
- Escenarios conservador, objetivo, máximo y optimista de la hoja Costos y márgenes: compra = V × (1 − v − m) − F + A.
- Valores iniciales: descuentos 10/6/2 %, margen 12 % objetivo y 8 % mínimo, comisiones 2 %, gastos fijos $106,000 y reserva $20,000 (caso demostrativo).
- Nuevo: escenario «venta a distribuidor», con margen para el distribuidor de 8 % (supuesto propio, por validar).
- Bloque «Datos para tu CR Sencillo V2»: B41, B8 y B38.

**Sensibilidad y rotación**
- Regresión log-lineal por modelo (año y km), con aviso cuando el efecto no es claro.
- Medianas por familia de motor, transmisión, tipo de vendedor y estado, contra la mediana del año ±1.
- Días publicados, rebajas de precio y anuncios que desaparecen entre capturas.
- Captura semanal automática con GitHub Actions (`.github/workflows/captura-semanal.yml`).
