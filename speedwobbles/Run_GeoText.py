import pandas as pd
import sqlite3

from geotext import GeoText

print("Running GeoText...")

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")


def get_cities(geotextobj):
    return geotextobj.cities


def get_countries(geotextobj):
    return geotextobj.countries


def get_country_mentions(geotextobj):
    return geotextobj.country_mentions


try:
    df = pd.read_sql_query("SELECT * from Body_Text b LEFT JOIN GeoText_Status g ON g.GUID = b.GUID WHERE TRUE AND g.GUID IS NULL", con)
    df = df.loc[:, ~df.columns.duplicated()]
except Exception as e:
    print(e.with_traceback())
    df = pd.read_sql_query("SELECT * from Body_Text b", con)

if len(df) > 0:

    print(f"\t>>Identified {len(df)} article(s) to scrub for Geospatial Text...")

    df_status = pd.DataFrame(df['GUID'], columns = ['GUID', 'GeoText_Applied'])
    df_status['GeoText_Applied'] = True

    df.Body = df.Body.astype('str')

    df['GeoText'] = df['Body'].apply(GeoText)

    df['Cities'] = df['GeoText'].apply(get_cities)
    df['Countries'] = df['GeoText'].apply(get_countries)
    # df['Country_Mentions'] = df['GeoText'].apply(getCountryMentions)

    city_df = df[['GUID', 'Cities']].explode('Cities')
    city_df = city_df[~city_df['Cities'].isnull()]
    city_df = city_df.drop_duplicates(subset=['GUID', 'Cities'])

    Country_df = df[['GUID', 'Countries']].explode('Countries')
    Country_df = Country_df[~Country_df['Countries'].isnull()]
    Country_df = Country_df.drop_duplicates(subset=['GUID', 'Countries'])

    # df_mentions = df[['GUID', 'Country_Mentions']]
    # pd.DataFrame(df_mentions['Country_Mentions'].explode())

    df_status.to_sql("GeoText_Status", con, if_exists='append', index=False)
    city_df.to_sql("GeoText_Cities", con, if_exists='append', index=False)
    Country_df.to_sql("GeoText_Countries", con, if_exists='append', index=False)
    # df_mentions.to_sql("GeoText_Country_Mentions", con, if_exists='append', index=False)

else:
    print("\t>>No docs to process for geospatial text, exiting...")

print("Done!")
