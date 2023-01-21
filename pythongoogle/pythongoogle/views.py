
from googleapiclient.discovery import build

from django.shortcuts import render, redirect
from django.urls import reverse

import google.oauth2.credentials
import google_auth_oauthlib.flow

# permissions set for the Google App to be accessed currently it is set to view and download only
# more permissions here https://developers.google.com/identity/protocols/oauth2/scopes
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# view used to request from spreadsheet 
def key(request):
    # created API key in Google Cloud
    key = "AIzaSyADUq4uB1aHPVvFQl-5d0ELgIGX0RGEW8I"

    # access Google Sheets API with API key
    service = build('sheets', 'v4', developerKey=key)

    # fetch rows
    # see function calls here https://github.com/googleapis/google-api-python-client/blob/main/docs/dyn/index.md
    rows = service.spreadsheets().values().get(spreadsheetId="1LSZ5vsoTSNRNyBNLB3PhLRZ7TG_bPKHVadl4NYwJVQQ", range="A:D").execute()

    print(rows)
    
    return render(request, "index.html")

# home view
def home(request):

    # if we have the credentials stored in the session
    if ('credentials' in request.session):
        # convert dictionary to oauth2 credentials
        credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])

        # access Google Sheets API with oauth2 credentials
        service = build('sheets', 'v4', credentials=credentials)

        # fetch rows
        rows = service.spreadsheets().values().get(spreadsheetId="1LSZ5vsoTSNRNyBNLB3PhLRZ7TG_bPKHVadl4NYwJVQQ", range="A:D").execute()

        print(rows)

        return render(request, "index.html")

    # fetch token using the credentials in creds.json
    else:
        # create flow from client credentials downloaded from Google cloud
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('creds.json', scopes=SCOPES)
    
        # URI where the oauth2's response will be redirected this must match with one of the authorized URIs configured in Google Cloud
        flow.redirect_uri = 'http://localhost:8000/oauthcallback/'

        # configuring the authorization url which will be used to request from oauth2
        authorization_url, state = flow.authorization_url(include_granted_scopes='true', access_type='offline')

        # store the state in the session
        request.session['state'] = state
        
        # redirect to the authorization url which will redirect back to the callback view
        print(authorization_url)
        return redirect(authorization_url)



# callback used to extract the credentials. this will have a URL with query parameters set to the necessary arguments to extract the credentials e.g. http://localhost/oauthcallback/?state=K15TtnzoBKKepgg0Z3Ph86nEgGiubM&code=4%2F0AWgavdeDqFt44lGsb24OidcJrpSeLUja1OZkhfHNgNsacb00BrKgyeA-6pY7Uw08lt7s9g&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets
def callback(request):
    # get URL of the callback
    response = request.get_full_path()

    # extract the state stored from the home view
    state = request.session['state']

    # create a new flow note that scopes were not defined because it gets appended to the previous scopes
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
     'creds.json', scopes=None, state=state)

    # same redirect uri as before
    flow.redirect_uri = 'http://localhost:8000/oauthcallback/'

    # function call to get the credentials
    flow.fetch_token(authorization_response=response)

    # store the fetched credentials
    credentials = flow.credentials

    # convert credentials to dictionary
    request.session['credentials'] = credentials_to_dict(credentials)

    # go back to the home page
    return redirect(reverse('home'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}