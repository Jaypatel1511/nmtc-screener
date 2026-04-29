import pytest
from nmtc_screener.screener import estimate_allocation, score_deal, run_screening, _MIN_VIABLE_QEI


class TestEstimateAllocation:
    def test_large_project_returns_85_pct(self):
        assert estimate_allocation(10_000_000) == pytest.approx(8_500_000)

    def test_small_project_returns_85_pct(self):
        assert estimate_allocation(1_000_000) == pytest.approx(850_000)

    def test_five_mm_project_returns_85_pct(self):
        assert estimate_allocation(5_000_000) == pytest.approx(4_250_000)


class TestScoreDeal:
    def test_high_score_confirmed_lic_manufacturing(self):
        score, likelihood, reasons = score_deal("manufacturing", "yes", 15_000_000, 2_000_000)
        assert likelihood == "HIGH"
        assert score >= 70

    def test_low_score_office_non_lic_tiny_project(self):
        score, likelihood, reasons = score_deal("office", "no", 2_000_000, 100_000)
        assert likelihood == "LOW"
        assert score < 45

    def test_medium_score_retail_unknown_lic(self):
        # Small retail project with unknown LIC: scores MEDIUM (below $5MM penalty offsets bonuses)
        score, likelihood, reasons = score_deal("retail", "unknown", 3_000_000, 200_000)
        assert likelihood in ("MEDIUM", "LOW")

    def test_lic_no_applies_penalty(self):
        score_yes, _, _ = score_deal("community", "yes", 10_000_000, 1_000_000)
        score_no, _, _ = score_deal("community", "no", 10_000_000, 1_000_000)
        assert score_yes > score_no

    def test_reasons_list_is_populated(self):
        _, _, reasons = score_deal("healthcare", "yes", 20_000_000, 3_000_000)
        assert len(reasons) >= 3

    def test_score_clamped_between_0_and_100(self):
        score, _, _ = score_deal("manufacturing", "yes", 50_000_000, 10_000_000)
        assert 0 <= score <= 100

    def test_dscr_bonus_when_revenue_sufficient(self):
        score_rich, _, reasons_rich = score_deal("healthcare", "yes", 10_000_000, 5_000_000)
        score_poor, _, reasons_poor = score_deal("healthcare", "yes", 10_000_000, 10_000)
        assert score_rich >= score_poor


class TestRunScreening:
    def test_returns_screening_result(self):
        from nmtc_screener.screener import ScreeningResult
        result = run_screening(
            project_name="Test Clinic",
            location="Detroit, MI",
            total_project_cost=12_000_000,
            project_type="healthcare",
            annual_revenue=2_000_000,
            lic_status="yes",
        )
        assert isinstance(result, ScreeningResult)

    def test_result_fields_populated(self):
        result = run_screening(
            project_name="Greenway School",
            location="Chicago, IL",
            total_project_cost=8_000_000,
            project_type="education",
            annual_revenue=1_200_000,
            lic_status="unknown",
        )
        assert result.project_name == "Greenway School"
        assert result.estimated_allocation > 0
        assert result.transaction_result is not None
        assert result.subsidy_result is not None
        assert result.credit_result is not None
        assert result.plain_english_summary != ""

    def test_nmtc_allocation_does_not_exceed_project_cost(self):
        result = run_screening(
            project_name="Small Shop",
            location="Memphis, TN",
            total_project_cost=5_000_000,
            project_type="manufacturing",
            annual_revenue=800_000,
            lic_status="yes",
        )
        assert result.estimated_allocation <= result.total_project_cost

    def test_high_likelihood_project_has_positive_summary(self):
        result = run_screening(
            project_name="Community Health Hub",
            location="Baltimore, MD",
            total_project_cost=15_000_000,
            project_type="healthcare",
            annual_revenue=3_000_000,
            lic_status="yes",
        )
        assert result.qualification_likelihood == "HIGH"
        assert "HIGH" in result.plain_english_summary
