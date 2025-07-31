import os
import requests
from PIL import Image
from dotenv import load_dotenv
import re

load_dotenv()
API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

def extract_text_from_image(uploaded_file):
    image_bytes = uploaded_file.read()
    
    response = requests.post(
        OCR_URL,
        files={"filename": image_bytes},
        data={"apikey": API_KEY, "language": "eng"},
    )

    result = response.json()
    try:
        return result["ParsedResults"][0]["ParsedText"]
    except (KeyError, IndexError):
        return ""

def parse_nutrition_info(text):
    def extract_value(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return float(match.group(1)) if match else 0.0

    return {
        "calories": extract_value(r"calories[^\d]*(\d+)"),
        "protein": extract_value(r"protein[^\d]*(\d+(\.\d+)?)"),
        "fat": extract_value(r"fat[^\d]*(\d+(\.\d+)?)"),
        "carbohydrate": extract_value(r"carbohydrate[^\d]*(\d+(\.\d+)?)"),
        "sugar": extract_value(r"sugar[^\d]*(\d+(\.\d+)?)"),
        "fiber": extract_value(r"fiber[^\d]*(\d+(\.\d+)?)"),
    }
