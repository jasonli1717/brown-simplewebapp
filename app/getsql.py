import psycopg2

def getSQLThing():
    """ insert multiple vendors into the vendors table  """

    conn = None
    try:
        # read database configuration
        # params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(database="pubmed",
                                user="postgres",
                                host="localhost",
                                password="dbpass")
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        # cur.executemany(sql,entry_list)
        quotestr = "string_agg(authors.author_lastname, ',') "
        select_clause = (
            'SELECT articles.pmid, article_title, EXTRACT (YEAR FROM pub_date), ' + cur.mogrify(quotestr))
        source_table = 'articles FULL JOIN article_author ON articles.pmid=article_author.pmid JOIN authors ON authors.author_id=article_author.author_id GROUP BY articles.pmid'
        source_columns = ['articles.pmid', 'article_title', 'EXTRACT (YEAR FROM pub_date)',
                          'string_agg(authors.author_lastname, ",")']

        from_clause = 'FROM %s' % source_table
        order_clause = 'ORDER BY pub_date DESC '
        limit_clause = 'LIMIT 20 '

        # sql = "INSERT INTO authors(author_lastname, author_firstname, author_id) VALUES "
        sql = ' '.join([select_clause,
                        from_clause,
                        # where_clause,
                        order_clause
                        ]) + ';'
        # args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in author_table)
        cur.execute(sql)
        things = cur.fetchall()
        thingdict = []
        for thing in things:
            d = dict([("pmid", thing[0]), ("title", thing[1]), ("year", thing[2]), ("authors", thing[3])])
            thingdict.append(d)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return thingdict