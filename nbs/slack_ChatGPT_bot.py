import credentials

SLACK_BOT_TOKEN = credentials.Slack_Bot_Token
SLACK_APP_TOKEN = credentials.Slack_Bot_App_Token
SLACK_SIGNING_SECRET = credentials.Slack_Signing_Secret
OPENAI_API_KEY  = credentials.openai_api

import os

import openai
openai.api_key = OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = credentials.openai_api

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from slack_bolt import App

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN) #, signing_secret=SLACK_SIGNING_SECRET
client = WebClient(SLACK_BOT_TOKEN)

# This gets activated when the bot is tagged in a channel    
@app.event("app_mention")
def handle_message_events(body, logger):

    # source
    # https://medium.com/@alexandre.tkint/integrate-openais-chatgpt-within-slack-a-step-by-step-approach-bea43400d311

    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1].strip()
    print(prompt)
    
    # Let thre user know that we are busy with the request 
    #response = client.chat_postMessage(channel=body["event"]["channel"], 
    #                                   thread_ts=body["event"]["event_ts"],
    #                                   text=f"I'm on it :sunglasses:")
    
    # OpenAI API response
    #response = openai.ChatCompletion.create(
    #    model="gpt-3.5-turbo",
    #    messages=[{'role' : 'user', 'content' : prompt}],
    #    temperature=0.35)['choices'][0]['message']['content']
    

    # langchain API response with ConversationHistory
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.35)

    PROMPT_TEMPLATE = """The following is a friendly conversation between a human and an AI. If the AI does not know the answer to a question, it truthfully says it does not know.
    Current conversation:
    {history}
    Human: {input}
    AI:"""

    PROMPT = PromptTemplate(input_variables=["history", "input"], template=PROMPT_TEMPLATE)

    conversation = ConversationChain(llm=llm, prompt = PROMPT, memory=ConversationBufferMemory())
    response = conversation.run(prompt)
    
    # Reply to thread 
    channel = body["event"]["channel"]
    thread_ts = body["event"]["event_ts"]
    client.chat_postMessage(channel=channel, 
                            thread_ts=thread_ts,
                            text=f"{response}") #Here you go 😎\n\n
    
    # retrieve thread history
    
    #result = client.conversations_history(channel=channel)
    #latest_message = result['messages'][0]
    #msg_id = latest_message['client_msg_id']
    #msg_thread_ts = latest_message['thread_ts'] #same as thread_ts

    while True:

        result = client.conversations_replies(channel=channel, ts=thread_ts)
        last_response_in_thread = result['messages'][-1]['text']

        if last_response_in_thread != response:

            response = conversation.run(last_response_in_thread)
            client.chat_postMessage(channel=channel, 
                                    thread_ts=thread_ts,
                                    text=f"{response}")



if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()