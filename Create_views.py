# https://www.sqlitetutorial.net/sqlite-create-view/

print("Creating cleaned view...")
import sqlite3

name = 'Operation_Lonestar'
con = sqlite3.connect(f"{name}_db.sqlite")

cur = con.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='view';")
views = [x[0] for x in cur.fetchall()]
# print(views)

if not 'cleaned_table' in views:
    print("\t>>Cleaned Table view not found, creating...")
    # Create table
    cur.execute('''CREATE VIEW cleaned_table
                    as
                    SELECT r.GUID, r.Date_Published, r.Link, r.Site, r.Title, 
                    b.Body from RSS_Hits r JOIN Body_Text b on r.GUID = b.GUID;''')

    # Save (commit) the changes
    con.commit()
else:
    print("\t>>You've already got the Cleaned Table, skipping...")

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()

print("Done!")