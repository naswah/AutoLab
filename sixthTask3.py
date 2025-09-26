import os
import json
import sys
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import ezdxf

load_dotenv()

try:
    API_KEY = os.environ["gemini_api_key"]
except KeyError:
    print("Error: The 'gemini_api_key' environment variable is not set.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')


def extract_json(image_path: str, output_filename: str):
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

            For an arc, you know that arc always rotates anti clockwise, so for C shaped arc, the start angle is 90 and the end angle is 270. For mirrored C, the start angle is 270 and the end angle is 90. 
            For semi circle(top part) the start angle must be 0 and the end angle should be 180 whereas for bottom half, the start angle should be 180 and the end angle must be 0

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
                }
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

        # Save JSON
        with open(output_filename, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Successfully extracted CAD data to {output_filename}")
        print("--- Generated JSON ---")
        print(json.dumps(data, indent=4))

        # Convert JSON to DXF
        dxf_output_file = output_filename.replace(".json", ".dxf")
        json_to_dxf(data, dxf_output_file)

    except json.JSONDecodeError as e:
        print(f"\n--- ERROR: Failed to decode JSON from model response ---")
        print(f"Error details: {e}")
        print("\n--- Raw Response Text ---")
        print(response.text)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def json_to_dxf(data: dict, dxf_filename: str):

    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()

    for entity in data.get("entities", []):
        type_ = entity.get("type")
        params = entity.get("params", {})

        if type_ == "LINE":
            start = tuple(params.get("start_point", [0, 0]))
            end = tuple(params.get("end_point", [0, 0]))
            msp.add_line(start, end)

        elif type_ == "CIRCLE":
            center = tuple(params.get("center", [0, 0]))
            radius = params.get("radius", 0)
            msp.add_circle(center, radius)

        elif type_ == "ARC":
            center = tuple(params.get("center", [0, 0]))
            radius = params.get("radius", 0)
            start_angle = params.get("start_angle", 0)
            end_angle = params.get("end_angle", 0)
            msp.add_arc(center, radius, start_angle, end_angle)

    doc.saveas(dxf_filename)
    print(f"Successfully converted JSON to DXF: {dxf_filename}")


if __name__ == "__main__":
    image_file = "D:\AutoLab\cad_image\circles.png"
    output_file = "sixthTask3.json"

    extract_json(image_file, output_file)

    #If half of an arc is used, for top left: start angle: 90, end angle is 180, for bottom left: start angle is 180 and end angle is 270
    #for bottom right, the start angle is 270 and end angle is 0 where as for top right the start angle is 0 and the end angle is 90.