#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

import pymysql
import argparse

from whoosh.index import create_in
from whoosh.analysis import NgramWordAnalyzer
from whoosh.fields import Schema, TEXT, NUMERIC

parser = argparse.ArgumentParser(description="Find the relevant links")
parser.add_argument("--user", "-u", help="Your MySQL user name",
                    default="root")
parser.add_argument("--password", "-p", help="Your MySQL password")
parser.add_argument("--indexdir", "-o", help="The output directory for the "
                                             "index", default="./index")
args = parser.parse_args()

# Set up the index.
analyzer = NgramWordAnalyzer(2, 4)
schema = Schema(id=NUMERIC(stored=True), length=NUMERIC(stored=True),
                title=TEXT(analyzer=analyzer, phrase=False, stored=True))
ix = create_in(args.indexdir, schema)
writer = ix.writer()
fields = ["id", "title", "length"]

with pymysql.connect(user=args.user, passwd=args.password, db="wiki",
                     charset="utf8") as c:
    c.execute("select page_id, page_title, page_len from movies")
    for doc in c.fetchall():
        doc = doc[0], doc[1].replace("_", " ").decode("utf-8"), doc[2]
        writer.add_document(**(dict(zip(fields, doc))))
writer.commit()
