import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils.logger import logger
import config


class SheetsAuthenticator:

    def __init__(self):
        self.creds: Credentials = None
        self.service = None

    def authenticate(self):
    
        if os.path.exists(config.TOKEN_FILE):
            with open(config.TOKEN_FILE, "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Refreshing authentication token...")
                self.creds.refresh(Request())
            else:
                logger.info("Starting authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, config.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open(config.TOKEN_FILE, "wb") as token:
                pickle.dump(self.creds, token)

            logger.info("✅ Authentication successful")

        self.service = build("sheets", "v4", credentials=self.creds)
        return self.service

    def get_service(self):
        """
        Get authenticated service, authenticating if necessary

        Returns:
            Google Sheets API service object
        """
        if not self.service:
            return self.authenticate()
        return self.service
