# dotenv allows to set environment variable (this one is actually just a dict)
import os
from pathlib import Path
from dotenv import dotenv_values

# if .env exists
# .env format:
#   PHONE="string"
#   API_ID="string"
#   API_HASH="string"

if os.path.isfile(f'{Path(__file__).parent.parent.parent}/.env'):
    config = dotenv_values(f'{Path(__file__).parent.parent.parent}/.env')
# if .env doesn't exist -> user input required values
else:
    info = '\nCan be found here -> https://my.telegram.org/ -> api development tools\nEnter'
    config = {'phone': '', 'api_id': input(f'{info} api_id: '), 'api_hash': input(f'{info} api_hash: ')}
