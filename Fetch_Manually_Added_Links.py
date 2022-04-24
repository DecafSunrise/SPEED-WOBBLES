print("Fetch manually added links...")

import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import sqlite3
import uuid
from boilerpy3 import extractors

extractor = extractors.ArticleExtractor()

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

def getBaseURL(link):
    t = urlparse(link).netloc
    baseurl = '.'.join(t.split('.')[-2:])

    return baseurl

def get_title(url):
    title = str()
    try:
        doc = extractor.get_doc_from_url(url)
        title = doc.title
    except:
        title = None
    return title

try:
    ## Wrap this whole thing in a Try/Except
    df_url = pd.read_sql_query("SELECT m.Link from Manually_Added_Links m LEFT JOIN RSS_Hits r ON m.Link = r.Link WHERE TRUE AND r.GUID IS NULL", con)

    # df_url
    print(f"Found {len(df_url)} manually-added links to catch up on")

    df_url['GUID'] = [str(uuid.uuid4()) for x in range(len(df_url))]

    df_url['Site'] = df_url['Link'].apply(getBaseURL)
    df_url['Date_Retrieved'] = str(datetime.utcnow())

    df_url['Date_Published'] = None
    df_url['Excerpt'] = None
    df_url['Google_Link'] = None

    df_url['Title'] = df_url['Link'].apply(get_title)

    # df_url

    df_url.to_sql("RSS_Hits", con, if_exists="append", index=False)
except:
    print("No Manual links to catch up on")


print("\n\nDone!")