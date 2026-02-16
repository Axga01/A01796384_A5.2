#!/usr/bin/env python3
"""
Actividad 5.2 - Programa 1: Compute sales

Invocación mínima (Req 5):
    python computeSales.py priceCatalogue.json salesRecord.json

- priceCatalogue.json: catálogo con precios
  (lista de objetos con al menos: title, price)
- salesRecord.json: registro de ventas
  (lista de objetos con al menos: Product, Quantity)

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
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

RESULTS_FILENAME = "SalesResults.txt"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SCRIPT_DIR, RESULTS_FILENAME)


@dataclass(frozen=True)
class Totals:
    """Aggregated totals and counters."""
    total: float
    processed: int
    ignored: int
    unknown: int


@dataclass(frozen=True)
class RunInfo:
    """All info needed to build the final output."""
    catalogue_path: str
    sales_path: str
    totals: Totals
    elapsed_seconds: float
    warnings: List[str]


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


def parse_args(argv: List[str]) -> Tuple[str, str]:
    """Parse args exactly as required by Req 5."""
    if len(argv) != 3:
        raise ValueError(
            "Usage: python computeSales.py priceCatalogue.json salesRecord.json"
        )
    return argv[1], argv[2]


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
        errors.append(
            f"Invalid JSON in {path}: line {exc.lineno}, col {exc.colno}"
        )
    return None, errors


def build_price_map(catalogue: Any) -> Tuple[Dict[str, float], List[str]]:
    """Build a map: title -> price."""
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
            errors.append(
                f"Catalogue row #{idx}: missing/invalid title -> ignored"
            )
            continue

        try:
            price_value = float(price)
        except (TypeError, ValueError):
            errors.append(
                f"Catalogue row #{idx}: invalid price for '{title}' -> ignored"
            )
            continue

        price_map[title.strip()] = price_value

    if not price_map:
        errors.append("No valid products found in catalogue.")
    return price_map, errors


def normalize_sales_record(sales: Any) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Ensure sales is a list of dict rows."""
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


def _validate_row(
    idx: int,
    row: Dict[str, Any],
    price_map: Dict[str, float],
) -> Tuple[str, int, str]:
    """
    Validate a sales row and return (product_key, qty, warning_message).

    If warning_message != "", caller should skip the row.
    """
    product = row.get("Product")
    quantity = row.get("Quantity")

    if not isinstance(product, str) or not product.strip():
        return "", 0, f"Row #{idx}: missing/invalid Product -> skipped"

    try:
        qty = int(quantity)
    except (TypeError, ValueError):
        warning = (
            f"Row #{idx}: invalid Quantity '{quantity}' for '{product}' -> skipped"
        )
        return "", 0, warning

    if qty <= 0:
        warning = (
            f"Row #{idx}: non-positive Quantity '{qty}' for '{product}' -> skipped"
        )
        return "", 0, warning

    key = product.strip()
    if key not in price_map:
        warning = f"Row #{idx}: product not in catalogue '{key}' -> skipped"
        return "", 0, warning

    return key, qty, ""


def compute_total(
    price_map: Dict[str, float],
    sales_rows: List[Dict[str, Any]],
) -> Tuple[Totals, List[str]]:
    """Compute total cost and counters; returns (Totals, warnings)."""
    total = 0.0
    processed = 0
    ignored = 0
    unknown = 0
    warnings: List[str] = []

    for idx, row in enumerate(sales_rows, start=1):
        key, qty, warning = _validate_row(idx, row, price_map)
        if warning:
            ignored += 1
            if "not in catalogue" in warning:
                unknown += 1
            warnings.append(warning)
            continue

        total += price_map[key] * qty
        processed += 1

    totals = Totals(
        total=total,
        processed=processed,
        ignored=ignored,
        unknown=unknown,
    )
    return totals, warnings


def build_output(info: RunInfo) -> str:
    """Build a human-readable output string."""
    lines: List[str] = []
    lines.append("=== SALES RESULTS ===")
    lines.append(f"Price catalogue: {os.path.basename(info.catalogue_path)}")
    lines.append(f"Sales record:    {os.path.basename(info.sales_path)}")
    lines.append("")
    lines.append(f"Processed rows:  {info.totals.processed}")
    lines.append(f"Ignored rows:    {info.totals.ignored}")
    lines.append(f"Unknown products ignored: {info.totals.unknown}")
    lines.append("")
    lines.append(f"TOTAL COST: {fmt(info.totals.total)}")
    lines.append(f"Elapsed time (s): {info.elapsed_seconds:.6f}")

    if info.warnings:
        lines.append("")
        lines.append("Warnings:")
        for w in info.warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)


def _emit(out: str, warnings: List[str]) -> None:
    """Print and persist output and warnings."""
    print(out)
    append_results(out)
    for w in warnings:
        warn(w)


def _run_compute(
    catalogue_path: str,
    sales_path: str,
    start_time: float,
) -> RunInfo:
    """Run full pipeline and return RunInfo for output."""
    cat_data, cat_errors = load_json(catalogue_path)
    sales_data, sales_errors = load_json(sales_path)
    warnings: List[str] = cat_errors + sales_errors

    if cat_data is None or sales_data is None:
        elapsed = time.perf_counter() - start_time
        totals = Totals(total=0.0, processed=0, ignored=0, unknown=0)
        return RunInfo(
            catalogue_path=catalogue_path,
            sales_path=sales_path,
            totals=totals,
            elapsed_seconds=elapsed,
            warnings=warnings,
        )

    price_map, map_errors = build_price_map(cat_data)
    sales_rows, rows_errors = normalize_sales_record(sales_data)
    warnings.extend(map_errors)
    warnings.extend(rows_errors)

    totals, compute_warnings = compute_total(price_map, sales_rows)
    warnings.extend(compute_warnings)

    elapsed = time.perf_counter() - start_time
    return RunInfo(
        catalogue_path=catalogue_path,
        sales_path=sales_path,
        totals=totals,
        elapsed_seconds=elapsed,
        warnings=warnings,
    )


def main(argv: List[str]) -> int:
    """Program entry point."""
    start = time.perf_counter()

    try:
        catalogue_path, sales_path = parse_args(argv)
    except ValueError as exc:
        elapsed = time.perf_counter() - start
        out = f"Error: {exc}\nElapsed time (s): {elapsed:.6f}\n"
        _emit(out, [])
        return 2

    info = _run_compute(catalogue_path, sales_path, start)
    out = build_output(info)
    _emit(out, info.warnings)

    if "File not found:" in "\n".join(info.warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
