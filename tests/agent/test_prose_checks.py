"""Unit-test the CJK counter + elision detector + mandated-quote extractor
used by write_beat_prose. These functions are pure, so no agent run needed."""
from crpg.agent.tools import (
    _cjk_char_count,
    _extract_mandated_quotes,
    _DIALOGUE_ELISION_MARKERS,
    _WORD_COUNT_SELF_REPORT,
)


def test_cjk_count_basic():
    assert _cjk_char_count("苏婉走进电梯") == 6


def test_cjk_count_ignores_latin_digits_punctuation():
    # Punctuation, whitespace, ASCII, digits should not count
    assert _cjk_char_count("Su Wan 按下了 23 楼") == 4  # 按 下 了 楼


def test_cjk_count_ignores_self_report_footnote():
    """This is the critical bug: agent was appending '（约2500字）' to game the count."""
    clean = "她推开门走出去。"  # 7 chars
    with_footnote = clean + "（约二千五百字，共约二百五十字符）"
    # Footnote is stripped before counting
    assert _cjk_char_count(with_footnote) == _cjk_char_count(clean)


def test_cjk_count_ignores_english_footnote_pattern():
    clean = "雨下得很密。她的鞋跟在石板上敲出两记闷响。"  # 20 chars
    with_footnote = clean + "(250 字)"
    assert _cjk_char_count(with_footnote) == _cjk_char_count(clean)


def test_cjk_count_preserves_legitimate_parentheticals():
    """Parenthetical content that isn't a word-count report should be counted."""
    text = "她沉默了（仿佛半秒）。"  # 6 CJK chars: 她 沉 默 了 仿 佛 半 秒 — actually 8
    # Should NOT strip this, it's legitimate prose (not a word-count)
    cnt = _cjk_char_count(text)
    assert cnt == 8, f"expected 8 (她沉默了仿佛半秒), got {cnt}"


def test_self_report_regex_matches_common_forms():
    assert _WORD_COUNT_SELF_REPORT.search("（约二千五百字）")
    assert _WORD_COUNT_SELF_REPORT.search("(2500 字)")
    assert _WORD_COUNT_SELF_REPORT.search("（共约 250 字符）")
    assert _WORD_COUNT_SELF_REPORT.search("（大约一千字）")
    # Should NOT match legitimate prose mentioning numbers + "字"
    assert not _WORD_COUNT_SELF_REPORT.search("她写了几个字")


def test_elision_markers_cover_common_patterns():
    assert "她不记得具体说了什么" in _DIALOGUE_ELISION_MARKERS
    assert "他们谈了很久" in _DIALOGUE_ELISION_MARKERS


def test_extract_mandated_quotes():
    synopsis = "Su Wan 在酒吧里对 Kai 说「你不想让我停。」然后陷入沉默。"
    quotes = _extract_mandated_quotes(synopsis)
    assert quotes == ["你不想让我停。"]


def test_extract_mandated_quotes_nested():
    synopsis = "她对自己说『其实我知道』然后对他说「走吧。」"
    quotes = _extract_mandated_quotes(synopsis)
    assert "走吧。" in quotes
    assert "其实我知道" in quotes


def test_extract_mandated_quotes_none():
    synopsis = "Su Wan 下班走出写字楼，地铁口被 Kai 搭讪。"
    assert _extract_mandated_quotes(synopsis) == []
