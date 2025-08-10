
from agent.security import sanitize_topic

def test_sanitize_removes_dangerous_chars_and_controls():
    raw = """<<bad>\n$topic\t`rm -rf`"""
    s = sanitize_topic(raw)
    assert "<" not in s and ">" not in s and "`" not in s and "$" not in s
    assert "\n" not in s and "\t" not in s
    assert "bad" in s and "rm -rf" in s

def test_sanitize_truncates_long_input():
    raw = "a" * 300
    s = sanitize_topic(raw)
    assert len(s) == 200
