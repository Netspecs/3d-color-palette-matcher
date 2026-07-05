"""
Filament cost estimation for the 3D Print Color Palette Matcher.

Given the color distribution of an image (each color's percentage share) and an
estimated total print weight, this module works out how many grams of each
color are needed and how much that will cost, using the per-kg price stored on
each matched filament.

The math is deliberately simple and transparent:

    grams_for_color = total_grams * (percentage / 100)
    cost_for_color  = (grams_for_color / 1000) * price_per_kg
"""

from typing import Dict, List, Optional, Tuple


def estimate_costs(
    results: List[Tuple[Dict, List[Dict]]],
    total_grams: float,
    default_price_per_kg: float = 20.0,
) -> Dict:
    """
    Estimate per-color and total filament cost for a print.

    Args:
        results: List of ``(color, matches)`` tuples as produced by the app.
            ``color`` must have a ``percentage`` key; the first entry of
            ``matches`` (the best match) supplies ``price_per_kg`` and the
            filament label used in the breakdown.
        total_grams: Estimated total filament weight for the whole print.
        default_price_per_kg: Fallback price if a color has no match.

    Returns:
        A dict with ``total_grams``, ``total_cost`` and a ``breakdown`` list.
    """
    total_grams = max(0.0, float(total_grams))
    breakdown = []
    total_cost = 0.0

    # Normalize percentages so they sum to 100 (k-means shares may drift a bit).
    pct_sum = sum(max(0.0, c.get("percentage", 0)) for c, _ in results) or 100.0

    for color, matches in results:
        pct = max(0.0, color.get("percentage", 0)) / pct_sum * 100.0
        grams = total_grams * pct / 100.0
        best = matches[0] if matches else None
        price = best.get("price_per_kg", default_price_per_kg) if best else default_price_per_kg
        label = (f"{best['brand']} {best['name']} [{best['material']}]"
                 if best else "(no match)")
        cost = grams / 1000.0 * price
        total_cost += cost
        breakdown.append({
            "hex": color.get("hex"),
            "percentage": round(pct, 1),
            "grams": round(grams, 1),
            "filament": label,
            "price_per_kg": round(price, 2),
            "cost": round(cost, 2),
        })

    return {
        "total_grams": round(total_grams, 1),
        "total_cost": round(total_cost, 2),
        "breakdown": breakdown,
    }


def format_cost_report(estimate: Dict, currency: str = "$") -> str:
    """Render a cost estimate as a human-readable multi-line string."""
    lines = [f"Estimated total: {currency}{estimate['total_cost']:.2f} "
             f"for {estimate['total_grams']:.0f} g", "-" * 44]
    for row in estimate["breakdown"]:
        lines.append(
            f"{row['hex']}  {row['percentage']:>5.1f}%  {row['grams']:>6.1f} g  "
            f"{currency}{row['cost']:>6.2f}  {row['filament']}"
        )
    return "\n".join(lines)
