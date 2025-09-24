#To run the code, activate vitual env : gemini_env\Scripts\activate

import os
import json
import sys
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

try:
    API_KEY = os.environ["gemini_api_key"]
except KeyError:
    print("Error: The 'gemini_api_key' environment variable is not set.")
    print("Please check your .env file or environment variables.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

import google.generativeai as genai

vision_model = genai.GenerativeModel('gemini-2.5-flash')

def extract_dimensions_to_json(image_path: str, output_filename: str):
  
    print(f"\n--- Analyzing image: {image_path} ---")
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    try:
        img = Image.open(image_path)


        #dimensions_and_entities.json

        # prompt = [
        #     "You are an expert CAD analyst. I need you to carefully analyze the provided image of a mechanical drawing. Your task is to extract and list all dimensions, count the total number of entities (including lines, arcs, and circles, rectangles, arrows etc), and identify the name of each entity present in the drawing. Return the information in JSON format."
        #     "Example 1: {\"dimensions\": [{\"name\": \"Overall Width\", \"value\": \"150mm\"}], \"entity_count\": 12, \"entity_names\": [\"Circile\", \"etc\"]}",
        #     "Example 2: {\"dimensions\": [{\"name\": \"Main Shaft Diameter\", \"value\": \"25.4mm\"}, {\"name\": \"Hole Distance\", \"value\": \"75mm\"}], \"entity_count\": 25, \"entity_names\": [\"lines\", \"arcs\",\"etc\"]}",

        #     "Analyze the attached image and your respose should be solely based on the analysis of the attached image.",
        #     img
        # ]

        #dimensions_and_entities_prompt2.json
        
        prompt = [
            "Hello Gemini! Suppose you are a CAD designer and analyst. "
            "Analyze the attached image and identify all dimensions and entities in it. "
            "Count the total number of entities and list their types (arrows, lines, arcs, circles, rectangles, etc.). "
            "Provide your response strictly in JSON format only, following this structure:",

            "{"
            "\"dimensions\": ["
            "  {\"name\": \"Dimension Name\", \"value\": \"Value with units\"}"
            "],"
            "\"entity_count\": 0,"
            "\"entity_names\": [\"type1\", \"type2\", \"etc\"]"
            "}",

            "Do not include any text outside the JSON. Only output JSON based on the attached image.",
            img
]
        response = vision_model.generate_content(prompt)
        
        # This part cleans the raw response to extract the JSON block
        json_start = response.text.find('```json')
        json_end = response.text.rfind('```')
        
        if json_start != -1 and json_end != -1:
            json_str = response.text[json_start+7:json_end].strip()
            data = json.loads(json_str)
            
            with open(output_filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Successfully saved dimensions to {output_filename}")
            print(json.dumps(data, indent=4))
        else:
            print("Error: Could not find JSON block in the model's response.")
            print("Raw response:")
            print(response.text)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("Raw response was:")
        print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    image_file = "D:\AutoLab\cad_image\Screenshot 2025-08-29 101018.png"
    output_file = "dimensions_and_entities_prompt2.json"
    
    extract_dimensions_to_json(image_file, output_file)