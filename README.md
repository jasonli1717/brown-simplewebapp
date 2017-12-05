# Brown interview web app

## by Jason Li

This project was developed in Python 2.7.10, mostly in the PyCharm IDE. I budgeted 6 afternoons (12 hrs), but it ballooned into about 20 hrs because of various silly bugs and mistakes.

It should be run in two parts. 

## Part 1: Data acquisition and database building

###Data acquisition

The query script is called queryPubmed.py but does not need to be run. It is imported into the next script, populateDB.py. queryPubmed handles the EUtils tools, Esearch and Efetch, that search and fetch the XML from PubMed. 

The XML was parsed by the ElementTree package. I chose to extract the four metadata fields into objects that were defined as classes. These classes follow the form of the SQL tables that the metadata will ultimately be stored in.

* class Entry
  * **pmid** :Pubmed ID, integer.
  * **title**: article's title, string.
  * **date**: publication date, Date object. There were several dates associated with each entry; I chose the actual hardcopy journal publication date. If I had more time, I would code alternate fallbacks to get the epub date in case there was no hardcopy, etc. 

* class Date
  * **year**: integer (default 1900 if missing)
  * **month**: integer (default 0). I coded a function to convert month names and abbreviations into integer.
  * **day**: integer (default 0). Note that not all dates had a month and/or day.

* class Author
  * **lastname**: author's last name, string
  * **firstname**: author's first name, string (Forename in XML)
  * **authid**: serially generated unique key, integer.

* class AuthorArticle:
  * **authid**: same as in Author
  * **pmid**: same as in Entry
  * **order**: order of authors for each article, integer. This actually turned out to be unnecessary, as Postgres/SQL preserves the order automatically.

Some of the functions I used here were adapted from [Bill Connelly's excellent blog post](http://www.billconnelly.net/?p=44) on using Python to interact with Pubmed. 

### Building the database

The next script should be called in the terminal by typing 

`python build/populateDB.py` 

It should run automatically. I tested and debugged the code using a sample fetch of 200 entries. Retrieving all ~50,000 entries takes a while because efetch has a limit of about 200 before it balks. A solution using the Pubmed tools and parameters proved quite difficult to find, so I just did a loop and fetched 200 ids at a time. Time-consuming and not ideal, I know. Also, the function to build the author table takes a really long time too, because of the O(N^2) for loop that checks whether an author is unique and assigns a key. The long run time is why I separated out these scripts from the web app part.

If you want to skip the long process and test on a small database with 200 rows, run

`python build/populateDBtest.py` 

The database was built on the Postgres 10 SQL server. This script imports the psycopg2 module to interface Python with Postgres. I am familiar with Postgres from coursework at OHSU and MySQL from my work at Stanford. It has functions to create the database "pubmed", create three tables "articles", "authors", "article_author", then insert the data we just retrieved from Pubmed into those tables. I used the form of functions found in [this tutorial](http://www.postgresqltutorial.com/postgresql-python/) to connect to the database.

Schema of the tables:

* articles (same as Entry class)
  * **pmid** primary key
  * article_title
  * pub_date

* authors (same as Author class)
  * author_lastname
  * author_firstname
  * **author_id** primary key

* article_author (same as AuthorARticle class)
  * author_id foreign key
  * pmid foreign key
  * order

Since a particular author may have written several articles (indeed, this is the case for the epilepsy field, where a scientist may have been first author on her first publication and eventually became a last author as a PI years later), and one article can have several authors, this is known as a Many-to-Many relation. As such, as need the article_author table as a junction table so we can perform a double JOIN in the SELECT query (more on that in Part 2). In that way, we can list several authors in one row of our table (there is a fancy aggregation command in Postgres 10.0 that allows you to do that).

## Part 2: Table and visualization

The web app is a separate function, which uses the Flask (0.12.2) web framework. Flask was chosen because it is simple and fast, good for a small, simple app like this one. Run the app by making sure you are in the root directory and in the terminal, type:

`FLASK_APP=app/__init__.py flask run`

This takes you to a basic index page with two links.

### Table

It was decided to use DataTables (1.10) as front-end for the table, with server-side processing on the Flask back-end. Since we have a huge amount of data, server-side processing and harnessing the power of the database is a natural fit. As a template, I used Sergio Llana's wonderful repo on Github (https://github.com/SergioLlana/datatables-flask-serverside), changing the table schemas, the HTML, and the Javascript to fit our requirements. The main original piece here is the function to do the SELECT query on our pubmed database that pulls the data and puts it in the form of a dictionary that can be turned into a JSON for DataTAbles. The SELECT column names, FROM clause, WHERE clause, ORDER clause are hard-coded. Ideally, they should be changed to a more programmatic form.

I believe I have modified the Javascript file so that it shows 20 rows per page as default and sorts by most recent publication date, although the output seems to act up and do strange things because of caching. But at last test it was working as intended.

### Visualization

For the data visualization, it was decided to use the Bokeh (0.12.10) interactive visualization library. This was chosen because I didn't want to mess with too much Javascript. I also strongly considered D3.js and the NVD3 Python wrapper.

The visualization is a very simple bar chart. Note that this chart shows non-zero counts for 2015-2017, which I think was just because it took so long to publish those papers (I know this pain). The original query was indeed for 2000-2014. With more time, I would like to make it so you can drill down and zoom into how many articles came out each month or day, and also add a hover tooltip. 
