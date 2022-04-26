# https://www.sqlitetutorial.net/sqlite-create-view/

print("Creating cleaned view...")
import sqlite3

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

cur = con.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='view';")
views = [x[0] for x in cur.fetchall()]
# print(views)
## Check to see if the cleaned view has sentiment scores
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [x[0] for x in cur.fetchall()]

cleaned_view = False
if 'cleaned_table' in views:
    cleaned_view = True
    cur.execute("PRAGMA table_info(cleaned_table);")
    schema = [x[1] for x in cur.fetchall()]

sentiment_table = False
if 'Sentiment_TextBlob' in tables:
    sentiment_table = True

if 'cleaned_table' ==False:
    print("\t>>Cleaned Table view not found, creating...")
    # Create table
    if sentiment_table==True:
        try:
            cur.execute('''CREATE VIEW cleaned_table
                            as
                           SELECT r.GUID, r.Date_Published, r.Link, r.Site, r.Title, 
                           b.Body, s.Subjectivity, s.Polarity from RSS_Hits r JOIN 
                           Body_Text b on r.GUID = b.GUID JOIN Sentiment_TextBlob s on s.GUID = r.GUID WHERE b.Body is not 'Error';''')

            # Save (commit) the changes
            con.commit()
        except:
            cur.execute('''CREATE VIEW cleaned_table
                            as
                            SELECT r.GUID, r.Date_Published, r.Link, r.Site, r.Title, 
                            b.Body from RSS_Hits r JOIN Body_Text b on r.GUID = b.GUID WHERE b.Body is not 'Error';''')
            # Save (commit) the changes
            con.commit()
else:

    if 'Sentiment_TextBlob' in tables and 'Polarity' not in schema:
        print("\t>>Updating your view to include Sentiment Analysis!")
        cur.execute("DROP VIEW cleaned_table;")
        con.commit()
        cur.execute('''CREATE VIEW cleaned_table
                        as
                       SELECT r.GUID, r.Date_Published, r.Link, r.Site, r.Title, 
                       b.Body, s.Subjectivity, s.Polarity from RSS_Hits r JOIN 
                       Body_Text b on r.GUID = b.GUID JOIN Sentiment_TextBlob s on s.GUID = r.GUID WHERE b.Body is not 'Error';''')

        # Save (commit) the changes
        con.commit()

    else:

        print("\t>>You've already got the Cleaned Table, skipping...")

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()

print("Done!")