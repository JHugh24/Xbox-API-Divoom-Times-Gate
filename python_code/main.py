import requests
import webbrowser
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os
from flask import Flask


# Flask is used to maintain created credentials in order to use https for localhost URL instead of http
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, HTTPS!"

if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem')) # Obtains the certification and key files for the approved SSL certification


# Azure app details
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID') # Azure app unique identifier
# CLIENT_SECRET = os.getenv('CLIENT_SECRET') # App secret key for authentication when requesting tokens
TENANT_ID = os.getenv('TENANT_ID') # Azure Active Directory tenant identifier
REDIRECT_URI = os.getenv('REDIRECT_URI') # URL for Microsoft to redirect to after authentication, use http://localhost for local testing

# Details for requesting authorization code, the ampersand (&) is used as a parameter seperator when constructing the authorization URL, the question mark (?) indicates that what follows is the query string
auth_url = ( # auth_url is the endpoint for Microsoft OAuth 2.0, using the configurable parameters inside to build the full URL
    f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?" # Base endpoint URL using tenant_id to identify the app being connected to
    f"client_id={CLIENT_ID}&" # Applications client ID
    "response_type=code&" # Configures what type of response you want, code indicates you want an authorization code
    "redirect_uri=https://localhost&" # Specifies the redirection URL for after the authorization request is complete
    "response_mode=query&" # Specifies how the response will be given, using query indicates that it will return as a query parameter in the redirect URL
    "scope=Xboxlive.signin Xboxlive.offline_access" # The scope of the permissions the app is requesting, in this case it is requesting permissions for xbox live sign in and offline access
)


webbrowser.open(auth_url) # This function calls the default web browser and uses it to open the URL given to it, in this case the auth_url that has been built 

redirect_response = input("Paste the redirect URL here: ") # Requests user to paste redirect response URL that has been given from Microsoft containing the authorization code. Change: Work to automate this portion so no input is needed
parsed_url = urlparse(redirect_response) # urlparse parses the input URL into its components, in this case we are doing this to gain access to the parsed out query string from the redirect response URL
auth_code = parse_qs(parsed_url.query)['code'][0] # parse_qs parses the query strings parameters into a dictionary of "parameter: [value]" pairs, specifically for this functoin "code: [0]" extracts the authorization code from the query string 

# Using the Authorization Code to obtain an Access Token

token_url = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/token" # Token endpoint URL for Microsoft OAuth 2.0, using the Tenant ID to identify the app being connected to
token_data = { # token_data is a dictionary containing the data being sent in the request for the token
    'client_id': CLIENT_ID, # Client ID is the unique identifier that specifies what app you are requesting the token for
 #   'client_secret': CLIENT_SECRET, # Client Secret is essentially the password created within Azure that authenticates the app to be used in the request
    'code': auth_code, # The authorization code that was obtained from the redirect response url after a succesfull authorization through Microsofts OAuth 
    'redirect_uri': REDIRECT_URI, # The base redirect URL, must match with the URI obtained from the authorization request
    'grant_type': 'authorization_code', # grant_type specifies what your are using to exchange for the Token, in this case we are using the authorization code obtained from the authorization request redirect URI
    'scope': 'Xboxlive.signin Xboxlive.offline_access' # The scope of the permissions the app is requesting, in this case it is requesting permissions for xbox live sign in and offline access
}

response = requests.post(token_url, data=token_data) # requests.post sends a POST request to the Token endpoint using the token_data dictionary that was created as the request body, this is where the actual exchange of authorization code for access token happen
if response.status_code == 200: # This is checking whether or not the request was successful, status code 200 indicates a success
    token_response = response.json() # This parses the JSON response from the endpoint, the response normally includes an access_token to authenticate API requests, a refresh_token used to get new tokens when the current one expires, and the expires_in field which indicates in seconds how long until the token expires
    access_token = token_response['access_token'] # This is setting the access_token from the parsed JSON response to the access_token variable
    print("Access Token:", access_token) # Prints out the access token, allowing validation in the terminal that the response was fully successful
else:
    print("Failed to retrieve access token:", response.status_code, response.text) # Handles errors that come from the token exchange request, printing out the status code received and any error message that may accompany it





# def print_test():
#     print(CLIENT_ID)

# def main():
#     print_test()


# main()