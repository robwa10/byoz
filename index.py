# This code is written in Python 2

# Imported modules
from datetime import datetime  # For getting the current time during logging
import json  # For parsing JSON and converting strings to JSON
import random  # For creating a Zap ID
import time  # For creating our syncing interval
import urllib2  # For making all our HTTP requests

# Global variables for our requests
API_KEY = 'a_key'
BASE_URL = 'a_url'

# Create a deduplication list
dedupe_list = []

# To help build the dedupe list and skip the action when the program starts
first_run = True

# Create a trigger function
def get_new_items():
    """Get the items in the trigger app and return anything new."""

    # This is where we will hold our data until we return it
    new_items_list = []

    # Let's try and get all the items from the trigger app
    # and add new data to the new_item_list
    try:
        # Build the url of the Airtable sheet we want to poll
        url = BASE_URL + '/Trigger%20Table?api_key=' + API_KEY
        # Make the request for the data
        request = urllib2.Request(url)
        # Open up the request to get the data
        response = urllib2.urlopen(request)

        # urllib2 returns a file object so we need to open it
        data = response.read()
        # Now we turn the string returned into a JSON object
        json_obj = json.loads(data)

        # Build a dictionary for logging purposes
        log_data = {
            'host': request.get_host(),
            'request_method': request.get_method(),
            'status_code': response.getcode(),
            # response.info returns an instance so we need to turn it into a string
            'meta_data': str(response.info()),
            'url': request.get_full_url(),
            'response_data': data
        }

        # Let's just print the log data to the Terminal for now
        print 'Trigger Log:\n', log_data

        # Iterate over the data we got back to see if anything is new
        for object in json_obj['records']:
            # Check if the id is in the dedupe_list
            if object['id'] not in dedupe_list:
                # Airtable doesn't return the cell/field key if there's no data
                # in that cell. So we check if the last cell is empty,
                # this makes sure we don't trigger while someone is adding
                # data in the row.
                if 'Email' in object['fields']:
                    # Let's add the id to the dedupe_list first
                    dedupe_list.append(object['id'])
                    # And then add the data to the new_items_list
                    new_items_list.append(object)

        # Just like Zapier we'll at least return an empty list
        return new_items_list

    # If we have an error on the request let's catch it and log it
    except urllib2.HTTPError as e:
        # Build the log dictionary
        error_data = {
            'code': e.code,
            'message': e.read(),
            'info': str(e.info())
            }

        # For now print the error to the Terminal
        print 'Trigger Error Log:\n', error_data

# Create an action function

# Set up a while loop to run the Zap

# For now let's invoke the function and print what's returned to the Terminal to see what happens
items = get_new_items()
print 'Trigger Data:\n', items
