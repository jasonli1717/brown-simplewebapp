from Bio import Entrez
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import urllib
import calendar

#classes correspond to SQL tables

class Entry:
    def __init__(self, pmid=None, title=None, date=0, author_list=[]):
        # defaults to blanks
        self.pmid = pmid
        self.title = title
        self.date = date
        self.author_list = author_list

    def displayAuthorList(self):
        al=self.author_list
        for a in al:
            a.displayFullName()
            print (a.authid)

class Date:
    # default date is 0/0/1900
    def __init__(self, year=1900, month=0, day=0):
        self.year=year
        self.month=month
        self.day=day

    def displayWholeDate(datestr):
        #print(str(self.year) + '-' + str(self.month).zfill(2) + '-' + str(self.day).zfill(2))
        print datestr

    # function to 1) put date in the correct ISO 8601 format (YYYY-MM-DD)
    # 2) to fill in a SQL-valid date in the cases where a day and/or month are missing (defaults to 1900-01-01)
    def getFormatDate(self):
        if self.month == 0:
            # datestr=str(self.year)
            datestr = (str(self.year) + '-01-01')
        elif self.day == 0:
            # datestr=str(self.year) + '-' + str(self.month).zfill(2)
            datestr = (str(self.year) + '-' + str(self.month).zfill(2) + '-01')
        else:
            datestr = str(self.year) + '-' + str(self.month).zfill(2) + '-' + str(self.day).zfill(2)

        return datestr


class Author:
    def __init__(self, lastname=None, firstname=None, authid=None):
        self.lastname = lastname
        self.firstname = firstname
        self.authid = authid

    def displayFullName(self):
        print (self.firstname + ' ' + self.lastname)

    def getFullName(self):

        return (self.firstname + ' ' + self.lastname)

class AuthorArticle:
    def __init__(self, authid=None, pmid=None, order=None):
        self.authid=authid
        self.pmid=pmid
        self.order=order

#performs the Entrez Esearch
def search(query):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed',
                            retmax='50000', #50000
                            retmode='xml',
                            datetype='pdat',
                            mindate='2000',
                            maxdate='2014',
                            term=query)
    results = Entrez.read(handle)
    return results

#performs Entrez Efetch
def fetchDetails(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    #handle = Entrez.efetch(db="pubmed",retmode='xml',id=ids)
    params = {
        'db': 'pubmed',
        'retmode': 'xml',
        'retmax':'5000',
        'id': ids
    }
    #print (handle.readline().strip())
    #data=Entrez.read(handle)
    #handle.close()
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urllib.urlencode(params)
    data = urllib.urlopen(url).read()
    return data

def checkXML(XML, path):
    if XML.find(path) is not None:
        if XML.find(path).text is not None:
            return XML.find(path).text
        else:
            return ""
    else:
        return ""

#function to convert month words and abbreviations (e.g. "November" or "Dec")
# into numerical values ("November" --> 11)
def monthToNum(mo):
    mtnDict=dict((v,k) for k,v in enumerate(calendar.month_abbr))
    month_num=mtnDict[mo]
    return month_num

def digestAuthors(authors):
    author_list = []
    for i, author in enumerate(authors):
        author_obj = Author(checkXML(author, "./LastName"), checkXML(author, "./ForeName"))

        author_list.append(author_obj)
        # author_list.append(checkXML(author, "./ForeName") + " " + checkXML(author, "./LastName"))

    return author_list

def digestDate(XML):
    if XML.find("./Article/Journal/JournalIssue/PubDate/Year") is not None:
        yr=XML.find("./Article/Journal/JournalIssue/PubDate/Year").text
        new_date=Date(int(yr))
        if XML.find("./Article/Journal/JournalIssue/PubDate/Month") is not None:
            mo=XML.find("./Article/Journal/JournalIssue/PubDate/Month").text
            if not mo.isdigit():
                new_date.month=monthToNum(mo)
            else:
                new_date.month=int(mo)
            if XML.find("./Article/Journal/JournalIssue/PubDate/Day") is not None:
                dd=XML.find("./Article/Journal/JournalIssue/PubDate/Day").text
                new_date.day=int(dd)
    else:
        new_date=Date()
    return new_date

#function that takes the XML in data and
#creates a list of Entry objects
def extractEntry(data):
    #root = data.getroot()
    root = ET.fromstring(data)

    articles = root.findall("./PubmedArticle/MedlineCitation")

    papers = []
    junction_table = []
    name_list=[]
    for article in articles:
        paper = Entry()
        paper.pmid=int(article.find("./PMID").text)
        paper.title = article.find("./Article/ArticleTitle").text
        paper.author_list = digestAuthors(article.findall("./Article/AuthorList/Author"))

        #for author in paper.author_list:
        #    if author.getFullName() in name_list:
        #        author.authid = name_list.index(author.getFullName())+1
        #    else:
        #        author.authid = len(name_list)+1
        #        name_list.append(author.getFullName())
            #new_junct_entry = AuthorArticle(author.authid, paper.pmid, i)
            #junction_table.append(new_junct_entry)

        paper.date = digestDate(article)
        papers.append(paper)

    return papers