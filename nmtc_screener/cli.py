import sys
import click

from nmtc_screener.screener import run_screening, PROJECT_TYPES
from nmtc_screener.display import console, print_banner, print_full_report

_TYPE_CHOICES = list(PROJECT_TYPES.keys())
_TYPE_MENU = "\n".join(
    f"  [{i+1}] {v['label']}"
    for i, v in enumerate(PROJECT_TYPES.values())
)
_LIC_CHOICES = {"1": "yes", "2": "no", "3": "unknown"}


def _prompt_project_type() -> str:
    console.print(f"\n[bold]Project type:[/bold]\n{_TYPE_MENU}")
    keys = list(PROJECT_TYPES.keys())
    while True:
        raw = click.prompt("\nEnter number", default="1")
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            pass
        console.print("[red]Please enter a number between 1 and 8.[/red]")


def _prompt_lic_status() -> str:
    console.print(
        "\n[bold]Is the project located in a Low Income Community (LIC) census tract?[/bold]"
        "\n  [1] Yes\n  [2] No\n  [3] Unknown"
    )
    while True:
        raw = click.prompt("\nEnter number", default="3")
        if raw in _LIC_CHOICES:
            return _LIC_CHOICES[raw]
        console.print("[red]Please enter 1, 2, or 3.[/red]")


def _prompt_dollars(label: str, min_val: float = 0.0) -> float:
    while True:
        raw = click.prompt(label)
        clean = raw.replace("$", "").replace(",", "").replace("MM", "e6").replace("M", "e6").strip()
        try:
            val = float(clean)
            if val >= min_val:
                return val
            console.print(f"[red]Value must be at least ${min_val:,.0f}.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid dollar amount (e.g. 12000000 or 12MM).[/red]")


@click.command()
@click.option("--project-name", default=None, help="Project name")
@click.option("--location", default=None, help="Project location (city, state)")
@click.option("--total-cost", type=float, default=None, help="Total project cost in dollars")
@click.option("--project-type", type=click.Choice(_TYPE_CHOICES), default=None, help="Project type key")
@click.option("--annual-revenue", type=float, default=None, help="Annual revenue in dollars")
@click.option("--lic-status", type=click.Choice(["yes", "no", "unknown"]), default=None, help="LIC census tract status")
def main(project_name, location, total_cost, project_type, annual_revenue, lic_status):
    """NMTC Screener — New Markets Tax Credit feasibility analysis."""
    print_banner()
    console.print("[bold]Answer a few questions about your project to receive a full NMTC feasibility analysis.[/bold]\n")

    if not project_name:
        project_name = click.prompt("Project name")

    if not location:
        location = click.prompt("Project location (city, state)")

    if total_cost is None:
        total_cost = _prompt_dollars("Total project cost ($)", min_val=0)

    if project_type is None:
        project_type = _prompt_project_type()

    if annual_revenue is None:
        annual_revenue = _prompt_dollars("Estimated annual revenue ($)", min_val=0)

    if lic_status is None:
        lic_status = _prompt_lic_status()

    console.print("\n[dim]Running NMTC feasibility analysis...[/dim]\n")

    try:
        result = run_screening(
            project_name=project_name,
            location=location,
            total_project_cost=total_cost,
            project_type=project_type,
            annual_revenue=annual_revenue,
            lic_status=lic_status,
        )
    except ValueError as exc:
        console.print(f"[red]Analysis error:[/red] {exc}")
        sys.exit(1)

    print_full_report(result)
