from google import genai
from dotenv import load_dotenv
import os
import logging
import json
from schemas import ExtractedFields

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

model = "gemini-2.0-flash"

def extract_fields_with_gemini(prompt):
    logger.info("Calling Gemini API...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        logger.info("Gemini API call successful.")
        
        # Parse the response and validate it against our schema
        try:
            # Extract JSON from markdown code blocks if present
            response_text = response.text.strip()
            
            # If the response starts with ```json and ends with ```, extract the JSON part
            if response_text.startswith("```json"):
                json_start = response_text.find("```json") + 7
                json_end = response_text.rfind("```")
                if json_end > json_start:
                    response_text = response_text[json_start:json_end].strip()
            elif response_text.startswith("```"):
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                if json_end > json_start:
                    response_text = response_text[json_start:json_end].strip()
            
            # Parse the JSON response
            response_data = json.loads(response_text)
            
            # Convert data types to match schema requirements
            converted_data = {}
            for key, value in response_data.items():
                if value is None:
                    converted_data[key] = "null"
                elif isinstance(value, (int, float)):
                    converted_data[key] = str(value)
                else:
                    converted_data[key] = str(value) if value is not None else "null"
            
            # Validate against our Pydantic schema
            validated_data = ExtractedFields(**converted_data)
            
            # Return as dictionary for JSON serialization
            return validated_data.model_dump()
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Raw response: {response.text[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Failed to validate Gemini response against schema: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error during Gemini extraction: {e}")
        return None