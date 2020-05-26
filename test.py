import credentials as credentials
from firebase import firebase

from google.oauth2 import credentials
from apiclient import discovery

client_secret = "xHIfKIILzqW2il79LTOcMH6g"
client_id = "736516281309-po1q1islep9oekni2p4fcs9ftm12si68.apps.googleusercontent.com"
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
refresh_url = "https://oauth2.googleapis.com/token"
scopes = "https://www.googleapis.com/auth/youtube.readonly"

firebase = firebase.FirebaseApplication('https://notifier-1138.firebaseio.com/', None)

def writefirebase(location, data):
    firebase.put('/', location, data)

def readfirebase(location):
    return firebase.get('/', location)




def updateViews():
    creds = credentials.Credentials(
        readfirebase("402344993391640578")["access_token"],
        refresh_token=readfirebase("402344993391640578")["refresh_token"],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=client_id,
        client_secret=client_secret
    )

    youtube = discovery.build("youtube", "v3", credentials=creds)

    req = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=25,
        playlistId=youtube.channels().list(part="snippet,contentDetails,statistics", mine=True).execute()["items"][0][
            "contentDetails"]["relatedPlaylists"]["uploads"]
    ).execute()



    new_list = {}

    for item in req["items"]:
        new_list[item["contentDetails"]["videoId"]] = ""

    ids = ""
    count = 0

    for key in list(new_list.keys()):

        temp = ids
        ids = temp + key + ","

        count += 1

    req = youtube.videos().list(
        part="statistics",
        id=ids
    ).execute()

    print(req["items"])

    a = [{'kind': 'youtube#video', 'etag': 'yrMV5sWGivsnDqc4_Y9ZY3_vJEI', 'id': 'aM22TRaLBc0', 'statistics': {'viewCount': '6', 'likeCount': '2', 'dislikeCount': '0', 'favoriteCount': '0', 'commentCount': '0'}}, {'kind': 'youtube#video', 'etag': 'VfHYqiWb7ma5RJWkpxXlNU5m2eM', 'id': 'rRfRkvI9uQ0', 'statistics': {'viewCount': '13', 'likeCount': '4', 'dislikeCount': '0', 'favoriteCount': '0', 'commentCount': '0'}}, {'kind': 'youtube#video', 'etag': 'IP8IWBlGoEaKxg3UjfHT4S1tAGI', 'id': 'Vsu-C2cetpw', 'statistics': {'viewCount': '15', 'likeCount': '1', 'dislikeCount': '1', 'favoriteCount': '0', 'commentCount': '3'}}]


    for (a, b) in zip(req["items"], sorted(list(new_list.keys()))):
        new_list[b] = a["statistics"]["likeCount"]
    print(new_list)





updateViews()