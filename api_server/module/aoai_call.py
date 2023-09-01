import os

import httpx
import openai
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

from module import prompt_template

load_dotenv()
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")


async def img_gen(query):
    openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION_IMG")
    prompt = prompt_template.return_prompt('imgGen')
    prompt = prompt.format(query=query)

    response = openai.Image.create(
        prompt=prompt,
        size='512x512',
        n=1
    )

    image_url = response["data"][0]["url"]

    return image_url


async def img_to_storage(blob_service_client, container_name, filename, image_url):
    response = httpx.get(image_url)
    img = Image.open(BytesIO(response.content))

    container_client = blob_service_client.get_container_client(container_name)
    # Upload the file data to the container
    container_client.upload_blob(name=filename, data=img.tobytes(), overwrite=True)


async def img_list_gen(query):
    openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION_CHAT")
    prompt = prompt_template.return_prompt('imgList')
    prompt = prompt.format(query=query)

    message_history = [
        # {"role":"system","content":"You are an AI assistant that helps people find information."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = openai.ChatCompletion.create(
            engine="gpt-35-default",
            messages=message_history,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)

        msg = response["choices"][0]["message"]["content"]
    except Exception as e:
        return ""

    return msg
