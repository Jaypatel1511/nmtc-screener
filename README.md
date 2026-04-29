# nmtc-screener

A Python CLI tool for New Markets Tax Credit (NMTC) feasibility analysis. Answer a few simple questions about your project and receive a complete NMTC screening report — including qualification likelihood, estimated allocation size, capital stack breakdown, net subsidy, and a plain-English summary.

## What is NMTC?

The New Markets Tax Credit (NMTC) Program incentivizes private investment in low-income communities by providing investors a 39% federal tax credit on Qualified Equity Investments (QEI) over 7 years. Projects receive below-market financing, often resulting in a **net subsidy of 15–25% of total project cost**.

## Installation

```bash
pip install nmtc-calc        # core calculation engine
pip install nmtc-screener    # this tool
```

Or install from source:

```bash
git clone https://github.com/Jaypatel1511/nmtc-screener
cd nmtc-screener
pip install -e ".[dev]"
```

## Usage

### Interactive mode

```bash
nmtc-screener
```

The tool will ask you:

1. **Project name**
2. **Location** (city, state)
3. **Total project cost** ($)
4. **Project type** (manufacturing, healthcare, education, etc.)
5. **Annual revenue** ($)
6. **LIC status** — is the project in a Low Income Community census tract?

### Non-interactive (all flags)

```bash
nmtc-screener \
  --project-name "Detroit Health Clinic" \
  --location "Detroit, MI" \
  --total-cost 12000000 \
  --project-type healthcare \
  --annual-revenue 2000000 \
  --lic-status yes
```

### Available project types

| Key | Label |
|-----|-------|
| `manufacturing` | Manufacturing / Industrial |
| `healthcare` | Healthcare / Medical |
| `education` | Education / Childcare |
| `community` | Community Facility / Nonprofit |
| `mixed_use` | Mixed-Use Development |
| `retail` | Retail / Food Service |
| `office` | Office / Professional Services |
| `other` | Other |

## Sample Output

```
NMTC Screener
New Markets Tax Credit Feasibility Analysis

Project: Detroit Health Clinic  |  Location: Detroit, MI

──────────────────── QUALIFICATION ASSESSMENT ─────────────────────
  Likelihood:  HIGH — STRONG CANDIDATE
  Score:       95/100

  • Project is in a confirmed Low Income Community census tract (+35 pts)
  • Project type 'Healthcare / Medical': Healthcare facilities directly serve underserved LIC residents. (+25 pts)
  • Project cost ≥$10MM — sufficient scale for NMTC transaction economics (+10 pts)
  • Revenue ($2,000,000/yr) covers estimated debt service at 1.25x DSCR (+5 pts)

──────────────────── ESTIMATED NMTC ALLOCATION ─────────────────────
  QEI (NMTC Allocation):  $10.2MM
  Total Tax Credits:       $3.98MM  (39% of QEI over 7 years)

──────────────────────── CAPITAL STACK BREAKDOWN ─────────────────────
 Component                        Amount     % of Project
 Total Project Cost              $12.00MM      100.0%
 NMTC Investment Fund (QEI)      $10.20MM       85.0%
   Investor Equity                $3.31MM       27.6%
   Leverage Loan                  $6.89MM       57.4%
 QLICI to QALICB                  $9.95MM       82.9%
   A Loan (Senior)                $6.89MM       57.4%
   B Loan (Subordinate)           $3.06MM       25.5%
   CDE Fee                        $0.26MM        2.1%

──────────────────────── NET SUBSIDY ANALYSIS ──────────────────────
 Net Subsidy (est. B Loan forgiven)       $3.06MM
 Net Subsidy as % of Project Cost           25.5%
 Effective Cost of Capital (blended)        0.27%
 Est. Interest Savings over 7 Years        $1.15MM

────────────────────── PLAIN-ENGLISH SUMMARY ───────────────────────
  Detroit Health Clinic is a Healthcare / Medical project in Detroit, MI
  with a total cost of $12.0MM. This project has a HIGH likelihood of
  qualifying for NMTC financing (screening score: 95/100)...
```

## How It Works

NMTC analysis uses industry-standard defaults:

| Parameter | Default | Notes |
|-----------|---------|-------|
| Credit price | $0.83 / $1 of credits | Current market |
| Leverage loan rate | 5.50% | Market rate proxy |
| QLICI A Loan rate | 0.50% | Below-market senior |
| QLICI B Loan rate | 0.00% | Subsidized subordinate |
| CDE fee | 2.50% of QEI | Typical range 2–3% |
| Compliance period | 7 years | Fixed per Section 45D |

The estimated NMTC allocation (QEI) is set to **85% of total project cost**, subject to a $5MM minimum viable deal floor.

Calculations are powered by the [`nmtc-calc`](https://pypi.org/project/nmtc-calc/) library.

## Running Tests

```bash
pytest
pytest --cov=nmtc_screener   # with coverage
```

## License

MIT
