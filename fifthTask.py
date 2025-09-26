import os
import json
import sys
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# --- Configuration and API Key Loading ---
load_dotenv()

try:
    API_KEY = os.environ["gemini_api_key"]
except KeyError:
    print("Error: The 'gemini_api_key' environment variable is not set.")
    print("Please check your .env file or environment variables.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

def extract_cad_data_to_json(image_path: str, output_filename: str):
    print(f"\n--- Analyzing image: {image_path} ---")
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    try:
        img = Image.open(image_path)

        prompt = [
            """
            You are an expert CAD analyst and programmer specializing in converting 2D drawings into structured vector data readable by software like ezdxf. Your task is to analyze the provided CAD drawing image and extract detailed geometric information for each individual entity.

            **Instructions & Rules:**
            1.  **Coordinate System:** Assume the origin (0, 0) is at the bottom-left corner of the object's primary bounding box. All coordinates must be relative to this origin.
            2.  **Output Format:** Your response MUST be a single, clean JSON object. Do not include any explanatory text, comments, or markdown formatting like ```json.
            3.  **Entity Schema:** The JSON object must have a single root key "entities", which is a list of objects. Each object in the list represents a single geometric entity and must have two keys: "type" and "params".
            4.  **Parameter Extraction:** Infer the geometric parameters (coordinates, radii, angles, etc.) as precisely as possible from the visual information and dimensions in the drawing. Angles are in degrees.

            **JSON Schema and Examples:**

            {
              "entities": [
                {
                  "type": "LINE",
                  "params": {
                    "start_point": [x1, y1],
                    "end_point": [x2, y2]
                  }
                },
                {
                  "type": "CIRCLE",
                  "params": {
                    "center": [cx, cy],
                    "radius": r
                  }
                },
                {
                  "type": "ARC",
                  "params": {
                    "center": [cx, cy],
                    "radius": r,
                    "start_angle": angle1,
                    "end_angle": angle2
                  }
                },
                {
                  "type": "ANGULAR_DIMENSION",
                  "params": {
                    "center": [x, y],
                    "radius": r,
                    "start_angle": angle1,
                    "end_angle": angle2,
                    "distance": d,
                    "dimstyle": "EZ_CURVED"
                  }
                },
              ]
            }

            Now, analyze the attached image and generate the JSON output based on these instructions.
            """,
            img
        ]

        response = model.generate_content(prompt)
        
        raw_text = response.text
        json_str = raw_text

        if '```json' in raw_text:
            json_start = raw_text.find('```json') + 7
            json_end = raw_text.rfind('```')
            json_str = raw_text[json_start:json_end].strip()

        data = json.loads(json_str)
        
        # Save and print the result
        with open(output_filename, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Successfully extracted CAD data to {output_filename}")
        print("--- Generated JSON ---")
        print(json.dumps(data, indent=4))

    except json.JSONDecodeError as e:
        print(f"\n--- ERROR: Failed to decode JSON from model response ---")
        print(f"Error details: {e}")
        print("\n--- Raw Response Text ---")
        print(response.text)
        print("--------------------------")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    image_file = r"D:\AutoLab\cad_image\shape.jpg"
    output_file = "fifthTask.json"
    
    extract_cad_data_to_json(image_file, output_file)