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

# Copy the code under here


# To help us in creating a task_id
def random_number():
    return random.randint(1000, 9999)


# Write success and errors to log files
def write_logs(log_data):
    # Use today's date as the filename
    today = datetime.today().strftime('%Y-%m-%d')
    filename = './logs/' + str(today) + '.json'

    # Open the file in append mode. This way we write all the logs from today
    # to a single file.
    with open(filename, 'a') as f_obj:
        json.dump(log_data, f_obj, sort_keys=True, indent=4)


# Create a trigger function
def get_new_items(task_id):
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
            'task_id': task_id,
            'trigger_success_log': {
                'timestamp': str(datetime.now()),
                'host': request.get_host(),
                'request_method': request.get_method(),
                'status_code': response.getcode(),
                # response.info returns an instance so we turn it into a string
                'meta_data': str(response.info()),
                'url': request.get_full_url(),
                'response_data': json_obj
            }
        }

        # Write the Trigger log
        write_logs(log_data)

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

    # Catch and log any errors
    except urllib2.HTTPError as e:

        # Build the log dictionary
        error_data = {
            'task_id': task_id,
            'trigger_error_log': {
                'timestamp': str(datetime.now()),
                'code': e.code,
                'message': e.read(),
                'info': str(e.info())
            }
        }

        # Write the error log
        write_logs(error_data)

        # Return the empty list so the loop continues
        return new_items_list


# Create an action function
def write_new_items(trigger_data, task_id):
    """Write all the items returned by the trigger."""

    # Set our url to the Action Table in Airtable
    url = BASE_URL + '/Action%20Table'

    # Specify our headers for the request
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json'
        }

    # Iterate over each object in the list returned by the Trigger function
    for item in trigger_data:
        # The fields key holds the values of the newly created row
        fields = item['fields']

        # Map the data to send to our Action Table
        values = {
            'fields': {
                'Email': fields['Email'],
                'Name': fields['Name']
            }
        }
        # Turn the data into JSON before we send it
        data = json.dumps(values)

        try:
            # Create the request and open it
            request = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(request)

            # Read the response we got back from the request
            action_data = response.read()

            # Build the log dictionary
            log_data = {
                'task_id': task_id,
                'action_success_log': {
                    'timestamp': str(datetime.now()),
                    'host': request.get_host(),
                    'request_method': request.get_method(),
                    'status_code': response.getcode(),
                    'meta_data': str(response.info()),
                    'url': request.get_full_url(),
                    'input_data': values,
                    'response_data': json.loads(action_data)
                }
            }

            # Write the Action log
            write_logs(log_data)

        # Catch and log any errors
        except urllib2.HTTPError as e:

            # Build the log dictionary
            error_data = {
                'task_id': task_id,
                'action_error_log': {
                    'timestamp': str(datetime.now()),
                    'code': e.code,
                    'message': e.read(),
                    'info': str(e.info())
                }
            }

            # Write the error log
            write_logs(error_data)


# Just to let us know the program started
print 'Zap on'

# Set up a while loop to run the Zap
while True:

    # Create a unique ID for this instance of the Zap
    task_id = str(random_number()) + '-' + str(random_number())

    # Call the trigger function to see if anything new is added
    items = get_new_items(task_id)

    # Only run the Action if this isn't the first time through the loop
    # and there is something returned by the Trigger function
    if first_run is False and len(items) > 0:
        write_new_items(items, task_id)

    # We only want to skip the Action the first time through the loop
    first_run = False

    # Set our syncing interval
    time.sleep(6)
