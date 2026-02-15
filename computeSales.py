#!/usr/bin/env python3
"""
Actividad 5.2 - Programa 1: Compute sales

Invocación mínima (Req 5):
    python computeSales.py priceCatalogue.json salesRecord.json

- priceCatalogue.json: catálogo con precios (lista de objetos con al menos: title, price)
- salesRecord.json: registro de ventas (lista de objetos con al menos: Product, Quantity)

El programa:
- Calcula el costo total: sum(price(Product) * Quantity)
- Maneja datos inválidos: muestra warnings y continúa (Req 3)
- Imprime resultados y los guarda en SalesResults.txt (Req 2)
- Incluye tiempo transcurrido (Req 7)
- PEP 8 (Req 8)
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

RESULTS_FILENAME = "SalesResults.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SCRIPT_DIR, RESULTS_FILENAME)


def fmt(number: float) -> str:
    """Format numbers without scientific notation and up to 2 decimals."""
    return f"{number:.2f}"


def warn(message: str) -> None:
    """Print warning to stderr."""
    print(f"Warning: {message}", file=sys.stderr)


def append_results(text: str) -> None:
    """Append results to SalesResults.txt (evidence)."""
    with open(RESULTS_PATH, "a", encoding="utf-8") as file:
        file.write("\n===== RUN =====\n")
        file.write(text)
        file.write("\n")


def load_json(path: str) -> Tuple[Any, List[str]]:
    """Load JSON from a file. Returns (data, errors)."""
    errors: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file), errors
    except FileNotFoundError:
        errors.append(f"File not found: {path}")
    except PermissionError:
        errors.append(f"Permission denied: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path}: line {exc.lineno}, col {exc.colno}")
    return None, errors


def build_price_map(catalogue: Any) -> Tuple[Dict[str, float], List[str]]:
    """
    Build a map: title -> price.

    Expected format:
      [
        {"title": "...", "price": 28.1, ...},
        ...
      ]
    """
    if not isinstance(catalogue, list):
        return {}, ["Catalogue JSON must be a list of products."]

    errors: List[str] = []
    price_map: Dict[str, float] = {}

    for idx, item in enumerate(catalogue, start=1):
        if not isinstance(item, dict):
            errors.append(f"Catalogue row #{idx}: not an object -> ignored")
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or not title.strip():
            errors.append(f"Catalogue row #{idx}: missing/invalid title -> ignored")
            continue

        try:
            price_value = float(price)
        except (TypeError, ValueError):
            errors.append(f"Catalogue row #{idx}: invalid price for '{title}' -> ignored")
            continue

        price_map[title.strip()] = price_value

    if not price_map:
        errors.append("No valid products found in catalogue.")
    return price_map, errors


def normalize_sales_record(sales: Any) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Ensure sales is a list of dict rows.

    Expected format:
      [
        {"Product": "...", "Quantity": 2, ...},
        ...
      ]
    """
    if not isinstance(sales, list):
        return [], ["Sales JSON must be a list of sales rows."]

    errors: List[str] = []
    rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(sales, start=1):
        if not isinstance(item, dict):
            errors.append(f"Sales row #{idx}: not an object -> ignored")
            continue
        rows.append(item)

    if not rows:
        errors.append("No valid sales rows found.")
    return rows, errors


def compute_total(
    price_map: Dict[str, float],
    sales_rows: List[Dict[str, Any]],
) -> Tuple[float, int, int, int, List[str]]:
    """
    Compute total cost.

    Returns:
      total, processed_rows, ignored_rows, unknown_products, warnings
    """
    total = 0.0
    processed = 0
    ignored = 0
    unknown = 0
    warnings: List[str] = []

    for idx, row in enumerate(sales_rows, start=1):
        product = row.get("Product")
        quantity = row.get("Quantity")

        if not isinstance(product, str) or not product.strip():
            ignored += 1
            warnings.append(f"Row #{idx}: missing/invalid Product -> skipped")
            continue

        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            ignored += 1
            warnings.append(f"Row #{idx}: invalid Quantity '{quantity}' for '{product}' -> skipped")
            continue

        if qty <= 0:
            ignored += 1
            warnings.append(f"Row #{idx}: non-positive Quantity '{qty}' for '{product}' -> skipped")
            continue

        key = product.strip()
        if key not in price_map:
            ignored += 1
            unknown += 1
            warnings.append(f"Row #{idx}: product not in catalogue '{key}' -> skipped")
            continue

        total += price_map[key] * qty
        processed += 1

    return total, processed, ignored, unknown, warnings


def build_output(
    catalogue_path: str,
    sales_path: str,
    total: float,
    processed: int,
    ignored: int,
    unknown: int,
    elapsed_seconds: float,
    warnings: List[str],
) -> str:
    """Build a human-readable output string."""
    lines: List[str] = []
    lines.append("=== SALES RESULTS ===")
    lines.append(f"Price catalogue: {os.path.basename(catalogue_path)}")
    lines.append(f"Sales record:    {os.path.basename(sales_path)}")
    lines.append("")
    lines.append(f"Processed rows:  {processed}")
    lines.append(f"Ignored rows:    {ignored}")
    lines.append(f"Unknown products ignored: {unknown}")
    lines.append("")
    lines.append(f"TOTAL COST: {fmt(total)}")
    lines.append(f"Elapsed time (s): {elapsed_seconds:.6f}")

    if warnings:
        lines.append("")
        lines.append("Warnings:")
        for w in warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)


def parse_args(argv: List[str]) -> Tuple[str, str]:
    """Parse args exactly as required by Req 5."""
    if len(argv) != 3:
        raise ValueError("Usage: python computeSales.py priceCatalogue.json salesRecord.json")
    return argv[1], argv[2]


def main(argv: List[str]) -> int:
    """Program entry point."""
    start = time.perf_counter()

    try:
        catalogue_path, sales_path = parse_args(argv)
    except ValueError as exc:
        msg = str(exc)
        elapsed = time.perf_counter() - start
        out = f"Error: {msg}\nElapsed time (s): {elapsed:.6f}\n"
        print(out)
        append_results(out)
        return 2

    cat_data, cat_errors = load_json(catalogue_path)
    sales_data, sales_errors = load_json(sales_path)

    warnings: List[str] = []
    warnings.extend(cat_errors)
    warnings.extend(sales_errors)

    if cat_data is None or sales_data is None:
        elapsed = time.perf_counter() - start
        out = build_output(
            catalogue_path=catalogue_path,
            sales_path=sales_path,
            total=0.0,
            processed=0,
            ignored=0,
            unknown=0,
            elapsed_seconds=elapsed,
            warnings=warnings,
        )
        print(out)
        append_results(out)
        for w in warnings:
            warn(w)
        return 1

    price_map, map_errors = build_price_map(cat_data)
    sales_rows, rows_errors = normalize_sales_record(sales_data)
    warnings.extend(map_errors)
    warnings.extend(rows_errors)

    total, processed, ignored, unknown, compute_warnings = compute_total(price_map, sales_rows)
    warnings.extend(compute_warnings)

    elapsed = time.perf_counter() - start
    out = build_output(
        catalogue_path=catalogue_path,
        sales_path=sales_path,
        total=total,
        processed=processed,
        ignored=ignored,
        unknown=unknown,
        elapsed_seconds=elapsed,
        warnings=warnings,
    )

    print(out)
    append_results(out)

    for w in warnings:
        warn(w)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
