import os
import logging
import json
from mistralai import Mistral
from dotenv import load_dotenv
from schemas import ExtractedFields

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

logger.info("Starting Mistral extraction...")

client = Mistral(api_key=MISTRAL_API_KEY)

def extract_fields_with_mistral(prompt):
    logger.info("Calling Mistral API...")    
    try:
        response = client.chat.complete(
            model="mistral-large-latest", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
    except Exception as e:
        logger.error(f"Error during Mistral extraction: {e}")
        return None
    
    logger.info("Mistral API call successful.")
    
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
        logger.error(f"Failed to parse Mistral response as JSON: {e}")
        logger.error(f"Raw response: {response.choices[0].message.content[:200]}...")
        return None
    except Exception as e:
        logger.error(f"Failed to validate Mistral response against schema: {e}")
        return None