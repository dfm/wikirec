#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import sys
import pymysql
import argparse

parser = argparse.ArgumentParser(description="Find the relevant links")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
parser.add_argument("title", nargs="+", help="A movie title")
args = parser.parse_args()

title = " ".join(args.title) + "*"
q1 = "+" + " +".join(args.title) + "*"
q2 = " ".join(args.title) + "%"

with pymysql.connect(user=args.user, passwd=args.password, db="wiki",
                     charset="utf8") as c:
    c.execute("""select ms_id, ms_title, match(ms_title) against (%s) as score
    from moviesearch where match(ms_title) against (%s in boolean mode)
    or ms_title like %s
    order by score DESC, ms_len DESC
    limit 1
    """, (title, q1, q2))

    result = c.fetchone()
    if result is None:
        print("Couldn't find any results")
        sys.exit(1)

    i, t, s = result
    print("Interpreting query as: '{0}'".format(t.encode("utf-8")))

    c.execute("""
    select page_title, count(page_id) as c from movielinks
    join moviebacklinks on mbl_from=ml_to
    join movies on mbl_to=page_id
    where ml_from=%s and mbl_to!=%s
    group by page_id
    order by c desc
    limit 10
    """, (i, i))
    for doc in c.fetchall():
        print(doc)
