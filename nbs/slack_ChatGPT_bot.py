import credentials

SLACK_BOT_TOKEN = credentials.Slack_Bot_Token
SLACK_APP_TOKEN = credentials.Slack_Bot_App_Token
SLACK_SIGNING_SECRET = credentials.Slack_Signing_Secret
OPENAI_API_KEY  = credentials.openai_api

import os
import openai
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from slack_bolt import App

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN) #, signing_secret=SLACK_SIGNING_SECRET
client = WebClient(SLACK_BOT_TOKEN)

# This gets activated when the bot is tagged in a channel    
@app.event("app_mention")
def handle_message_events(body, logger):
    # Log message
    print(str(body["event"]["text"]).split(">")[1])
    
    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]
    
    # Let thre user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"I'm on it :sunglasses:")
    
    # Check ChatGPT
    openai.api_key = OPENAI_API_KEY

    # old davinci
    #response = openai.Completion.create(
    #    engine="text-davinci-003",
    #    prompt=prompt,
    #    max_tokens=1024,
    #    n=1,
    #    stop=None,
    #    temperature=0.5).choices[0].text
    
    # new ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role' : 'user', 'content' : prompt}],
        temperature=0.5)['choices'][0]['message']['content']
    
    
    # Reply to thread 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Here you go: \n{response}")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()