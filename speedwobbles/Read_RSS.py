#!/usr/bin/env python
# encoding: utf-8

import pandas as pd
import re
import requests
import sqlite3
import uuid

from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

# - https://stackoverflow.com/questions/70770541/how-to-parse-data-from-google-alerts-using-scrapy-in-python
# - https://www.simplified.guide/scrapy/scrape-rss
# - https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html

print("Reading RSS feed...")

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

url = 'https://www.google.com/alerts/feeds/14966249695842301360/8191453454664689556'
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'html.parser')

try:
    df_existing = pd.read_sql_query("SELECT * from RSS_Hits", con)
except Exception as e:
    print(e.with_traceback())
    df_existing = pd.DataFrame(columns=['GUID', 'Title', 'Date_Published', 'Date_Retrieved', 'Excerpt',
                                        'Google_Link', 'Link', 'Site'])

output = []
for entry in soup.find_all('entry'):

    item = {
        'Title': entry.find('title', {'type': 'html'}).text,
        'Date_Published': entry.find('published').text,
        'Date_Retrieved': str(datetime.utcnow()),
        'Excerpt': entry.find('content').text,
        'Google_Link': entry.find('link')['href'],
    }

    output.append(item)

df = pd.DataFrame(output)
df['GUID'] = [str(uuid.uuid4()) for x in range(len(df))]


def extract_url(GALink):
    match = re.findall(r"(?:&url=)(.*)(?:&ct=)", GALink)
    return match[0]


def get_base_url(link):
    t = urlparse(link).netloc
    baseurl = '.'.join(t.split('.')[-2:])

    return baseurl


df['Link'] = df['Google_Link'].apply(extract_url)
df['Site'] = df['Link'].apply(get_base_url)
# df['Hash'] = df[['Title', 'Excerpt', 'Google_Link', 'Link']].apply(lambda x: hash(tuple(x)), axis = 1)


# Compare the links, only write the new stuff
old_links = df_existing['Link'].tolist()
df_out = df[~df['Link'].isin(old_links)]

# Write the new DataFrame to a new SQLite table
df_out.to_sql("RSS_Hits", con, if_exists="append", index=False)

con.close()

now = datetime.utcnow()
with open(fr"./Logs/Read_RSS_run_{str(now.strftime('%m_%d_%Y, %H_%M_%S'))}.txt", 'w') as f:
    f.write(str(now)+"\n")
    f.write(f"RSS feed identified {len(df)} links")

print(f"\t>>Read {len(df)} links")
print(f"\t>>RSS feed identified {len(df_out)} new links")

print("Done!")
