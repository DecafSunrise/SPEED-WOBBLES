print("Running NER...")

import sqlite3
from itertools import *
import pandas as pd
import spacy

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_lg")
nlp.max_length = 1250000 # or higher
try:
    df = pd.read_sql_query(
        "SELECT * from cleaned_table c LEFT JOIN NER_Vanilla_SpaCy n ON c.GUID = n.GUID WHERE TRUE AND n.GUID IS NULL AND c.Body is not 'Error'",
        con)
    df = df.loc[:, ~df.columns.duplicated()]
except:
    df = pd.read_sql_query("SELECT * from cleaned_table", con)


def getEnts(i):
    doc = nlp(i)
    entities = {key: list(set(map(lambda x: str(x), g))) for key, g in groupby(sorted(doc.ents, key=lambda x: x.label_), lambda x: x.label_)}

    return entities


def addEnts(dataframe, columnName):
    extracted = []

    for i, row in dataframe.iterrows():
        ents = getEnts(row[columnName])
        extracted.append(ents)

    dataframe["ExtractedEnts"] = extracted

    return dataframe

def splitEnts(dataframe):
    df_temp = pd.json_normalize(dataframe['ExtractedEnts'])
    dataframe = pd.concat([dataframe, df_temp], axis=1)

    return dataframe

if len(df)>0:
    print(f"\t>>Found {len(df)} new articles for NER")
    df = addEnts(df, 'Body')

    results = list()

    for i, row in df.iterrows():
        GUID = row['GUID']
        extracted = row['ExtractedEnts']
        for EntType in extracted:
            for hit in extracted[EntType]:
                results.append([GUID, EntType, hit])

    ner_df = pd.DataFrame(results, columns=['GUID', 'EntityType', 'Entity'])

    ner_df.to_sql("NER_Vanilla_SpaCy", con, if_exists="append", index=False)
else:
    print("\t>>No new articles to NER, skipping...")

print("Done!")