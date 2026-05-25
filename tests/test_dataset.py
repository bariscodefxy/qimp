from qimp.data import validate_example, to_chat_messages
from qimp.prompts import QIMP_SYSTEM_PROMPT


def test_validate_example_ok() -> None:
    raw = {"instruction": "i", "response": "r", "risk_level": "low", "tags": ["linux"]}
    ex = validate_example(raw)
    assert ex.instruction == "i"
    assert ex.response == "r"


def test_validate_example_bad_risk() -> None:
    raw = {"instruction": "i", "response": "r", "risk_level": "bad"}
    try:
        validate_example(raw)
        assert False, "expected ValueError"
    except ValueError:
        assert True


def test_chat_messages_shape() -> None:
    ex = validate_example({"instruction": "i", "response": "r"})
    msgs = to_chat_messages(ex, QIMP_SYSTEM_PROMPT)
    assert [m["role"] for m in msgs] == ["system", "user", "assistant"]
