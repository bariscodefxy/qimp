from qimp.prompts import QIMP_SYSTEM_PROMPT, build_user_prompt


def test_system_prompt_contains_safety_contract() -> None:
    lower = QIMP_SYSTEM_PROMPT.lower()
    assert "distribution-aware" in lower
    assert "read-only diagnostics" in lower
    assert "high-risk" in lower


def test_build_user_prompt() -> None:
    prompt = build_user_prompt("Check ssh", context="sshd fails", distro="ubuntu")
    assert "Check ssh" in prompt
    assert "Distribution: ubuntu" in prompt
    assert "Context: sshd fails" in prompt
