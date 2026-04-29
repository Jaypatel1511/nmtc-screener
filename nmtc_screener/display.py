from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

from nmtc_screener.screener import ScreeningResult, PROJECT_TYPES

console = Console()

_LIKELIHOOD_COLORS = {
    "HIGH": "bold green",
    "MEDIUM": "bold yellow",
    "LOW": "bold red",
}

_LIKELIHOOD_ICONS = {
    "HIGH": "STRONG CANDIDATE",
    "MEDIUM": "POSSIBLE CANDIDATE",
    "LOW": "UNLIKELY CANDIDATE",
}


def print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]NMTC Screener[/bold cyan]\n"
            "[dim]New Markets Tax Credit Feasibility Analysis[/dim]",
            border_style="cyan",
        )
    )
    console.print()


def print_qualification(result: ScreeningResult) -> None:
    color = _LIKELIHOOD_COLORS[result.qualification_likelihood]
    icon = _LIKELIHOOD_ICONS[result.qualification_likelihood]

    console.rule("[bold]QUALIFICATION ASSESSMENT[/bold]")
    console.print(
        f"\n  Likelihood:  [{color}]{result.qualification_likelihood} — {icon}[/{color}]"
    )
    console.print(f"  Score:       [bold]{result.qualification_score}/100[/bold]\n")

    for reason in result.qualification_reasons:
        console.print(f"  [dim]•[/dim] {reason}")

    console.print()


def print_allocation(result: ScreeningResult) -> None:
    console.rule("[bold]ESTIMATED NMTC ALLOCATION[/bold]")
    console.print(
        f"\n  QEI (NMTC Allocation):  [bold cyan]${result.estimated_allocation / 1e6:.1f}MM[/bold cyan]"
    )
    console.print(
        f"  Total Tax Credits:      [bold cyan]${result.transaction_result.total_nmtcs / 1e6:.2f}MM[/bold cyan]"
        f"  [dim](39% of QEI over 7 years)[/dim]\n"
    )


def print_capital_stack(result: ScreeningResult) -> None:
    console.rule("[bold]CAPITAL STACK BREAKDOWN[/bold]")
    tx = result.transaction_result

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Component", style="dim", min_width=30)
    table.add_column("Amount", justify="right", min_width=14)
    table.add_column("% of Project", justify="right", min_width=14)

    def pct(amt: float) -> str:
        return f"{amt / result.total_project_cost * 100:.1f}%"

    table.add_row("Total Project Cost", f"${result.total_project_cost / 1e6:.2f}MM", "100.0%")
    table.add_row("", "", "")
    table.add_row("[bold]NMTC Investment Fund (QEI)[/bold]", f"${tx.qei / 1e6:.2f}MM", pct(tx.qei))
    table.add_row("  Investor Equity", f"${tx.investor_equity / 1e6:.2f}MM", pct(tx.investor_equity))
    table.add_row("  Leverage Loan", f"${tx.leverage_loan / 1e6:.2f}MM", pct(tx.leverage_loan))
    table.add_row("", "", "")
    table.add_row("[bold]QLICI to QALICB[/bold]", f"${tx.qlici_total / 1e6:.2f}MM", pct(tx.qlici_total))
    table.add_row("  A Loan (Senior)", f"${tx.qlici_a_loan / 1e6:.2f}MM", pct(tx.qlici_a_loan))
    table.add_row("  B Loan (Subordinate)", f"${tx.qlici_b_loan / 1e6:.2f}MM", pct(tx.qlici_b_loan))
    table.add_row("  CDE Fee", f"${tx.cde_fee / 1e6:.2f}MM", pct(tx.cde_fee))
    table.add_row("", "", "")
    table.add_row("Leverage Ratio", f"{tx.leverage_ratio:.2f}x", "")
    table.add_row("NMTC Coverage", f"{tx.nmtc_coverage * 100:.1f}%", "")

    console.print(table)


def print_subsidy(result: ScreeningResult) -> None:
    console.rule("[bold]NET SUBSIDY ANALYSIS[/bold]")
    sub = result.subsidy_result

    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Item", style="dim", min_width=35)
    table.add_column("Value", justify="right", min_width=14)

    table.add_row("Net Subsidy (est. B Loan forgiven)", f"[bold green]${sub.net_subsidy / 1e6:.2f}MM[/bold green]")
    table.add_row("Net Subsidy as % of Project Cost", f"[bold green]{sub.net_subsidy_pct * 100:.1f}%[/bold green]")
    table.add_row("", "")
    table.add_row("Effective Cost of Capital (blended)", f"{sub.effective_cost_of_capital * 100:.2f}%")
    table.add_row("Est. Interest Savings over 7 Years", f"${sub.interest_savings_7yr / 1e6:.2f}MM")

    console.print(table)


def print_credit_schedule(result: ScreeningResult) -> None:
    console.rule("[bold]7-YEAR CREDIT SCHEDULE[/bold]")
    cr = result.credit_result

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Year", justify="center", min_width=6)
    table.add_column("Rate", justify="center", min_width=6)
    table.add_column("Annual Credit", justify="right", min_width=16)
    table.add_column("Cumulative", justify="right", min_width=16)

    for i, (annual, cumulative) in enumerate(
        zip(cr.annual_credits, cr.cumulative_credits), 1
    ):
        rate = "5%" if i <= 3 else "6%"
        table.add_row(
            f"Y{i}", rate,
            f"${annual:,.0f}",
            f"${cumulative:,.0f}",
        )

    table.add_row("", "", "", "")
    table.add_row(
        "[bold]Total[/bold]", "",
        f"[bold]${cr.total_nmtcs:,.0f}[/bold]",
        f"[dim]PV: ${cr.pv_credits:,.0f}[/dim]",
    )

    console.print(table)


def print_summary(result: ScreeningResult) -> None:
    console.rule("[bold]PLAIN-ENGLISH SUMMARY[/bold]")
    console.print(
        Panel(
            result.plain_english_summary,
            border_style="dim",
            padding=(1, 2),
        )
    )


def print_full_report(result: ScreeningResult) -> None:
    console.print()
    console.print(f"[bold]Project:[/bold] {result.project_name}  |  "
                  f"[bold]Location:[/bold] {result.location}")
    console.print()
    print_qualification(result)
    print_allocation(result)
    print_capital_stack(result)
    print_subsidy(result)
    print_credit_schedule(result)
    print_summary(result)
