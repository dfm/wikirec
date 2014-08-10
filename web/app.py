#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import os
import pymysql

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.escape import json_encode
from tornado.options import define, options, parse_command_line

import ui_methods

define("port", default=3047, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("xheaders", default=True, help="use X-headers")

define("mysql_user", default=None, help="MySQL username")
define("mysql_pass", default=None, help="MySQL password")
define("mysql_db", default="wiki", help="MySQL database name")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/complete", CompleteHandler),
            (r"/search", SearchHandler),
            (r"/movie/([0-9]+)", RelatedHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            xheaders=options.xheaders,
            cookie_secret="Zuper",
            debug=options.debug,
        )
        super(Application, self).__init__(handlers, ui_methods=ui_methods,
                                          **settings)

        self._db = pymysql.connect(user=options.mysql_user,
                                   passwd=options.mysql_pass,
                                   db=options.mysql_db,
                                   charset="utf8")

    @property
    def db(self):
        # Make sure that the connection is still alive.
        self._db.ping(reconnect=True)
        return self._db


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


class SearchHandler(APIHandler):

    def get(self):
        # Build the database query from the request parameter.
        q = self.get_argument("q", None)
        if q is None:
            self.redirect("/")
            return

        # First search for exact matches.
        with self.db as c:
            c.execute("""select ms_id from moviesearch where ms_title like %s
                         limit 1""",
                      (q, ))
            movie = c.fetchone()

        # Search for matches.
        if movie is None:
            movie = self.get_movies(q, 1)
            if not len(movie):
                self.render("list.html", movie=None, message="No matches.")
            movie = movie[0]

        self.redirect("/movie/{0}".format(movie[0]))


class RelatedHandler(BaseHandler):

    def get(self, movie_id):
        # Find related movies.
        with self.db as c:
            c.execute("select page_title from movies where page_id=%s",
                      (movie_id, ))
            movie = c.fetchone()
            if movie is None:
                self.render("list.html", movie=None, message="No matches.")
                return
            movie = movie[0]

            c.execute("""
            select page_id, page_title, count(page_id) as c from movielinks
                join moviebacklinks on mbl_from=ml_to
                join movies on mbl_to=page_id
                where ml_from=%s and mbl_to!=%s
                group by page_id
                order by c desc
                limit 10
            """, (movie_id, movie_id))
            movies = c.fetchall()

        # Fail if nothing was found.
        if not len(movies):
            self.render("list.html", movie=movie, movies=[])

        # Format the list correctly.
        keys = ["id", "title", "score"]
        movies = [dict(zip(keys, m)) for m in movies]

        self.render("list.html", movie=movie, movies=movies)


def main():
    parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
