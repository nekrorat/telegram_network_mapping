# dotenv allows to set environment variable (this one is actually just a dict)
import os
from dotenv import dotenv_values

#if .env exists 
#.env format:
#   phone="string"
#   api_id="string"
#   api_hash="string"
#   
if os.path.isfile('.env'):
    config = dotenv_values('.env')
#if .env doesn't exist -> user input required values
else:
    info = '\nCan be found here -> https://my.telegram.org/ -> api development tools\nEnter App'
    config = {'phone': '', 'api_id': input(f'{info} api_id: '), 'api_hash': input(f'{info} api_hash: ')}