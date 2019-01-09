# This code is written in Python 2

# Imported modules
from datetime import datetime # For getting the current time during logging
import json # For parsing JSON and converting strings to JSON
import random  # For creating a Zap ID
import time # For creating our syncing interval
import urllib2 # For making all our HTTP requests

# Global variables for our requests
API_KEY = 'a_key'
BASE_URL = 'a_url'

# Create a deduplication list
dedupe_list = []

# To help build the dedupe list and skip the action when the program starts
first_run = True

# Create a trigger function

# Create an action function

# Set up a while loop to run the Zap
