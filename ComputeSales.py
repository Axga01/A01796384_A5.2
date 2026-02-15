#!/usr/bin/env python3
"""
Actividad 5.2 - Programa 1: Compute sales

Lee 2 archivos JSON desde línea de comandos:
  1) priceCatalogue.json  -> catálogo de productos con precio
  2) salesRecord.json     -> registro de ventas (producto + cantidad)

Calcula el costo total de todas las ventas (sum(price(product) * quantity)),
manejando datos inválidos (muestra warnings y continúa), imprime en consola y
guarda evidencia en un archivo llamado SalesResults.txt.

Ejecución mínima (Req 5):
  python computeSales.py priceCatalogue.json salesRecord.json

Cumple PEP 8.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

RESULTS_FILENAME = "SalesResults.txt"


def fmt(number: float) -> str:
    """Format numbers without scientific notation and with up to 2 decimals."""
    # En ventas suele ser deseable 2 decimales; si te piden más, cámbialo a 8.
    return f"{number:.2f}"


def safe_load_json(path: str) -> Any:
    """Load JSON from disk with clear error messages."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: file not found -> {path}")
        raise
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path} (line {exc.lineno}, col {exc.colno})")
        raise


def build_catalogue_map(catalogue_json: Any) -> Dict[str, float]:
    """
    Build a dictionary: product_title -> price.

    Expected catalogue format (based on your TC1.ProductList.json):
      [
        {"title": "...", "price": 28.1, ...},
        ...
      ]
    """
    if not isinstance(catalogue_json, list):
        raise ValueError("Catalogue JSON must be a list of product objects.")

    catalogue: Dict[str, float] = {}
    invalid_rows = 0

    for idx, item in enumerate(catalogue_json, start=1):
        if not isinstance(item, dict):
            invalid_rows += 1
            print(f"Warning (catalogue row {idx}): not an object -> ignored")
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or title.strip() == "":
            invalid_rows += 1
            print(f"Warning (catalogue row {idx}): missing/invalid title -> ignored")
            continue

        try:
            price_value = float(price)
        except (TypeError, ValueError):
            invalid_rows += 1
            print(
                f"Warning (catalogue row {idx}): invalid price for '{title}' -> ignored"
            )
            continue

        # Si hay duplicados, nos quedamos con el último (determinista).
        catalogue[title.strip()] = price_value

    if invalid_rows > 0:
        print(f"Info: catalogue invalid rows ignored: {invalid_rows}")

    return catalogue


def extract_sales_rows(sales_json: Any) -> List[Dict[str, Any]]:
    """
    Validate that sales_json is a list of sale rows.

    Expected sales format (based on your TC1.Sales.json):
      [
        {"SALE_ID": 1, "SALE_Date": "...", "Product": "...", "Quantity": 2},
        ...
      ]
    """
    if not isinstance(sales_json, list):
        raise ValueError("Sales JSON must be a list of sale objects.")

    rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(sales_json, start=1):
        if not isinstance(item, dict):
            print(f"Warning (sales row {idx}): not an object -> ignored")
            continue
        rows.append(item)
    return rows


def compute_total(
    catalogue: Dict[str, float],
    sales_rows: List[Dict[str, Any]],
) -> Tuple[float, int, int, int]:
    """
    Compute total cost and basic counters.

    Returns:
      total_cost, processed_rows, ignored_rows, unknown_products
    """
    total = 0.0
    processed = 0
    ignored = 0
    unknown_products = 0

    for idx, row in enumerate(sales_rows, start=1):
        product = row.get("Product")
        quantity = row.get("Quantity")

        if not isinstance(product, str) or product.strip() == "":
            ignored += 1
            print(f"Warning (sales row {idx}): missing/invalid Product -> ignored")
            continue

        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            ignored += 1
            print(
                f"Warning (sales row {idx}): invalid Quantity '{quantity}' -> ignored"
            )
            continue

        if qty <= 0:
            ignored += 1
            print(f"Warning (sales row {idx}): non-positive Quantity '{qty}' -> ignored")
            continue

        product_name = product.strip()
        if product_name not in catalogue:
            unknown_products += 1
            ignored += 1
            print(
                f"Warning (sales row {idx}): product not in catalogue '{product_name}' "
                "-> ignored"
            )
            continue

        price = catalogue[product_name]
        total += price * qty
        processed += 1

    return total, processed, ignored, unknown_products


def build_output(
    catalogue_path: str,
    sales_path: str,
    total_cost: float,
    processed: int,
    ignored: int,
    unknown_products: int,
    elapsed_seconds: float,
) -> str:
    """Build human-readable output for console and file."""
    return (
        "=== SALES RESULTS ===\n"
        f"Price catalogue: {os.path.basename(catalogue_path)}\n"
        f"Sales record:    {os.path.basename(sales_path)}\n"
        "\n"
        f"Processed rows:  {processed}\n"
        f"Ignored rows:    {ignored}\n"
        f"Unknown products ignored: {unknown_products}\n"
        "\n"
        f"TOTAL COST: {fmt(total_cost)}\n"
        f"Elapsed time (s): {elapsed_seconds:.6f}\n"
    )


def append_results(output_text: str) -> None:
    """Append results to SalesResults.txt (evidence)."""
    with open(RESULTS_FILENAME, "a", encoding="utf-8") as file:
        file.write("\n===== RUN =====\n")
        file.write(output_text)


def parse_args(argv: List[str]) -> Tuple[str, str]:
    """
    Parse args in the exact minimal required format:
      python computeSales.py priceCatalogue.json salesRecord.json
    """
    if len(argv) != 3:
        print("Usage: python computeSales.py priceCatalogue.json salesRecord.json")
        raise SystemExit(2)

    return argv[1], argv[2]


def main() -> None:
    """Program entry point."""
    start = time.perf_counter()
    catalogue_path, sales_path = parse_args(sys.argv)

    try:
        catalogue_json = safe_load_json(catalogue_path)
        sales_json = safe_load_json(sales_path)
    except (FileNotFoundError, json.JSONDecodeError):
        # Errores fatales: no se puede continuar sin archivos/JSON válido.
        return

    try:
        catalogue = build_catalogue_map(catalogue_json)
        sales_rows = extract_sales_rows(sales_json)
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    total_cost, processed, ignored, unknown_products = compute_total(
        catalogue, sales_rows
    )
    elapsed = time.perf_counter() - start

    output_text = build_output(
        catalogue_path=catalogue_path,
        sales_path=sales_path,
        total_cost=total_cost,
        processed=processed,
        ignored=ignored,
        unknown_products=unknown_products,
        elapsed_seconds=elapsed,
    )

    print(output_text)
    append_results(output_text)


if __name__ == "__main__":
    main()
