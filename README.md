# SPEED-WOBBLES
### Gain rapid insight into emerging news publication on topics of your chosing!
![image](https://user-images.githubusercontent.com/36832027/164999066-211c41d7-0b58-433c-bb05-6fa299e93818.png)

-----

## Getting Started
- Clone this repo
- install requirements.txt (pip install requirements.txt)
- Run Data_pipeline.py
- Now you've got a database... Happy Data Sciencein'

![image](https://user-images.githubusercontent.com/36832027/165001835-bf57aca4-a254-4c7f-93f1-07cf0506c195.png)

## How does this work?
- This collection of scripts looks at a **Google News RSS feed** to identify news articles of interest to you, on a given topic. 
- Once it's found a new article, it scrapes the text to an SQLite database. 
  - The processing is idempotent, so you can run this every ~15 minutes and won't wind up with duplicate text in your database. Personally, I'm running it every 12 hours, but if you were to modify this to grab tweets you might want a lower periodicity.
- Once you've got the article text, the pipeline creates a "cleaned" view suitable for analysis
  - The pipeline runs SpaCy's Named Entity Recognition (NER) on all new documents, and puts those entitites in a new table

## Why Google News?
- **Work smarter, not harder:** Writing your own scraper better than google sounds really, really hard.
- **Only do what you have to:** Google Alerts lets you set up arbitrary RSS feeds, without you having to set up runners, cron jobs etc to identify content of interest.
- **Extensibility:** You can set up multiple RSS feeds for multiple topics of interest, or different angles on a single topic. With some minor refactoring, these scripts can be set to run against many different Alerts, or even your favorite site's RSS feed. Neat.

## What if this can't grab a particular site's text?
Run "Manually Fix Text.ipynb", and copy/paste the article text into the ipywidget. Continue running that cell until the errors are gone!

## What about articles published before you started scraping? (**Cold Start Problem**)
There's a table (and helper script, Manually_Add_Links.ipynb) for submitting individual URLs to "catch up" on. This injects them into a "Manually_Added_Links" table and the RSS_Hits table, gives them a UUID, and kicks off further processing.

![image](https://user-images.githubusercontent.com/36832027/164998875-3173866a-aa83-4fd3-9cf4-df83506b0774.png)

## So what do I do with this database?
The longer this thing runs and scrapes, the more data you have to suss out interesting trends and insight. By running simple keyword searches, or visualizing the output of NER, you can tell what people, places, or themes are present in the documents. Check out the planned features for an overview of some common text processing techniques I'd like to build into it.

## Planned Features/TODO
- Named Entity Recognition (NER) to identify people/named entities present in the data
  - Uses SpaCy's vanilla en_core_web_lg model presently
    - Could create a custom SpaCy NER model for this
  - Sentiment Analysis by entity ("Sent4Ent")
    - Might necessitate some Entity Linking or Coreference Resolution to cluster different spellings/references of particular folks together, so you don't have a **vocabulary mismatch** problem.
- Graph Analysis:
  - Which entities occur together in documents?
  - Which documents cover similar themes?
- Event Detection:
  - Can we find emerging 'events', given large drops of reporting in a small amount of time?
- Text Classification:
  - Assign classes/tags given various features of the data. Is this article about politics? Military? etc.
