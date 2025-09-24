#Folder anmed Extracted dims secondTask is created to store all the extracted dimensions of the images.
#To run the code, activate vitual env : gemini_env\Scripts\activate
#ALl the extracted dimensions will be stored in json format, outside the folder(Extracted dims secondTask), I created the folder to manage after execcution

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

vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')

def extract_dimensions_to_json(image_path: str, output_filename: str):
    
    print(f"\n--- Analyzing image: {image_path} ---")
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    try:
        img = Image.open(image_path)
        
        prompt = [
            "You are an expert CAD analyst. Extract all visible dimensions and return them in JSON format. The JSON should have a 'dimensions' key, which is an array of objects. Each object has a 'name' and 'value'."

            "Example 1: {\"dimensions\": [{\"name\": \"Overall Width\", \"value\": \"150mm\"}]}",
            "Example 2: {'dimensions': [{'name': 'Main Shaft Diameter', 'value': '25.4mm'}, {'name': 'Hole Distance', 'value': '75mm'}]}",
            "Example 3: {'dimensions': [{'name': 'Side Plate Thickness', 'value': '0.5in'}, {'name': 'Mounting Hole Radius', 'value': '1/8in'}]}",

            "Analyze the attached image and provide a response in the same format.",
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

# --- Main execution ---
if __name__ == "__main__":
    image_directory = "D:\\AutoLab\\images"
    
    # Images in the directory
    image_files = [os.path.join(image_directory, f) for f in os.listdir(image_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Loop through each image and process it
    for img_path in image_files:
        # Create a unique output filename for each image
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        output_file = f"extracted_dimensions_{base_name}.json"
        
        extract_dimensions_to_json(img_path, output_file)