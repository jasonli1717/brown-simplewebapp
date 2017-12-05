import psycopg2
from sys import stdout

import queryPubmed

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

#creates the database pubmed on the Postgres server
#After the first time this is run, it will always throw an error saying "Database pubmed already exists"
# this is normal, we don't drop the database every time
def createDB():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        # params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            host="localhost",  # localhost
            password="123"
        )

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # <-- ADD THIS LINE

        db_name = "pubmed"
        cur.execute("CREATE DATABASE %s  ;" % db_name)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

#function to create three tables on pubmed Database
#schema explained in documentation
def createTables():
    stdout.write("Creating tables...")
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        DROP TABLE IF EXISTS articles CASCADE;
        """,
        """
        DROP TABLE IF EXISTS authors CASCADE;
        """,
        """
        DROP TABLE IF EXISTS article_author CASCADE;
        """,
        """
        CREATE TABLE articles (
            pmid INTEGER PRIMARY KEY NOT NULL,
            article_title VARCHAR(1023),
            pub_date DATE
        );
        """,
        """ CREATE TABLE authors (
                author_lastname VARCHAR(255),
                author_firstname VARCHAR(255),
                author_id INTEGER PRIMARY KEY
                );
        """,
        """
        CREATE TABLE article_author (
                pmid INTEGER,
                author_id INTEGER,
                author_ordinal INTEGER,
                FOREIGN KEY (pmid)
                    REFERENCES articles (pmid)
                    ON UPDATE CASCADE ON DELETE CASCADE,

                FOREIGN KEY (author_id)
                    REFERENCES authors (author_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        );
        """
    )
    conn = None
    try:
        # read the connection parameters
        # params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(database="pubmed",
                                user="postgres",
                                host="localhost",
                                password="dbpass")
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#next 3 functions make the rows of each of the 3 SQL tables
# each row is a tuple, function returns a list of tuples
def makeEntryList(article_table_obj_list):
    entry_list = []
    for article in article_table_obj_list:
        dateobj = article.date
        datestr = dateobj.getFormatDate()
        tup = (article.pmid, article.title, datestr)
        entry_list.append(tup)

    return entry_list

#because efetch was done in chunks, the ultimate assingment of author ID (PK of Authors table)
# has to be done here. O(N^2) takes a lot of time
def makeAuthorList(article_table_obj_list):
    authortab = []
    name_list = []
    for article in article_table_obj_list:
        for auth in article.author_list:
            if auth.getFullName() not in name_list:
                #author.authid = name_list.index(author.getFullName()) + 1
                auth.authid = len(name_list) + 1
                name_list.append(auth.getFullName())
                aname = (auth.lastname, auth.firstname, auth.authid)
                authortab.append(aname)
            #already_there = [tup for tup in authortab if tup[2] == auth.authid]
            #if len(already_there) == 0:
            #    aname = (auth.lastname, auth.firstname, auth.authid)
            #    authortab.append(aname)

    return authortab

#Note: order of authors is not really necessary to store, PostgreSQL preserves the order
def makeJunctionTable(article_tab_obj_list):
    junction_table = []
    for article in article_tab_obj_list:
        authors = article.author_list
        for j, author in enumerate(authors):
            new_junct_entry = (author.authid, article.pmid, j)
            junction_table.append(new_junct_entry)

    return junction_table

#Next 3 functions do the INSERT command into our 3 database tables
def insertEntryList(entry_list):
    """ insert multiple articles into the articles table  """
    sql = "INSERT INTO articles(pmid, article_title, pub_date) VALUES "
    conn = None
    try:
        # read database configuration
        #params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(database="pubmed",
                               user="postgres",
                               host="localhost",
                               password="dbpass")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        #cur.executemany(sql,entry_list)
        args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in entry_list)
        cur.execute(sql + args_str + ';')
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insertAuthors(author_table):
    """ insert multiple authors into the authors table  """
    sql = "INSERT INTO authors(author_lastname, author_firstname, author_id) VALUES "
    conn = None
    try:
        # read database configuration
        #params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(database="pubmed",
                               user="postgres",
                               host="localhost",
                               password="dbpass")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        #cur.executemany(sql,entry_list)
        args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in author_table)
        cur.execute(sql + args_str + ";")
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insertToJunctionTable(junction_list):
    """ insert multiple rows into the article_author table  """
    sql = "INSERT INTO article_author(author_id, pmid, author_ordinal) VALUES "
    conn = None
    try:
        # read database configuration
        #params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(database="pubmed",
                               user="postgres",
                               host="localhost",
                               password="dbpass")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        #cur.executemany(sql,entry_list)
        args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in junction_list)
        cur.execute(sql + args_str + ";")
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()



if __name__ == '__main__':
    createDB()
    createTables()

    results = queryPubmed.search('epilepsy[MAJR]')
    id_list = results['IdList']
    print len(id_list)
    n = 200
    chunks = [id_list[i:i + n] for i in xrange(0, len(id_list), n)]
    stdout.write ("Fetching data...")
    stdout.flush()

    data = queryPubmed.fetchDetails(chunks[1])
    papers = queryPubmed.extractEntry(data)
    print len(papers)


    entries=makeEntryList(papers)
    authors=makeAuthorList(papers)
    junct=makeJunctionTable(papers)

    insertEntryList(entries)
    insertAuthors(authors)
    insertToJunctionTable(junct)