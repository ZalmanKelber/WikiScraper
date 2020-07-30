from urllib.request import urlopen
import ssl
import re
import sqlite3
import time

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from bs4 import BeautifulSoup

conn = sqlite3.connect('wikidb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Articles;
DROP TABLE IF EXISTS Routes;

CREATE TABLE Articles (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    url    TEXT UNIQUE,
    title TEXT
);

CREATE TABLE Routes (
    from_id INTEGER,
    to_id INTEGER
);

''')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

default_phrase = "Qa"
phrase = input('Enter phrase: ') or default_phrase
default_starting_article = "Qatar"
starting_article = input('Enter root article: ') or default_starting_article
stack = [starting_article]
searched = dict()
duplicates = dict()

while len(stack) > 0:
    #print the number of urls the program will search in the next sequence
    print("NEXT SEQUENCE: stack length =", len(stack))
    #sort the stack so that we have a rough idea of where we are in each stack
    stack.sort()
    #create the temp stack, which is where we will put all new urls that we find
    temp_stack = list()
    for url in stack:
        #register that we've already searched this url
        searched[url] = True
        #insert the url into the database if it's not alrady there and retrieve its id
        #in the vairable from_id
        cur.execute('''INSERT OR IGNORE INTO Articles (url)
                VALUES ( ? )''', (url,) )
        cur.execute('SELECT id FROM Articles WHERE url = ? ', (url, ))
        from_id = cur.fetchone()[0]
        #open the url and parse the content
        response = urlopen("https://en.wikipedia.org/wiki/" + url, context=ctx)
        soup = BeautifulSoup(response.read(), "html.parser")
        #extract the title from the page, which we will use to
        #check for duplicates resulting from redirects
        title = soup('title')[0].getText()[:-12]
        #determine if another url already has this title
        cur.execute('SELECT id FROM Articles WHERE title = ? ', (title,))
        result = cur.fetchone()
        if result is not None:
            #if there is a duplicate, replace all references to this url with the found duplicate
            duplicate_id = result[0]
            cur.execute('UPDATE Routes SET to_id = ? WHERE to_id = ?', (duplicate_id, from_id))
            duplicates[from_id] = duplicate_id
        else:
            #otherwise add the title to the databse
            print(url)
            cur.execute('UPDATE Articles SET title = ? WHERE id = ? ', (title, from_id))
            for link in soup('a'):
                #find all links to other english language wikipedia articles
                next_url_handler = re.search("^/wiki/(" + phrase + "[^:]+$)", link.get("href", ""))
                if next_url_handler:
                    next_url = next_url_handler.group(1)
                    if next_url not in searched.keys():
                        #if the urls are new, add them to the temp_stack and into the database
                        temp_stack.append(next_url)
                        cur.execute('''INSERT OR IGNORE INTO Articles (url)
                            VALUES ( ? )''', ( next_url, ) )
                        searched[next_url] = True
                    #find the id of the url in the databse
                    cur.execute('SELECT id FROM Articles WHERE url = ? ', (next_url, ))
                    to_id = cur.fetchone()[0]
                    cur.execute('SELECT from_id FROM Routes WHERE from_id = ? AND to_id = ? ', (from_id, to_id))
                    #if the route from the current page to the new url isn't already in the databse, add it
                    #after checking for duplicates
                    if cur.fetchone() is None and from_id != to_id:
                        cur.execute('''INSERT INTO Routes (from_id, to_id)
                            VALUES ( ?, ? )''', ( from_id, to_id) )
    #the next stack will be the current temp_stack
    stack = temp_stack

#remove duplicate articles
for from_id in duplicates:
    cur.execute('UPDATE Routes SET to_id = ? WHERE to_id = ?', (duplicates[from_id], from_id))
    cur.execute('DELETE from Articles WHERE id = ?', (from_id,))
conn.commit()
conn.close()
