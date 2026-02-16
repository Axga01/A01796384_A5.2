# Actividad 5.2 – Ejercicio de programación 2 y análisis estático

**Alumno:** Andrea Xcaret Gomez Alfaro || A01796384  
**Repositorio:** A01796384_A5.2  

---

## Descripción del proyecto

Este repositorio contiene la implementación del **Programa 1: Compute Sales**, desarrollado en Python conforme a las especificaciones de la Actividad 5.2.

El programa:

- Se ejecuta desde línea de comandos  
- Recibe **dos archivos JSON como parámetros**:
  - `priceCatalogue.json`: catálogo de productos con precio  
  - `salesRecord.json`: registro de ventas  
- Calcula el **costo total de ventas** usando algoritmos básicos  
- Maneja errores y datos inválidos mostrando advertencias en consola  
- Imprime resultados en pantalla  
- Genera evidencia en archivo `SalesResults.txt`  
- Incluye el tiempo de ejecución  
- Cumple estándares **PEP 8**, **flake8** y **pylint**

---

## Estructura del repositorio

```text
A01796384_A5.2
│
├── compute_sales.py
├── SalesResults.txt
├── evidencia_terminal.txt
├── priceCatalogue.json
├── salesRecord.json
├── README.md
├── .flake8
│
└── tests
    ├── TC1
    │   ├── TC1.ProductList.json
    │   └── TC1.Sales.json
    │
    ├── TC2
    │   └── TC2.Sales.json
    │
    └── TC3
        └── TC3.Sales.json
```

---

# Cómo se corrieron los requerimientos 

## 0) Preparación (clonar y entrar al repo)

```bash
git clone https://github.com/Axga01/A01796384_A5.2.git
cd A01796384_A5.2
```

---

## Req 1 — Ejecución desde línea de comandos

Se ejecuta desde terminal pasando rutas como argumentos:

```bash
python compute_sales.py priceCatalogue.json salesRecord.json
```

También se puede ejecutar directamente con los archivos de prueba:

```bash
python compute_sales.py tests/TC1/TC1.ProductList.json tests/TC1/TC1.Sales.json
```

---

## Req 2 — Cálculo del costo total

La operación calculada es:

```text
TOTAL = Σ (precio_producto × cantidad)
```

- `precio_producto` se toma del catálogo (`priceCatalogue.json`)  
- `cantidad` se toma del registro de ventas (`salesRecord.json`)  
- Se usa un `dict` (mapa título→precio) para búsquedas eficientes  

---

## Req 3 — Manejo de errores / datos inválidos 

El programa **no se detiene** por errores de datos; en su lugar:

- Reporta warnings por registros inválidos  
- Ignora filas con problemas  
- Continúa ejecución  

Ejemplos:

```text
Warning: Row #33: negative Quantity '-35' for 'Fresh blueberries' -> skipped
Warning: Row #22: product not in catalogue 'Elotes' -> skipped
```

---

## Req 4 — Nombre del programa

```text
compute_sales.py
```

---

## Req 5 — Formato mínimo de invocación requerido

Formato exigido por la actividad:

```bash
python compute_sales.py priceCatalogue.json salesRecord.json
```

### Cumplimiento con casos reales

Para mantener Req 5 y usar los TCs:

**TC1**

```bash
cp tests/TC1/TC1.ProductList.json priceCatalogue.json
cp tests/TC1/TC1.Sales.json salesRecord.json
python compute_sales.py priceCatalogue.json salesRecord.json
```

**TC2**

```bash
cp tests/TC1/TC1.ProductList.json priceCatalogue.json
cp tests/TC2/TC2.Sales.json salesRecord.json
python compute_sales.py priceCatalogue.json salesRecord.json
```

**TC3**

```bash
cp tests/TC1/TC1.ProductList.json priceCatalogue.json
cp tests/TC3/TC3.Sales.json salesRecord.json
python compute_sales.py priceCatalogue.json salesRecord.json
```

---

## Req 6 — Manejo de grandes volúmenes

- El catálogo se convierte en `dict` para lookup O(1)  
- Las ventas se recorren una sola vez  
- Funciona con cientos o miles de registros  

---

## Req 7 — Tiempo de ejecución

Cada corrida mide el tiempo con `time.perf_counter`:

```text
Elapsed time (s): 0.000306
```

Se imprime y se guarda en evidencia.

---

## Req 8 — Cumplimiento PEP8 y análisis estático

### Flake8

```bash
pip install flake8
flake8 compute_sales.py
```

Resultado:

```text
Sin errores
```

---

### Pylint

```bash
pip install pylint
pylint compute_sales.py
```

Resultado:

```text
Your code has been rated at 10.00/10
```
<img width="981" height="731" alt="Captura de pantalla 2026-02-15 181315" src="https://github.com/user-attachments/assets/2cdc7e9f-2706-4f7c-9384-f1e2c97539e6" />

---

# Casos de prueba ejecutados (TC1, TC2, TC3)

Catálogo base:

```text
tests/TC1/TC1.ProductList.json
```

---

## TC1 — Ventas válidas

```bash
python compute_sales.py tests/TC1/TC1.ProductList.json tests/TC1/TC1.Sales.json
```

Resultado:

```text
TOTAL COST: 2481.86
```

---

## TC2 — Cantidades negativas

```bash
python compute_sales.py tests/TC1/TC1.ProductList.json tests/TC2/TC2.Sales.json
```

```text
Warning: Row #33: negative Quantity '-35' -> skipped
Warning: Row #45: negative Quantity '-123' -> skipped
TOTAL COST: 169478.22
```

---

## TC3 — Productos inexistentes y datos inválidos

```bash
python compute_sales.py tests/TC1/TC1.ProductList.json tests/TC3/TC3.Sales.json
```

```text
Warning: product not in catalogue -> skipped
Warning: negative quantity -> skipped
TOTAL COST: 168145.36
```

---

# Evidencia generada

## Archivo de resultados

```text
SalesResults.txt
```

Contiene:

- Historial de ejecuciones  
- Resultados por corrida  
- Tiempo de ejecución  
- Advertencias detectadas  

---
<img width="980" height="670" alt="image" src="https://github.com/user-attachments/assets/0671e415-c36f-42c4-a378-77aaa9818820" />

## Evidencia de terminal

```text
evidencia_terminal.txt
```

Generación:

```bash
python compute_sales.py tests/TC1/... >> evidencia_terminal.txt
flake8 compute_sales.py >> evidencia_terminal.txt
pylint compute_sales.py >> evidencia_terminal.txt
```

---

