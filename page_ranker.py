import sqlite3
import json
import collections


default_file = "wikidb.sqlite"
file = input("Enter file: ") or default_file
conn = sqlite3.connect(file)
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM Articles')
num_rows = cur.fetchone()[0]

cur.executescript('''
DROP TABLE IF EXISTS Ranks;

CREATE TABLE Ranks (
	id INTEGER PRIMARY KEY,
	title TEXT NOT NULL,
	num_outlinks INTEGER,
	rank FLOAT
);

INSERT INTO ranks (id, title)
SELECT id, title FROM Articles;
''')

cur.execute('UPDATE Ranks set rank = ? WHERE rank IS NULL', (1 / num_rows,))
cur.execute('SELECT * FROM Ranks')
rows = cur.fetchall()
for row in rows:
    cur.execute('''UPDATE Ranks SET num_outlinks =
    (SELECT COUNT(from_id) FROM Routes WHERE from_id = ?)
    WHERE id = ? ''', (row[0], row[0]))


default_rounds = 10
rounds = int(input("Enter number of rounds: ") or default_rounds)
# damping_constant = input("Enter damping constant")
# if not damping_constant.isnumeric() or damping_constant <= 0 or dampign_constant > 1:
#     damping_constant = 1

for i in range(rounds):
    new_ranks = dict()
    cur.execute('SELECT * FROM Ranks')
    rows = cur.fetchall()
    for row in rows:
        page_rank = 0
        cur.execute('SELECT from_id FROM Routes WHERE to_id = ?', (row[0],))
        inlinks = cur.fetchall()
        for inlink in inlinks:
            cur.execute('SELECT num_outlinks FROM Ranks WHERE id = ?', (inlink[0],))
            divisor = cur.fetchone()[0]
            cur.execute('SELECT rank FROM Ranks WHERE id = ?', (inlink[0],))
            rank = cur.fetchone()[0]
            page_rank += rank / divisor
        new_ranks[row[0]] = round(page_rank, 7)
    for id in new_ranks:
        cur.execute('UPDATE Ranks SET Rank = ? WHERE id = ?', (new_ranks[id], id))
    print("ROUND COMPLETED")

conn.commit()

ranks = list()
routes = list()
cur.execute('''SELECT Ranks.id, Ranks.title, Ranks.rank, Articles.url
    FROM Ranks JOIN Articles ON Ranks.id = Articles.id''')
rows = cur.fetchall()
for row in rows:
    d = collections.OrderedDict()
    d["id"], d["title"], d["rank"], d["url"] = row[0], row[1], row[2], row[3]
    ranks.append(d)
with open('js/ranks.js', 'w') as outfile:
    outfile.write("ranks = ")
    json.dump(ranks, outfile)

cur.execute('SELECT from_id, to_id FROM Routes')
rows = cur.fetchall()
for row in rows:
    d = collections.OrderedDict()
    d["from_id"], d["to_id"] = row[0], row[1]
    routes.append(d)
with open('js/routes.js', 'w') as outfile:
    outfile.write("routes = ")
    json.dump(routes, outfile)

conn.close()
