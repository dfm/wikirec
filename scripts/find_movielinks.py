#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pymysql
import argparse

parser = argparse.ArgumentParser(description="Find the relevant links")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
args = parser.parse_args()

with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    print("Finding links")
    c.execute("drop table if exists movielinks")
    c.execute("""create table movielinks (
        ml_from int unsigned NOT NULL,
        ml_to int unsigned NOT NULL,
        primary key (ml_from, ml_to)
    )""")
    c.execute("""insert into movielinks (ml_from, ml_to)
    select m.page_id, p.page_id
    from movies as m
    join pagelinks on pl_from=m.page_id
    join page as p on pl_title=p.page_title
    where pl_namespace=0 and p.page_namespace=0 and p.page_is_redirect=0
    """)

    print("Indexing")
    c.execute("create index ml_to on movielinks(ml_to)")

with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    print("Finding backlinks")
    c.execute("drop table if exists moviebacklinks")
    c.execute("""create table moviebacklinks (
        mbl_from int unsigned NOT NULL,
        mbl_to int unsigned NOT NULL,
        primary key (mbl_from, mbl_to)
    )""")
    c.execute("""insert ignore into moviebacklinks (mbl_from, mbl_to)
    select pl_from, page_id
    from movies
    join pagelinks on pl_title=page_title
    where pl_namespace=0""")

    print("Indexing")
    c.execute("create index mbl_to on moviebacklinks(mbl_to)")
