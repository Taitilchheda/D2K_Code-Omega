import os
import ast
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time 
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
class GeminiProvider:
    def __init__(self, profile=None, tools=None):
        self.gemini_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = "gemini-1.5-flash"
        if profile and tools:
            self.chat= self.initialize_assistant(profile, tools)
        else:
            self.chat = None

    def generate_response(self, prompt, remove_literals=False):
        completion = self.gemini_client.models.generate_content(model= self.model, contents=prompt)
        if remove_literals:
            output = ast.literal_eval(completion.text)
        else:
            output = completion.text
        return output

    def generate_json_response(self, prompt, response_schema=None, markdown=False, file=None):
        while True:
            try:
                if markdown:
                    generation_config= types.GenerateContentConfig()
                elif response_schema is None:
                    generation_config= types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.5
                    )
                else:
                    generation_config= types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema = response_schema,
                        temperature=0.5
                    )
                if file is not None:
                    completion = self.gemini_client.models.generate_content(
                        model = self.model,
                        contents=[types.Part.from_uri(file_uri=file.uri, mime_type=file.mime_type), prompt],
                        config=generation_config,
                    )
                else:
                    completion = self.gemini_client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=generation_config,
                    )
                if markdown:
                    return completion.text
                output = ast.literal_eval(completion.text)
                return output
            except Exception as e:
                print("Invalid JSON response, retrying in 10 seconds...")
                time.sleep(3)

    def upload_file(self, file_path, mime_type="video/mp4"):
        print("Uploading file...")
        file = self.gemini_client.files.upload(path=file_path, config={"mime_type": mime_type})
        print(f"Completed upload: {file.uri}.\nProcessing file...")
        while file.state == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            file = self.gemini_client.files.get(name=file.name)
        if file.state == "FAILED":
            raise ValueError(file.state)
        print(f"\nFile processing complete: {file.state}")
        return file
    
    def delete_file(self, file):
        print("Deleting file...")
        return self.gemini_client.files.delete(name=file.name)
    
    def explain_two_image(self, prompt, image1_path, image2_path):
        with open(image1_path, 'rb') as f:
            image1_bytes = f.read()
        with open(image2_path, 'rb') as f:
            image2_bytes = f.read()

        completion = self.gemini_client.models.generate_content(
            model= "gemini-1.5-flash",
            contents=[prompt, types.Part.from_bytes(data=image1_bytes, mime_type=os.path.splitext(image1_path)[1] ), types.Part.from_bytes(data=image2_bytes, mime_type=os.path.splitext(image2_path)[1] ), prompt],
        )
        return completion.text
    
    def initialize_assistant(self, profile, tools):
        self.chat = self.gemini_client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=f"You are ISSAC, a helpful assistant for the website Solo Leveling. Use the functions provided to you to answer user's question about the Solo Leveling platform. User Profile: {profile}",
                tools=tools,
                automatic_function_calling=True,
            )
        )
        return self.chat
    
    def return_chat(self):
        if self.chat is None:
            raise AttributeError("Chat has not been initialized. Call 'initialize_assistant' first.")
        return self.chat