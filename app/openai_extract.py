import os
import logging
import json
from dotenv import load_dotenv
from openai import OpenAI
from schemas import ExtractedFields

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
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
    except Exception as e:
        logger.error(f"Error during OpenAI extraction: {e}")
        return None
    
    logger.info("OpenAI API call successful.")
    
    # Parse and validate the response
    try:
        content = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        response_data = json.loads(content)
        
        # Validate against our Pydantic schema
        validated_data = ExtractedFields(**response_data)
        
        # Return as dictionary for JSON serialization
        return validated_data.model_dump()
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        logger.error(f"Raw response: {response.choices[0].message.content[:200]}...")
        return None
    except Exception as e:
        logger.error(f"Failed to validate OpenAI response against schema: {e}")
        return None