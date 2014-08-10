import re
_title_re_1 = re.compile(r"\(film\)$")
_title_re_2 = re.compile(r"\wfilm\)$")

AMAZON_BASE_URL = ("http://www.amazon.com/gp/search?ie=UTF8&index=movies-tv&"
                   "keywords={0}&tag=danielfm-20")


def format_title(self, s):
    s = _title_re_1.sub("", s)
    s = _title_re_2.sub(")", s)
    return s.replace("_", " ")


def amazon_url(self, s):
    return AMAZON_BASE_URL.format(s)
