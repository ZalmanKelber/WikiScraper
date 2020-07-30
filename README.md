This is a simple web scraper that searches and displays networks of wikipedia articles.
To run this program, download the directory and run wiki_scraper.py followed by page_ranker.py (all inputs have default options and can be skipped).
The sample data stored in wikidb.sqlite, ranks.js and routes.js will be overriden.  MAKE SURE that bs4 is set up in the parent directory of the
folder or change the path in wiki_scraper.py to access the library another way.  Once both programs have been run, open the html file in a browser.
You can view the sample data (searching wikipedia articles whose urls begin with "Griffith") [here](https://zalmankelber.github.io/WikiScraper/)

The program takes a search phrase and root article and searches wikipedia, beginning with the root article, for all articles whose urls begin with the 
search phrase.  It keeps track of how many inlinks and outlinks each article has from other articles in the database and stores them in a sqlite 
database.  A simple page-ranking algorithm is used (with user-entered number of rounds) to determine the rank of each page.  The network of articles 
is then visualized using the D3 library.
