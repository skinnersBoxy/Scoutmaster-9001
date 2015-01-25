import datetime
import conf, database, scraper
import pymongo.cursor


# Current year
year = datetime.date.today().year


# Event list table in the database
events = None


def get_match_list(event):
    return database.get_table(event).all()


def get_match(event, qual, number):
    # Match ID
    match_id = event + "_"
    
    # Convert the qualification into a BlueAlliance value
    if qual == "final":
        match_id += "f1"
    elif qual[:6] == "sfinal":
        match_id += "sf" + qual[6:]
    elif qual[:6] == "qfinal":
        match_id += "qf" + qual[6:]
    elif qual == "qual":
        match_id += "qm"

    # Add the match number
    match_id += 'm' + str(number)

    # Look up and return the match
    matches = database.get_table(event)
    return matches.find_one(key=match_id)


def init():
    """Initialize the event handler"""
    # Create the event table if it doesn't exist
    global events
    try:
        events = database.get_collection("events")
    except:
        # Create the event table
        events = database.add_collection("events")

        # Override the current year if it's in the configuration file
        year = conf.lookup("year", year)

        # Get a list of events from the Blue Alliance API and add it
        scraped_events = scraper.get_events(year)
        print(scraped_events)
        for event in scraped_events:
            events.insert(event)

    # Add the matches for each event
    for event in pymongo.cursor.Cursor(events):
        # Create the matches table if it doesn't exist
        try:
            matches = database.get_collection(event[key])
        except:
            # Create the match table
            matches = database.add_collection(event[key])

            # Get a list of matches from the Blue Alliance API and add it
            matches.insert(scraper.get_matches(event))
