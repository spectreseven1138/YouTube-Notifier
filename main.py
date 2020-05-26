# Oauth / Apis
import credentials as credentials
from oauthlib import oauth2
from requests_oauthlib import OAuth2Session
from google.oauth2 import credentials
from apiclient import discovery
from google.auth.exceptions import GoogleAuthError

# Discord
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# Firebase
from firebase import firebase
from firebase_admin.db import reference
import firebase_admin

# Other
import os
import time
import schedule

client = commands.Bot(command_prefix=".")

# Static variables
bot_name = "YouTube Notifier"
owner_ids = ["402344993391640578"]
admin_ids = ["402344993391640578"]

known_firebase_variables = (
"active", "points", "commentCount", "dislikeCount", "favoriteCount", "likeCount", "viewCount", "notif_list")

client_secret = "xHIfKIILzqW2il79LTOcMH6g"
client_id = "736516281309-po1q1islep9oekni2p4fcs9ftm12si68.apps.googleusercontent.com"
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
refresh_url = "https://oauth2.googleapis.com/token"
scopes = "https://www.googleapis.com/auth/youtube.readonly"

auth_url_short = "https://shorturl.at/fzMNR"
auth_url_long = "https://accounts.google.com/signin/oauth/oauthchooseaccount?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.readonly&response_type=code&state=security_token%3D138r5719ru3e1%26url%3Dhttps%3A%2F%2Foauth2.example.com%2Ftoken&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&client_id=736516281309-po1q1islep9oekni2p4fcs9ftm12si68.apps.googleusercontent.com&o2v=2&as=U1xBmkG7iRxTXeekFevTtg&flowName=GeneralOAuthFlow"

stat_types = {"likes": "likeCount",
              "dislikes": "dislikeCount",
              "views": "viewCount",
              "comments": "commentCount",
              "favorites": "favoriteCount"}


@client.event
async def on_ready():
    for id in owner_ids:
        await client.get_user(int(id)).send(bot_name + " is now running")
    print(bot_name + " is now running")
    await client.change_presence(activity=discord.Game("Use '.yt ?' for info"))


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "firebase_auth.json"
firebase_admin.initialize_app()
firebase = firebase.FirebaseApplication('https://notifier-1138.firebaseio.com/', None)


def returnurl(code):
    if str(code).lower() == "long":
        return auth_url_long
    else:
        return auth_url_short


def writefirebase(location, data):
    firebase.put('/', location, data)


def readfirebase(location):
    return firebase.get('/', location)


def deletefirebase(location):
    firebase.delete('/', location)


points = int(readfirebase("points"))
active = bool(readfirebase("active"))
notif_list = readfirebase("notif_list")


def job(mode):
    if mode == "stop":
        active = False
    else:
        points = 10000
        active = True


schedule.every().day.at("03:00").do(job, "stop")

schedule.every().day.at("06:00").do(job, "start")



tick = 1
@loop(seconds=30)
async def time_loop1():
    schedule.run_pending()
    global tick

    print("per 30 sec tick " + str(tick))

    tick += 1


# 30 Minutes
# cost= amount of notif users * 24 * 21
# @loop(minutes=1)
# async def notifications_loop():
#     print("per 1 minute tick " + str(tick))
#     print("1")
#     if active and points > 0:
#         print("2")
#
#         for item in list(reference(url="https://notifier-1138.firebaseio.com/").get(shallow=True).keys()):
#             print("3")
#
#             if not str(item) in known_firebase_variables and str(item) in notif_list:
#                 print("4")
#
#                 for stat in list(stat_types.keys()):
#                     print("5")
#
#                     if not stat == "favorites":
#                         print("6")
#
#                         result = updatestatistic(str(item), stat_types[stat])
#                         if result[0] == "refresh_token_expired":
#                             print("7")
#
#                             await client.get_user(int(item)).send(
#                                 "Your authentication for " + bot_name + " has expired. You can authenticate again by using **.auth**")
#                         elif result[0] == True:
#                             print("8")
#
#                             await client.get_user(int(item)).send(
#                                 "The amount of " + stat + " of one or more videos on your channel has changed")
#                             print(result)
#                             for item in result[1]:
#                                 print(item)
#                                 await client.get_user(int(item)).send(
#                                     "Video id:  " + item[0] + "\nAmount:  " + str(item[1]))


extra = {'client_id': client_id, 'client_secret': client_secret}


def refreshtoken(user_id):
    try:
        client = OAuth2Session(client_id, token=readfirebase(user_id))
        writefirebase(user_id, client.refresh_token(refresh_url, **extra))
    except GoogleAuthError:
        return True


# cost:  3 + 3
def updatestatistic(user_id, mode):
    try:
        creds = credentials.Credentials(
            readfirebase("402344993391640578")["access_token"],
            refresh_token=readfirebase("402344993391640578")["refresh_token"],
            token_uri='https://accounts.google.com/o/oauth2/token',
            client_id=client_id,
            client_secret=client_secret
        )
    except TypeError:
        if refreshtoken(user_id):
            deletefirebase(user_id)
            return ("refresh_token_expired", "")

    youtube = discovery.build("youtube", "v3", credentials=creds)

    req = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=25,
        playlistId=youtube.channels().list(part="snippet,contentDetails,statistics", mine=True).execute()["items"][0][
            "contentDetails"]["relatedPlaylists"]["uploads"]
    ).execute()

    new_list = {}

    for item in req["items"]:
        new_list[item["contentDetails"]["videoId"]] = "a"

    ids = ""
    count = 0

    for key in sorted(list(new_list.keys())):
        temp = ids
        ids = temp + key + ","

        count += 1

    req = youtube.videos().list(
        part="statistics",
        id=ids
    ).execute()

    for (a, b) in zip(req["items"], sorted(list(new_list.keys()))):
        new_list[b] = a["statistics"][mode]

    old_list = readfirebase(mode)

    try:
        if old_list[user_id] == None:
            return
    except KeyError:
        old_list[user_id] = new_list
        writefirebase(mode, old_list)

        print("1")
        return (False, "")


    else:
        countA = 0
        change_list = []
        for i in new_list:

            old = old_list[user_id][sorted(list(old_list[user_id].keys()))[countA]]
            new = new_list[sorted(list(new_list.keys()))[countA]]

            videoid = sorted(list(new_list.keys()))[countA]

            print("old " + str(old))
            print("new" + str(new))

            countA += 1

            if old != new:
                change_list.append([str(videoid), int(new) - int(old)])

        old_list[user_id] = new_list

        writefirebase(mode, old_list)

        if change_list == []:
            return (False, "")

        return (True, change_list)


user_list = []


@client.command(pass_context=True)
async def auth(ctx, code=""):
    if readfirebase(str(ctx.message.author.id)) == None:
        if [str(ctx.message.author.id), "awaiting_code"] in user_list:
            if code.lower() == "cancel":
                await ctx.send("Authentication has been cancelled")
                user_list.remove([str(ctx.message.author.id), "awaiting_code"])
            elif code == "":
                await ctx.send("Please input a code or cancel authentication by using **.auth cancel**")
            else:
                oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)

                try:
                    token = oauth.fetch_token(
                        'https://accounts.google.com/o/oauth2/token',
                        code=code,
                        client_secret=client_secret,
                    )

                    await ctx.send("You have been successfully authenticated")
                    user_list.remove([str(ctx.message.author.id), "awaiting_code"])
                    writefirebase(str(ctx.message.author.id), token)

                except oauth2.rfc6749.errors.InvalidGrantError:
                    await ctx.send(
                        "That code is invalid. Please try again or cancel authentication by using **.auth cancel**")
        else:
            if code.lower() == "cancel":
                await ctx.send("Authentication is not currently in progress")
            else:
                if not isinstance(ctx.channel, discord.channel.DMChannel):
                    await ctx.send(ctx.message.author.mention + " | The authentication link has been sent to you")

                await ctx.author.send(
                    "This is the authentication URL (It's the same every time so you can bookmark it)\n\n" + returnurl(
                        code) + "\n\nInput the code received from the site like this:   **.auth *code***")
                user_list.append([str(ctx.message.author.id), "awaiting_code"])
    elif isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("You have already been authenticated")
    else:
        await ctx.send(ctx.message.author.mention + " | You have already been authenticated")


@client.command(pass_context=True)
async def readfb(ctx, location=""):
    if str(ctx.message.author.id) in owner_ids:
        await ctx.send(readfirebase(location))
    else:
        await ctx.send(ctx.message.author.mention + " | This command is only available to the bot owner(s)")


@client.command(pass_context=True)
async def writefb(ctx, location="", data=""):
    if str(ctx.message.author.id) in owner_ids:
        writefirebase(location, data)
        await ctx.send("The value:  " + data + "\nHas been written to:  " + location)
    else:
        await ctx.send(ctx.message.author.mention + " | This command is only available to the bot owner(s)")


@client.command(pass_context=True)
async def deletefb(ctx, location=""):
    if str(ctx.message.author.id) in owner_ids:
        deletefirebase(location)
        await ctx.send("The value: '" + location + "' has been deleted")
    else:
        await ctx.send(ctx.message.author.mention + " | This command is only available to the bot owner(s)")


@client.command(pass_context=True)
async def stat(ctx, mode=""):
    if mode.lower() in list(stat_types.keys()):

        result = updatestatistic(str(ctx.message.author.id), stat_types[mode])

        if result[0] == "refresh_token_expired":
            await ctx.send(
                ctx.message.author.mention + " | Your authentication has expired. Please authenticate again by using **.auth**")
        elif result[0] == False:
            await ctx.send(
                ctx.message.author.mention + " | That statistic has not changed for any of the videos on your channel")
        else:
            await ctx.send(
                ctx.message.author.mention + " | That statistic has changed for the following videos on your channel:")

            for item in result[1]:
                await ctx.send("Video id:  " + item[0] + "\nAmount:  " + str(item[1]))
    else:
        await ctx.send(
            ctx.message.author.mention + " | That is not a valid statistic. Below are all currently available statistics:\n\nLikes, dislikes, views, comments, favorites\n\nThese are not case sensitive")


@client.command(pass_context=True)
async def notifs(ctx, mode=""):

    if mode == "add":
        notif_list.append(str(ctx.message.author.id))
    elif mode == "remove":
        notif_list.remove(str(ctx.message.author.id))

    writefirebase("notif_list", notif_list)

time_loop1.start()
# notifications_loop.start()
client.run("NzEzMzIwMzEzNDc5MzY0NjE5.Xsi_wg.Eiz9hNO3wIGtJsZ9yBuKYm5SY_E")
