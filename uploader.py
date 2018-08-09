from __future__ import print_function
from config import CSV_FILENAME, SPREADSHEET_ID
from pathlib import Path
import httplib2
import os, sys, csv, time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

def get_script_path():
    """
    http://stackoverflow.com/a/4943474
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def read_csv(csv_filename):
    contents = []
    with open(csv_filename) as csvfile:
        csvReader = csv.reader(csvfile)
        next(csvReader) # skip the header row
        for row in csvReader:
          if len(row) > 0:
              contents.append(row)
    return contents
    

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials 

def write_spreadsheet(values):
    needs_header = False
    csv_file = os.path.join(os.sep, get_script_path(), CSV_FILENAME)
    print("using CSV file at {}".format(csv_file))
    if not os.path.exists(csv_file):
        needs_header = True

    with open(csv_file, 'a') as csvfile:
        fieldnames = ["Name", "Email", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()
        for row in values:
            writer.writerow({"Name":row[0], "Email":row[1], "Timestamp":row[2]})

def update_spreadsheet(spreadsheet_id, data):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')

    print("data = "+str(data))
    values = data
    print("values = "+str(values))
    values = list(filter(None, values))
    if len(values) == 0:
        print("didn't find any useful data")
        return
    sheetname = "Sheet1"
    spreadsheet_range = sheetname + "!A1:C" + str(len(values))
    valueInputOption = "USER_ENTERED"
    body = {
        'values': values
    }
    try:
        service = discovery.build('sheets', 'v4', http=http,
            discoveryServiceUrl=discoveryUrl)
        response = service.spreadsheets().values().append(spreadsheetId = spreadsheet_id,
                                                   range = spreadsheet_range, valueInputOption = valueInputOption, body=body).execute()
        n_updates = response.get("updates")["updatedRows"]
        if n_updates == len(values):
            print("Successfully updated Google sheets. Deleting "+CSV_FILENAME)
    except (httplib2.ServerNotFoundError, TimeoutError) as e:
        print("Failed to update Google sheets. Look at " +CSV_FILENAME +" for updates.")
        write_spreadsheet(values)

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1e6PV5ejmVUXSXiHPJR033pR1d-wKvLR8G9xWr_n4wtc/edit
    """

    while (True):
        csv_file = Path(CSV_FILENAME)
        if csv_file.is_file(): 
            print("File found. Updating Google spreadsheet.")
            user_data = read_csv(CSV_FILENAME)
            os.remove(CSV_FILENAME)
            update_spreadsheet(SPREADSHEET_ID, user_data) 
        else:
            print("Nothing to upload.")

        time.sleep(30) #Time delay in seconds

if __name__ == '__main__':
    main()
    