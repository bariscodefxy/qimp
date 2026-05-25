from qimp.safety import assess_commands, has_high_risk


def test_assess_high_risk_rm_rf() -> None:
    findings = assess_commands("rm -rf /tmp/foo")
    assert findings
    assert findings[0].risk in {"high", "critical"}


def test_assess_read_only_command() -> None:
    findings = assess_commands("journalctl -p err -b")
    assert findings == []


def test_has_high_risk() -> None:
    assert has_high_risk("userdel alice") is True
