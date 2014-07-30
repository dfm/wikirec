#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import sys
import pymysql
import argparse

parser = argparse.ArgumentParser(description="Find similar movies")
parser.add_argument("title", nargs="+", help="A movie title")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
args = parser.parse_args()
title_query = " ".join(args.title)

with pymysql.connect(user=args.user, passwd=args.password, db="wiki",
                     charset="utf8") as c:
    # Search the database for relevant movies.
    q = """select m_id, m_title, match(m_title) against (%s) as score
           from movies
           where match(m_title) against (%s)
           limit 10"""
    c.execute(q, (title_query, title_query))
    results = c.fetchall()

    # Were any results found?
    if results is None:
        print("Couldn't find any movies matching title '{0}'"
              .format(title_query))
        sys.exit(1)
    results = list(results)
    m_id, m_title, score = results[0]
    print("Interpreting query as: '{0}'".format(m_title.encode("utf-8")))

    # Find the related movies.
    c.execute("""
    select m_title, count(m_id) as links
    from pagelinks as pl1
    join page as pa1 on pa1.page_title=pl1.pl_title
    join pagelinks as pl2 on pa1.page_id=pl2.pl_from
    join page as pa2 on pa2.page_title=pl2.pl_title
    join movies on m_id=pa2.page_id
    where pl1.pl_namespace=0 and pl1.pl_from=%s
      and pa1.page_namespace=0
      and pl2.pl_namespace=0
      and pa2.page_namespace=0
      and pa2.page_id!=%s
    group by m_id
    order by links DESC, m_counter DESC
    limit 10
    """, (m_id, m_id))

    print("Similar films:")
    for _ in c.fetchall():
        print("\t({1}) {0}".format(*_))
