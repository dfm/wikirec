
.. code-block:: bash
  
  zcat preimport.sql.gz enwiki-latest-redirect.sql.gz postimport.sql.gz | mysql -u USERNAME -p wiki
