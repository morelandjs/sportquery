SportQuery
==========

*Data scraper for sportsreference.com affiliate sites*

Documentation
-------------

...coming soon

Quick start
-----------

Requires python3 with
  * bs4
  * numpy
  * pandas
  * prefect
  * requests
  * sqlalchemy
  * unidecode

At the time of this documentation writing, ``sportquery`` is private.
You can install it by cloning its git repository and installing from source: ::

  git clone https://github.com/morelandjs/sportquery sportquery
  cd sportquery
  pip3 install -e .

Once the package is installed, set the following environment variable to pass
your database credentials to the ``sportquery`` prefect workflow. ::

  export SPORTQUERY_DB=$YOUR_DATABASE_CONNECTION_STRING

Next, navigate to the project root directory and execute the prefect workflow. ::

  python3 -m sportquery.nba.sync_database

This will start scraping data from
`basketball-reference.com <https://www.basketball-reference.com>`_
and subsequently persist it to the ``$SPORTQUERY_DB`` database connection.

Generally speaking, you'll want to run this script on a schedule to ensure the
database is up to date.
To do this, `create a prefect account <https://universal.prefect.io/signin/register>`_
and follow the instructions for running a
`prefect flow <https://docs.prefect.io/orchestration/tutorial/first.html#creating-a-project>`_
on a schedule using the prefect cloud backend.

And that's it! The package should take care of the rest. Reference each sport's
individual documentation page for details on the available tables and the schemas for each.
