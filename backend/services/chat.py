from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Esto carga las variables del .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gpt_response(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content