import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger.info("Starting OpenAI extraction...")

client = OpenAI(api_key=OPENAI_API_KEY) 

def extract_fields_with_openai(prompt):
    logger.info("Calling OpenAI API...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logger.error(f"Error during OpenAI extraction: {e}")
        return None
    logger.info("OpenAI API call successful.")
    return response.choices[0].message.content