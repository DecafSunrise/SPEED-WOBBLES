# TODO: 1. Verify functionality following reformat
# TODO: 2. Implement logging
# TODO: 3. Move helper functions/utils to dedicated file
# TODO: 4. Implement threading

print("\nStage 0:")
exec(open("Fetch_Manually_Added_Links.py").read())
print("\nStage 1:")
exec(open("Read_RSS.py").read())
print("\nStage 2:")
exec(open("Scrape_Text.py").read())
print("\nStage 3:")
exec(open("Create_views.py").read())
print("\nStage 4:")
exec(open("NER_Vanilla_SpaCy.py").read())
print("\nStage 5:")
exec(open("Run_GeoText.py").read())
print("\nStage 6:")
exec(open("Sentiment_Analysis.py").read())
