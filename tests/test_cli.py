from click.testing import CliRunner
from nmtc_screener.cli import main


def _run(args=None, input_text=None):
    runner = CliRunner()
    return runner.invoke(main, args or [], input=input_text, catch_exceptions=False, mix_stderr=False)


class TestCLIFlags:
    def test_all_flags_produces_output(self):
        result = _run([
            "--project-name", "Detroit Fab",
            "--location", "Detroit, MI",
            "--total-cost", "12000000",
            "--project-type", "manufacturing",
            "--annual-revenue", "2000000",
            "--lic-status", "yes",
        ])
        assert result.exit_code == 0
        assert "NMTC" in result.output
        assert "Detroit Fab" in result.output

    def test_high_likelihood_shown_in_output(self):
        result = _run([
            "--project-name", "City Clinic",
            "--location", "Cleveland, OH",
            "--total-cost", "20000000",
            "--project-type", "healthcare",
            "--annual-revenue", "4000000",
            "--lic-status", "yes",
        ])
        assert result.exit_code == 0
        assert "HIGH" in result.output

    def test_low_likelihood_office_non_lic(self):
        result = _run([
            "--project-name", "Suburban Office",
            "--location", "Scottsdale, AZ",
            "--total-cost", "6000000",
            "--project-type", "office",
            "--annual-revenue", "300000",
            "--lic-status", "no",
        ])
        assert result.exit_code == 0
        assert "LOW" in result.output

    def test_capital_stack_section_present(self):
        result = _run([
            "--project-name", "Green School",
            "--location", "Newark, NJ",
            "--total-cost", "9000000",
            "--project-type", "education",
            "--annual-revenue", "1500000",
            "--lic-status", "yes",
        ])
        assert result.exit_code == 0
        assert "CAPITAL STACK" in result.output

    def test_net_subsidy_section_present(self):
        result = _run([
            "--project-name", "Market Fresh",
            "--location", "Kansas City, MO",
            "--total-cost", "7000000",
            "--project-type", "retail",
            "--annual-revenue", "900000",
            "--lic-status", "unknown",
        ])
        assert result.exit_code == 0
        assert "NET SUBSIDY" in result.output

    def test_plain_english_summary_present(self):
        result = _run([
            "--project-name", "Riverside Hub",
            "--location", "St. Louis, MO",
            "--total-cost", "11000000",
            "--project-type", "community",
            "--annual-revenue", "2000000",
            "--lic-status", "yes",
        ])
        assert result.exit_code == 0
        assert "PLAIN-ENGLISH SUMMARY" in result.output


class TestCLIInteractive:
    def test_interactive_prompts_complete(self):
        inputs = "\n".join([
            "Eastside Factory",
            "Gary, IN",
            "14000000",
            "1",          # manufacturing
            "2500000",
            "1",          # LIC yes
        ])
        result = _run(input_text=inputs)
        assert result.exit_code == 0
        assert "Eastside Factory" in result.output
