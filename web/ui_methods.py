import re
_title_re_1 = re.compile(r"\(film\)$")
_title_re_2 = re.compile(r"\wfilm\)$")


def format_title(self, s):
    s = _title_re_1.sub("", s)
    s = _title_re_2.sub(")", s)
    return s.replace("_", " ")
