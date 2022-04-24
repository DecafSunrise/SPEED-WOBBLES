# SPEED-WOBBLES
-----
## Getting Started
- Clone this repo
- install requirements.txt (pip install requirements.txt)
- Run Data_pipeline.py
- Now you've got a database... Happy Data Sciencein'

## How does this work?
This collection of scripts looks at a **Google News RSS feed** to identify news articles of interest to you, on a given topic. Once it's found a new article, it scrapes the text to an SQLite database. The processing is idempotent, so you can run this every ~15 minutes and won't wind up with duplicate text in your database. Personally, I'm running it every 12 hours, but if you were to modify this to grab tweets you might want a lower periodicity.

## What if this can't grab a particular site's text?
Run "Manually Fix Text.ipynb", and copy/paste the article text into the ipywidget. Continue running that cell until the errors are gone!

## So what do I do with this database?
Currently, the database will consist of three tables: RSS Hits, Scrape status, and Body Text. I intend to create a "view" of cleaned metadata and body text, to permit data science and machine learning efforts.

## Planned Features/TODO
- Create a standard "view" of clean metadata and body text
- Named Entity Recognition (NER) to identify people/named entities present in the data
  - Could create a custom SpaCy NER model for this
  - Sentiment Analysis by entity ("Sent4Ent")
- Graph Analysis:
  - Which entities occur together in documents?
  - Which documents cover similar themes?
- Event Detection:
  - Can we find emerging 'events', given large drops of reporting in a small amount of time?
- Text Classification:
  - Assign classes/tags given various features of the data. Is this article about politics? Military? etc.
