#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pymysql
import argparse

parser = argparse.ArgumentParser(description="Build the connection graph")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
args = parser.parse_args()

with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    c.execute("drop table if exists `graph`")
    c.execute("""create table `graph` (
        `g_id1` int(8) unsigned NOT NULL,
        `g_id2` int(8) unsigned NOT NULL,
        `g_distance` int(8) unsigned NOT NULL,
        `g_count` int(8) unsigned NOT NULL DEFAULT 0,
        PRIMARY KEY (`g_id1`, `g_id2`, `g_distance`)
    )""")

    print("Finding direct links")
    c.execute("""insert into graph
        (g_id1, g_id2, g_distance, g_count)
    select m1.m_id, m2.m_id, 0, count(m2.m_id)
        from movies as m1
        join pagelinks on pl_from=m1.m_id
        join page on page_title=pl_title
        join movies as m2 on m2.m_id=page_id
        where pl_namespace=0 and page_namespace=0 and page_is_redirect=0
        group by m2.m_id""")

    print("Finding indirect links")
    c.execute("""insert into graph
        (g_id1, g_id2, g_distance, g_count)
    select m1.m_id, m2.m_id, 1, count(m2.m_id)
        from movies as m1

        join pagelinks as pl1 on pl1.pl_from=m1.m_id
        join page as p1 on p1.page_title=pl1.pl_title

        join pagelinks as pl2 on pl2.pl_from=p1.page_id
        join page as p2 on p2.page_title=pl2.pl_title

        join movies as m2 on m2.m_id=p2.page_id

        where pl1.pl_namespace=0
        and p1.page_namespace=0 and p1.page_is_redirect=0

        and pl2.pl_namespace=0
        and p2.page_namespace=0 and p2.page_is_redirect=0

        group by m2.m_id""")
