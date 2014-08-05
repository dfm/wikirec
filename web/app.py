#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import os
import pymysql

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.escape import json_encode
from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("xheaders", default=False, help="use X-headers")

define("mysql_user", default=None, help="MySQL username")
define("mysql_pass", default=None, help="MySQL password")
define("mysql_db", default="wiki", help="MySQL database name")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/complete", CompleteHandler),
            (r"/suggest", SuggestHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            xheaders=options.xheaders,
            cookie_secret="Zuper",
            debug=options.debug,
        )
        super(Application, self).__init__(handlers, **settings)

        self.db = pymysql.connect(user=options.mysql_user,
                                  passwd=options.mysql_pass,
                                  db=options.mysql_db,
                                  charset="utf8")


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db


class IndexHandler(BaseHandler):

    def get(self):
        self.render("index.html")


class APIHandler(BaseHandler):

    def get_movies(self, q, N):
        with self.db as c:
            c.execute("""
                select ms_id, ms_title, match(ms_title) against (%s) as score
                from moviesearch
                where
                match(ms_title) against (%s in boolean mode)
                or
                ms_title like %s
                order by ms_title like %s DESC, score DESC, ms_len DESC
                limit {0}
            """.format(N), (q+"*", "+"+q.replace(" ", " +")+"*",
                            "%"+q+"%", q+"%"))
            titles = c.fetchall()
        return titles


class CompleteHandler(APIHandler):

    def get(self):
        # The output of this function will always be JSON.
        self.set_header("Content-Type", "application/json")

        # Build the database query from the request parameter.
        q = self.get_argument("q", None)
        if q is None:
            self.set_status(400)
            self.write(json_encode([]))
            return

        # Run the database query.
        titles = self.get_movies(q, 5)

        # Write the output.
        results = [{"i": _[0], "t": _[1]} for _ in titles]
        self.write(json_encode(results))


class SuggestHandler(APIHandler):

    def get(self):
        # Build the database query from the request parameter.
        q = self.get_argument("q", None)
        if q is None:
            self.set_status(400)
            self.write(json_encode([]))
            return

        # Run the database query.
        movie = self.get_movies(q, 1)
        self.write(json_encode(movie))
        return

        # Run the database query.
        with self.db as c:
            c.execute("""
            select page_title, count(page_id) as c from movielinks
                join moviebacklinks on mbl_from=ml_to
                join movies on mbl_to=page_id
                where ml_from=%s and mbl_to!=%s
                group by page_id
                order by c desc
                limit 10
            """, (page_id, page_id))
            results = c.fetchall()

        self.write(json_encode(results))


def main():
    parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
