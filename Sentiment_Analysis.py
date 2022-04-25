print("Running Sentiment Analysis...")

from textblob import TextBlob
import sqlite3
import pandas as pd
name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

def get_Sentiment(text):
    blob = TextBlob(text)
    sents = []
    polarities = []
    subjectivities = []
    for sent in blob.sentences:
        sents.append(str(sent))
        polarities.append(sent.sentiment.polarity)
        subjectivities.append(sent.sentiment.subjectivity)

    return sents, polarities, subjectivities

def avg(mylist):
    return sum(mylist)/len(mylist)


def process_article(text):
    sents, polarities, subjectivities = get_Sentiment(text)

    return avg(polarities), avg(subjectivities)

try:
    df = pd.read_sql_query(
        "SELECT * from cleaned_table c LEFT JOIN Sentiment_TextBlob s ON c.GUID = s.GUID WHERE TRUE AND s.GUID IS NULL AND c.Body is not 'Error'",
        con)
    df = df.loc[:, ~df.columns.duplicated()]
except:
    df = pd.read_sql_query("SELECT * from cleaned_table", con)

if len(df)>0:
    print(f"\t>>Found {len(df)} articles for Sentiment Analysis...")

    a = df['Body'].apply(process_article)

    polarities = [y[0] for y in a]
    subjectivities = [y[1] for y in a]

    df['Polarity'] = polarities
    df['Subjectivity'] = subjectivities

    df[['GUID', 'Subjectivity', 'Polarity']].to_sql("Sentiment_TextBlob", con, if_exists="append", index=False)
else:
    print("\t>> No articles found for Sentiment Analysis, skipping...")

print("Done!")