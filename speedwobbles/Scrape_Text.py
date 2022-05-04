#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import random
import sqlite3
import time

from boilerpy3 import extractors
from datetime import datetime
from tqdm import tqdm

# Create new `pandas` methods which use `tqdm` progress
# (can use tqdm_gui, optional kwargs, etc.)
tqdm.pandas()

extractor = extractors.ArticleExtractor()

print("Scraping Text...")

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

# cursor = con. cursor()
# cursor. execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor. fetchall())

# We can always add better error handling, 'cuz god knows this'll get messed up
# TODO: Implement better error handling 'cuz God knows this'll get messed up
try:
    df = pd.read_sql_query("SELECT * from RSS_Hits t1 LEFT JOIN Scrape_Status t2 ON t1.GUID = t2.GUID WHERE TRUE AND t2.GUID IS NULL", con)
    df = df.loc[:, ~df.columns.duplicated()]
except Exception as e:
    df = pd.read_sql_query("SELECT * from RSS_Hits", con)


print(f"\t>>Identified {len(df)} document(s) to scrape")


def get_article_content(url):
    # print(url)
    time.sleep(random.randint(1, 3))
    try:
        doc = extractor.get_doc_from_url(url)
        content = doc.content
        # print("\t"+doc.title)

    except Exception as e:
        # print(E)
        content = "Error"

    return content


"""
We probably want to get smarter about how we're checking good/bad values here
- I want to be able to set "rules" to check if stuff meets the criteria
- Rules may need to be able to be sourced from more than just the BaseUrl, probably need to look into a way to 
"""

badlist = [
    'google.com',
    'youtube.com'
]


def determine_scrape_suitability(baseurl):
    if baseurl.lower() in badlist:
        return False
    else:
        return True


def sanity_clean(df):
    """
    Does some light cleanup on the output variables, so we have useful clean data to validate our stuff on
    """

    # If your Body text is less than 6, you've got a problem
    df.loc[df['Body'].str.len() < 6, 'Failed_Scrape'] = True

    # If your Body text is blank, set it to our common 'Error' value
    df.loc[df['Body'].str.len() < 6, 'Body'] = 'Error'

    # If the FailedScrape var isn't True, we currently have the alternative just hanging out as an indeterminite value.
    # Let's make that explicitly False.
    # TODO: This is where the confusion started.
    df.loc[df['Failed_Scrape'] != True, 'Failed_Scrape'] = False

    # If your Body text is a NaN, set it to our common 'Error' value
    df.loc[df['Body'].isnull(), 'Body'] = 'Error'

    return df


df['Suitable'] = df['Site'].apply(determine_scrape_suitability)

# TODO: I'm really confused.
df['Body'] = df[df['Suitable']==True]['Link'].progress_apply(get_article_content)
df.loc[df['Suitable']==True, 'Scrape_Attempted']=True
df.loc[df['Suitable']==False, 'Scrape_Attempted']=False

df = sanity_clean(df)


TotalQueueLen = len(df)
UnsuitableLen = len(df[df['Suitable'] == False])
SuitableLen = len(df[df['Suitable'] == True])
FailCount = len(df[(df['Suitable'] == True) & (df['Failed_Scrape'] == True)])


# print("""\n\n/////     /////     /////\n\n""")


# Tests

# assert TotalQueueLen == (SuitableLen+UnsuitableLen), "Something went wrong with your Suitability function!"
# assert FailCount <= SuitableLen, "How can you fail more things than you checked?"

df['Manually_Fixed'] = False
df['Dead_Letter'] = False

df_scrape_status = df[['GUID', 'Suitable', 'Scrape_Attempted', 'Failed_Scrape', 'Manually_Fixed', 'Dead_Letter']]
df_scrape_status.to_sql("Scrape_Status", con, if_exists="append", index=False)

# TODO: I'm still confused.
df_body_text = df[df['Failed_Scrape'] == False][['GUID', 'Body']]
df_body_text.to_sql("Body_Text", con, if_exists="append", index=False)

now = datetime.utcnow()

with open(fr"./Logs/Scrape_Text_run_{str(now.strftime('%m_%d_%Y, %H_%M_%S'))}.txt", 'w') as f:
    f.write(str(now)+"\n")
    try:
        print(f"\t>>{SuitableLen}/{TotalQueueLen} ({round((SuitableLen / TotalQueueLen) * 100, 1)}%) of things in the queue are appropriate for scraping")
        print(f"\t>>{FailCount}/{SuitableLen} ({round((FailCount / SuitableLen) * 100, 1)}%) failed Rate")
        f.write(f"{SuitableLen}/{TotalQueueLen} ({round((SuitableLen/TotalQueueLen)*100, 1)}%) of things in the queue are appropriate for scraping\n")
        f.write(f"{FailCount}/{SuitableLen} ({round((FailCount/SuitableLen)*100, 1)}%) failed Rate\n")

    except Exception as e:
        print("\t>>Queue length was zero, exiting...")
        f.write("Queue length was zero, exiting...")


print("Done!")
