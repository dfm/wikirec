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

# with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
#     c.execute("drop table if exists `graph`")
#     c.execute("""create table `graph` (
#         `g_from` int(8) unsigned NOT NULL,
#         `g_to` int(8) unsigned NOT NULL,
#         `g_distance` int(8) unsigned NOT NULL,
#         `g_count` int(8) unsigned NOT NULL DEFAULT 0,
#         PRIMARY KEY (`g_from`, `g_to`, `g_distance`)
#     )""")

#     print("Finding direct links")
#     c.execute("""insert into graph
#         (g_from, g_to, g_distance, g_count)
#     select m1.m_id, m2.m_id, 0, count(m2.m_id)
#         from movies as m1
#         join pagelinks on pl_from=m1.m_id
#         join page on page_title=pl_title
#         join movies as m2 on m2.m_id=page_id
#         where pl_namespace=0 and page_namespace=0 and page_is_redirect=0
#         group by m1.m_id, m2.m_id""")


with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    # print("Finding indirect links (part 1)")
    # c.execute("drop table if exists `tmp`")
    # c.execute("""create table `tmp` (
    #     `t_from` int(8) unsigned NOT NULL,
    #     `t_to` int(8) unsigned NOT NULL,
    #     PRIMARY KEY (`t_from`, `t_to`)
    # )""")
    # c.execute("""insert into tmp (t_from, t_to)
    # select m_id, page_id
    #     from movies
    #     join pagelinks on pl_from=m_id
    #     join page on page_title=pl_title
    #     where pl_namespace=0 and page_namespace=0 and page_is_redirect=0
    # group by m_id, page_id""")
    # c.execute("create index t_to on tmp (t_to)")

    c.execute("select count(*) from tmp")
    total = c.fetchone()[0]
    print(total)

    c.execute("drop view if exists v_tmp")
    c.execute("create view v_tmp as select * from tmp limit 10000")
    c.execute("""
    select t_from, m_id, 1, 1
        from v_tmp
        join pagelinks on pl_from=t_to
        join page on page_title=pl_title
        join movies on m_id=page_id
        where pl_namespace=0 and page_namespace=0 and page_is_redirect=0""")
    print(len(c.fetchall()))

    # print("Finding indirect links (part 2)")
    # c.execute("""insert into graph
    #     (g_from, g_to, g_distance, g_count)
    # select t_from, m_id, 1, count(m_id)
    #     from tmp
    #     join pagelinks on pl_from=t_to
    #     join page on page_title=pl_title
    #     join movies on m_id=page_id
    #     where pl_namespace=0 and page_namespace=0 and page_is_redirect=0
    #     group by t_from, m_id""")

    # c.execute("drop table `tmp`")
