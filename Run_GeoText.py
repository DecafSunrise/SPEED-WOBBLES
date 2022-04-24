print("Running GeoText...")

import pandas as pd
from geotext import GeoText
import sqlite3
name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")


def getCities(geotextObj):
    return geotextObj.cities

def getCountries(geotextObj):
    return geotextObj.countries

def getCountryMentions(geotextObj):
    return geotextObj.country_mentions

try:
    df = pd.read_sql_query("SELECT * from Body_Text b LEFT JOIN GeoText_Status g ON g.GUID = b.GUID WHERE TRUE AND g.GUID IS NULL", con)
    df = df.loc[:,~df.columns.duplicated()]
except:
    df = pd.read_sql_query("SELECT * from Body_Text b", con)

if len(df)>0:

    print(f"\t>>Identified {len(df)} article(s) to scrub for Geospatial Text...")

    df_status = pd.DataFrame(df['GUID'], columns = ['GUID', 'GeoText_Applied'])
    df_status['GeoText_Applied'] = True

    df.Body = df.Body.astype('str')

    df['GeoText'] = df['Body'].apply(GeoText)

    df['Cities'] = df['GeoText'].apply(getCities)
    df['Countries'] = df['GeoText'].apply(getCountries)
    # df['Country_Mentions'] = df['GeoText'].apply(getCountryMentions)


    city_df = df[['GUID','Cities']].explode('Cities')
    city_df = city_df[~city_df['Cities'].isnull()]
    city_df = city_df.drop_duplicates(subset=['GUID', 'Cities'])

    Country_df = df[['GUID','Countries']].explode('Countries')
    Country_df = Country_df[~Country_df['Countries'].isnull()]
    Country_df = Country_df.drop_duplicates(subset=['GUID', 'Countries'])

    # df_mentions = df[['GUID', 'Country_Mentions']]
    # pd.DataFrame(df_mentions['Country_Mentions'].explode())

    df_status.to_sql("GeoText_Status", con, if_exists='append', index=False)
    city_df.to_sql("GeoText_Cities", con, if_exists='append', index=False)
    Country_df.to_sql("GeoText_Countries", con, if_exists='append', index=False)
    #df_mentions.to_sql("GeoText_Country_Mentions", con, if_exists='append', index=False)

else:
    print("\t>>No docs to process for geospatial text, exiting...")

print("Done!")