import base64
import json
import logging
import os
import time
from datetime import datetime
import pytz
import aiohttp  # Make sure to import aiohttp

# Get the current date and time for Texas, US (Central Time Zone)
texas_timezone = pytz.timezone('US/Central')
texas_time = datetime.now(texas_timezone)

# Format the date and time
formatted_time = texas_time.strftime("%d/%m/%y %I:%M%p")
# import openai

AI_COMPLETION_MODEL = os.getenv("AI_COMPLETION_MODEL", "gpt-3.5-turbo")
LANGUAGE = os.getenv("LANGUAGE", "en")
VF_KEY = os.getenv("VF_KEY", "")
INITIAL_PROMPT = """Your name is XXXXX, and you are an assistant tasked with answering questions about XXXX. Your primary objective is to manage and respond to 80% of the repetitive queries users may have regarding XXXX. Your role is to provide detailed and accurate information about the strategies, methods, and guide customers to find the best answer for their needs. You are provided with transcript from more than 2000 Podcast Hosted by XXXX. Your task is to analyze the given context and answer user's questions. You need to sift through the information provided, determine the relevance, and use it to answer the question appropriately. If the context provided doesn't have the required information, respond with: "Sorry, I don't know the answer to that question. Can you provide more information to help me understand it better?" Use this exact phrase and refrain from providing information not present in the given context, such as phone numbers or website links not explicitly provided.. Consider yourself as part of the XXXX team, and use collective pronouns like "us," "we," "our," when speaking about the business. Strive to provide relevant and concise responses to user queries, with most answers fitting within one or two sentences. Avoid ending your messages with follow-on questions like "Let me know if I can help with anything else" or "Do you have any other questions?". Instead, direct your responses to addressing the user's query and provide the necessary links for further navigation. Your responses should be well-formatted into paragraphs. Avoid using a large block of text or bullet points to format your answers. If the context provided doesn't have the required information to answer the question, respond with: "Sorry, I don't know the answer to that question. Can you provide more information to help me understand it better?" Use this exact phrase and refrain from providing information not present in the given context, such as phone numbers or website links not explicitly provided."""

# import requests

url = "https://general-runtime.voiceflow.com/knowledge-base/query"


headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": VF_KEY
}

async def get_completion(user_prompt, conversation_thus_far):
    if _is_empty(user_prompt):
        raise ValueError("empty user prompt received")
    start_time = time.time()
    question = f"""A user just sent you a message in a chat conversation, try to help him with the informations you know about XXXX.

                    The message : "
                    {user_prompt}
                    "

                    Use a friendly tone in your response, Act like a very kind and helpfull asistant.

                    Do not greet in your response.

                    It is imperative to focus solely on the query at hand without initiating further dialogue."""

    payload = {
        "chunkLimit": 3,
        "synthesis": True,
        "settings": {
            "model": AI_COMPLETION_MODEL,
            "temperature": 0.1,
            "system": INITIAL_PROMPT,
        },
        "question": question
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as res:
            logging.info("get_completion res",res)
            if res.status == 200:
                res_data = await res.json()  # Parse JSON response content to a dict
                if 'output' in res_data:
                    completion = res_data['output']
                    logging.info('%s res: %s', AI_COMPLETION_MODEL, completion)
                else:
                    logging.error("No 'output' key found in the response")
                    completion = None
            else:
                logging.error("Failed to get a successful response")
                completion = None

    return completion   

def _is_empty(user_prompt: str):
    return not user_prompt or user_prompt.isspace()
