First download the ``page``, ``pagelinks``, and ``redirects`` tables from
the `latest Wikipedia dump <http://dumps.wikimedia.org/enwiki/latest/>`_ and
save them in ``data``. Run:

.. code-block:: bash
  
  zcat preimport.sql.gz enwiki-latest-page.sql.gz postimport.sql.gz | mysql -u USERNAME -p wiki
  zcat preimport.sql.gz enwiki-latest-pagelinks.sql.gz postimport.sql.gz | mysql -u USERNAME -p wiki
  zcat preimport.sql.gz enwiki-latest-redirect.sql.gz postimport.sql.gz | mysql -u USERNAME -p wiki

This will take a *long* time. Like days.

Then, to find the movies, run:

.. code-block:: bash

  scripts/find_movies.py -u USERNAME -p PASSWORD
  
And the links:

.. code-block:: bash

  scripts/find_movielinks.py -u USERNAME -p PASSWORD
