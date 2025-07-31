import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OCR_API_KEY")
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
    fields = {
        "calories": r"calories?\D*(\d+)",
        "protein": r"protein\D*(\d+\.?\d*)",
        "fat": r"total fat\D*(\d+\.?\d*)",
        "carbohydrate": r"total carbohydrates?\D*(\d+\.?\d*)",
        "sugar": r"includes\s*(\d+\.?\d*)\s*g\s*added\s*sugars?",
        "fiber": r"fiber\D*(\d+\.?\d*)",
    }

    result = {}
    for key, pattern in fields.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result[key] = float(match.groups()[-1])
    return result
