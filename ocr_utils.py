from PIL import Image
import pytesseract
import re

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image)

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
            # Use the *last* group that matched (to support optional prefixes)
            result[key] = float(match.groups()[-1])
    return result

