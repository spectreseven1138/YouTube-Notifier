import discord
import oauthlib
from discord.ext import commands
import os

from discord.ext.tasks import loop
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

client = commands.Bot(command_prefix=".yt ")

# Static variables
bot_name = "YouTube Bot"
owner_id = "402344993391640578"
admin_ids = ["402344993391640578"]

client_secret = "xHIfKIILzqW2il79LTOcMH6g"
client_id = "736516281309-po1q1islep9oekni2p4fcs9ftm12si68.apps.googleusercontent.com"
redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
scopes = "https://www.googleapis.com/auth/youtube.readonly"

auth_url_short = "https://shorturl.at/fzMNR"
auth_url_long = "https://accounts.google.com/signin/oauth/oauthchooseaccount?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.readonly&response_type=code&state=security_token%3D138r5719ru3e1%26url%3Dhttps%3A%2F%2Foauth2.example.com%2Ftoken&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&client_id=736516281309-po1q1islep9oekni2p4fcs9ftm12si68.apps.googleusercontent.com&o2v=2&as=U1xBmkG7iRxTXeekFevTtg&flowName=GeneralOAuthFlow"


@client.event
async def on_ready():
    print(bot_name + " is now running")
    await client.change_presence(activity=discord.Game("Use '.yt ?' for info"))

tick = 1

@loop(seconds=5)
async def time_loop():
    global tick
    print("tick " + str(tick))
    tick += 1


user_list = []


def returnurl(code):
    if str(code).lower() == "long":
        return auth_url_long
    else:
        return auth_url_short


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@client.command(pass_context=True)
async def auth(ctx, code=""):
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
                    client_secret=client_secret)

                await ctx.send("You have been successfully authenticated")
                user_list.remove([str(ctx.message.author.id), "awaiting_code"])

            except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
                await ctx.send("Code is invalid. Please try again or cancel authentication by using **.auth cancel**")

    else:
        if code.lower() == "cancel":
            await ctx.send("Authentication is not currently in progress")
        else:
            if not isinstance(ctx.channel, discord.channel.DMChannel):
                await ctx.send(ctx.message.author.mention + " | The authentication link has been sent to you")

            await ctx.author.send(
                "This is the authentication URL (It's the same every time so you may bookmark it)\n\n" + returnurl(
                    code) + "\n\nInput the code received from the site like this:   **.auth *code***")
            user_list.append([str(ctx.message.author.id), "awaiting_code"])


client.run("NzEzMzIwMzEzNDc5MzY0NjE5.Xsi_wg.Eiz9hNO3wIGtJsZ9yBuKYm5SY_E")
