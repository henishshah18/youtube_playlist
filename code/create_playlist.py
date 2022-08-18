import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from custom_logger import create_logger

logger = create_logger('../data/test.log',__name__)

def load_credentials():
  credentials=None

  if os.path.exists('../data/token.pickle'):
      logger.info('Loading Credentials From File...')
      with open('../data/token.pickle', 'rb') as token:
          credentials = pickle.load(token)

  # If there are no valid credentials available, then either refresh the token or log in.
  if not credentials or not credentials.valid:
      if credentials and credentials.expired and credentials.refresh_token:
          logger.info('Refreshing Access Token...')
          credentials.refresh(Request())
      else:
          logger.info('Fetching New Tokens...')
          flow = InstalledAppFlow.from_client_secrets_file(
              '../data/client_secrets.json',
              scopes= ['https://www.googleapis.com/auth/youtube']
          )

          flow.run_local_server(port=8080, prompt='consent',
                                authorization_prompt_message='')
          credentials = flow.credentials

          # Save the credentials for the next run
          with open('../data/token.pickle', 'wb') as f:
              logger.info('Saving Credentials for Future Use...')
              pickle.dump(credentials, f)
  return credentials

def initiate_playlist(inp,credentials):
  inp = ' '.join([word.capitalize() for word in inp.split()])
  youtube = build('youtube','v3',credentials=credentials)
  request = youtube.playlists().insert(
          part="snippet,status",
          body={
            "snippet": {
              "title": f"Playlist for {inp}",
              "description": f"Set of videos from very famous Youtubers creating video content in {inp}.",
              "tags": [f'inp'],
              "defaultLanguage": "en",
            },
            "status": {
              "privacyStatus": "public"
            }
          }
      )
  response_playlist = request.execute()
  return response_playlist


def add_videos_to_playlist(yt_vid_ids,response_playlist,credentials):
  youtube = build('youtube','v3',credentials=credentials)
  for videoId in yt_vid_ids:
    request = youtube.playlistItems().insert(
          part="snippet",
          body={
            "snippet": {
              "playlistId": str(response_playlist['id']), #an actual playlistid
              "resourceId": {
                "kind": "youtube#video",
                "videoId": videoId
              }
            }
          }
        )
    response = request.execute()
  print('Your playlist is created!')


