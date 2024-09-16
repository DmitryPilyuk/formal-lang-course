from project.task2 import regex_to_dfa


def test_regex_to_dfa_on_empty():
    dfa = regex_to_dfa("")
    assert dfa.is_deterministic()
    assert dfa.is_empty()


def test_regex_to_dfa():
    dfa = regex_to_dfa("a*|b")
    assert dfa.is_deterministic()
    assert dfa.accepts("a")
    assert dfa.accepts("b")
    assert dfa.accepts("aaa")
    assert not dfa.accepts("bb")
