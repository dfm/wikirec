#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pymysql
import argparse

parser = argparse.ArgumentParser(description="Parse the database")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
args = parser.parse_args()

blacklist = [
    "Documentary_film",
    "Television_film",
]

with pymysql.connect(user=args.user, passwd=args.password, db="wiki") as c:
    def count():
        c.execute("select count(*) from movies")
        n = int(c.fetchone()[0])
        print("Found {0} movies".format(n))

    # Set up the table.
    print("Setting up the table")
    c.execute("drop table if exists movies")
    c.execute("create table movies like page")

    # Find all the pages linked to from lists of movies.
    print("Searching lists of movies")
    c.execute("""insert ignore into movies
    select p1.* from page as p0
        join pagelinks on pl_from=p0.page_id
        join page as p1 on pl_title=p1.page_title
        where p0.page_namespace=0 and p0.page_is_redirect=0
            and p0.page_title like 'List_of_films:_%'
            and pagelinks.pl_namespace=0
            and p1.page_namespace=0 and p1.page_is_redirect=0
    """)
    count()

    print("Searching lists of movies (redirects)")
    c.execute("""insert ignore into movies
    select p2.* from page as p0
        join pagelinks on pl_from=p0.page_id
        join page as p1 on pl_title=p1.page_title
        join redirect on rd_from=p1.page_id
        join page as p2 on rd_title=p2.page_title
        where p0.page_namespace=0 and p0.page_is_redirect=0
            and p0.page_title like 'List_of_films:_%'
            and pagelinks.pl_namespace=0
            and p1.page_namespace=0 and p1.page_is_redirect=1
            and rd_namespace=0
            and p2.page_namespace=0 and p2.page_is_redirect=0
    """)
    count()

    # Search for pages ending in something like (film) or (2014 film).
    print("Searching for 'orphan' movies")
    c.execute(r"""insert ignore into movies
    select * from page where
        page_namespace=0 and page_is_redirect=0
        and page_title rlike '\\([0-9]*_*film\\)'
    """)
    count()

    print("Removing incorrect elements")
    c.execute("""
    delete from movies where
        page_title rlike '^[0-9]*_in_film.*'
        or page_title rlike '^[0-9]*_film.*'
        or page_title rlike '^List_of.*'
        or page_title like '%(disambiguation)'
        {0}
    """.format("\n".join(map("or page_title like '{0}'".format,
                             blacklist))))
    count()
