import pandas as pd
import spacy
import sqlite3

from itertools import *

print("Running NER...")

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

spacy.prefer_gpu()
# TODO: check if NLP model exists before execution
nlp = spacy.load("en_core_web_lg")
nlp.max_length = 1250000  # or higher
try:
    df = pd.read_sql_query(
        "SELECT * from cleaned_table c LEFT JOIN NER_Vanilla_SpaCy n ON c.GUID = n.GUID WHERE TRUE AND n.GUID IS NULL AND c.Body is not 'Error'",
        con)
    df = df.loc[:, ~df.columns.duplicated()]
except Exception as e:
    df = pd.read_sql_query("SELECT * from cleaned_table", con)


def get_entities(data):
    doc = nlp(data)
    entities = {key: list(set(map(lambda x: str(x), g))) for key, g in groupby(sorted(doc.ents, key=lambda x: x.label_), lambda x: x.label_)}

    return entities


def add_entities(dataframe, column_name):
    _extracted = []

    for i, row in dataframe.iterrows():
        ents = get_entities(row[column_name])
        _extracted.append(ents)

    dataframe["ExtractedEnts"] = _extracted

    return dataframe


def split_entities(dataframe):
    df_temp = pd.json_normalize(dataframe['ExtractedEnts'])
    dataframe = pd.concat([dataframe, df_temp], axis=1)

    return dataframe


if len(df) > 0:
    print(f"\t>>Found {len(df)} new articles for NER")
    df = add_entities(df, 'Body')

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
