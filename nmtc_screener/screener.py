from dataclasses import dataclass
from typing import Optional

from nmtccalc import NMTCDeal, transaction, credits, subsidy

_DEFAULT_CREDIT_PRICE = 0.83
_DEFAULT_LEVERAGE_LOAN_RATE = 0.055
_DEFAULT_QLICI_A_RATE = 0.005
_DEFAULT_QLICI_B_RATE = 0.0
_DEFAULT_CDE_FEE_RATE = 0.025
_DEFAULT_DISCOUNT_RATE = 0.08
_MIN_VIABLE_QEI = 5_000_000

PROJECT_TYPES: dict = {
    "manufacturing": {
        "label": "Manufacturing / Industrial",
        "base_score": 25,
        "rationale": "Manufacturing creates quality jobs and is a top NMTC priority.",
    },
    "healthcare": {
        "label": "Healthcare / Medical",
        "base_score": 25,
        "rationale": "Healthcare facilities directly serve underserved LIC residents.",
    },
    "education": {
        "label": "Education / Childcare",
        "base_score": 25,
        "rationale": "Educational facilities are highly competitive NMTC candidates.",
    },
    "community": {
        "label": "Community Facility / Nonprofit",
        "base_score": 22,
        "rationale": "Community facilities are prime NMTC candidates with clear community benefit.",
    },
    "mixed_use": {
        "label": "Mixed-Use Development",
        "base_score": 15,
        "rationale": "Mixed-use can qualify but requires careful commercial vs. residential structuring.",
    },
    "retail": {
        "label": "Retail / Food Service",
        "base_score": 12,
        "rationale": "Retail qualifies if serving underserved LIC residents (e.g., grocery in food desert).",
    },
    "office": {
        "label": "Office / Professional Services",
        "base_score": 8,
        "rationale": "Office projects are less competitive unless providing significant community benefit.",
    },
    "other": {
        "label": "Other",
        "base_score": 10,
        "rationale": "Eligibility depends on specific business activities and community benefit.",
    },
}


@dataclass
class ScreeningResult:
    project_name: str
    location: str
    total_project_cost: float
    project_type: str
    annual_revenue: float
    lic_status: str

    qualification_likelihood: str
    qualification_score: int
    qualification_reasons: list

    estimated_allocation: float
    transaction_result: object
    credit_result: object
    subsidy_result: object

    plain_english_summary: str


def estimate_allocation(total_cost: float) -> float:
    """Estimate NMTC allocation (QEI) as 85% of total project cost, never exceeding project cost."""
    return total_cost * 0.85


def score_deal(
    project_type: str,
    lic_status: str,
    total_cost: float,
    annual_revenue: float,
) -> tuple:
    """Return (score 0-100, likelihood label, list of reason strings)."""
    score = 40
    reasons = []

    if lic_status == "yes":
        score += 35
        reasons.append("Project is in a confirmed Low Income Community census tract (+35 pts)")
    elif lic_status == "unknown":
        score += 10
        reasons.append("LIC status unknown — census tract eligibility must be confirmed (+10 pts)")
    else:
        score -= 20
        reasons.append("Project is NOT in a Low Income Community — NMTC eligibility severely limited (-20 pts)")

    pt = PROJECT_TYPES.get(project_type, PROJECT_TYPES["other"])
    type_score = pt["base_score"]
    score += type_score
    reasons.append(f"Project type '{pt['label']}': {pt['rationale']} (+{type_score} pts)")

    if total_cost >= 10_000_000:
        score += 10
        reasons.append("Project cost ≥$10MM — sufficient scale for NMTC transaction economics (+10 pts)")
    elif total_cost >= 5_000_000:
        score += 5
        reasons.append("Project cost ≥$5MM — meets minimum viable deal size (+5 pts)")
    else:
        score -= 15
        reasons.append("Project cost <$5MM — below typical minimum for NMTC transaction economics (-15 pts)")

    # Rough debt service coverage check: A loan ≈ 55% of QEI at 5.5%
    estimated_qei = estimate_allocation(total_cost)
    a_loan_est = estimated_qei * 0.55
    annual_ds = a_loan_est * _DEFAULT_LEVERAGE_LOAN_RATE
    if annual_revenue > 0 and annual_revenue >= annual_ds * 1.25:
        score += 5
        reasons.append(f"Revenue (${annual_revenue:,.0f}/yr) covers estimated debt service at 1.25x DSCR (+5 pts)")
    elif annual_revenue > 0:
        reasons.append(f"Revenue (${annual_revenue:,.0f}/yr) may be thin for leverage loan debt service (0 pts)")

    score = max(0, min(100, score))

    if score >= 70:
        likelihood = "HIGH"
    elif score >= 45:
        likelihood = "MEDIUM"
    else:
        likelihood = "LOW"

    return score, likelihood, reasons


def _generate_summary(
    project_name: str,
    location: str,
    total_cost: float,
    project_type: str,
    likelihood: str,
    score: int,
    qei: float,
    tx,
    sub,
) -> str:
    pt_label = PROJECT_TYPES.get(project_type, PROJECT_TYPES["other"])["label"]
    lines = [
        f"{project_name} is a {pt_label} project in {location} with a total cost of "
        f"${total_cost / 1e6:.1f}MM.",
        "",
        f"This project has a {likelihood} likelihood of qualifying for NMTC financing "
        f"(screening score: {score}/100).",
        "",
        f"The estimated NMTC allocation is ${qei / 1e6:.1f}MM, generating "
        f"${tx.total_nmtcs / 1e6:.2f}MM in federal tax credits over the 7-year compliance period.",
        "",
        f"The capital stack is funded by ${tx.investor_equity / 1e6:.2f}MM in tax credit investor equity "
        f"and a ${tx.leverage_loan / 1e6:.2f}MM leverage loan, both flowing through the NMTC fund.",
        "",
        f"The project receives an estimated net subsidy of ${sub.net_subsidy / 1e6:.2f}MM "
        f"({sub.net_subsidy_pct * 100:.1f}% of total cost) — the B Loan is typically forgiven "
        f"at the end of the compliance period, representing the real economic benefit to your project.",
        "",
        f"Effective blended cost of capital: {sub.effective_cost_of_capital * 100:.2f}% — "
        f"well below conventional market rates.",
    ]

    if likelihood == "HIGH":
        lines.append(
            "\nRecommended next step: Engage a Community Development Entity (CDE) and begin "
            "the NMTC allocation application process."
        )
    elif likelihood == "MEDIUM":
        lines.append(
            "\nRecommended next step: Confirm LIC census tract eligibility and refine community "
            "benefit narrative before approaching CDEs."
        )
    else:
        lines.append(
            "\nRecommended next step: Review NMTC eligibility requirements carefully. "
            "Alternative financing such as Historic Tax Credits or CDFI loans may be more appropriate."
        )

    return "\n".join(lines)


def run_screening(
    project_name: str,
    location: str,
    total_project_cost: float,
    project_type: str,
    annual_revenue: float,
    lic_status: str,
) -> ScreeningResult:
    """Run a full NMTC feasibility screening and return a ScreeningResult."""
    score, likelihood, reasons = score_deal(
        project_type, lic_status, total_project_cost, annual_revenue
    )

    qei = estimate_allocation(total_project_cost)

    deal = NMTCDeal(
        project_name=project_name,
        total_project_cost=total_project_cost,
        nmtc_allocation=qei,
        credit_price=_DEFAULT_CREDIT_PRICE,
        leverage_loan_rate=_DEFAULT_LEVERAGE_LOAN_RATE,
        qlici_a_loan_rate=_DEFAULT_QLICI_A_RATE,
        qlici_b_loan_rate=_DEFAULT_QLICI_B_RATE,
        cde_fee_rate=_DEFAULT_CDE_FEE_RATE,
        discount_rate=_DEFAULT_DISCOUNT_RATE,
        project_location=location,
    )

    tx = transaction.structure(deal)
    cr = credits.schedule(deal)
    sub = subsidy.analyze(deal)

    summary = _generate_summary(
        project_name, location, total_project_cost, project_type,
        likelihood, score, qei, tx, sub,
    )

    return ScreeningResult(
        project_name=project_name,
        location=location,
        total_project_cost=total_project_cost,
        project_type=project_type,
        annual_revenue=annual_revenue,
        lic_status=lic_status,
        qualification_likelihood=likelihood,
        qualification_score=score,
        qualification_reasons=reasons,
        estimated_allocation=qei,
        transaction_result=tx,
        credit_result=cr,
        subsidy_result=sub,
        plain_english_summary=summary,
    )
