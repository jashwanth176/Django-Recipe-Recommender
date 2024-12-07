from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import json
import logging
from recipes.models import Recipe 
from gtts import gTTS
import base64
import os
import asyncio
import threading

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Configure the Gemini API key
api_key = "AIzaSyBupL0wRBvGL2TPsRZ2RTSwecRF1hq4tBc"
logger.info(f"Using GEMINI_API_KEY: {api_key}")
genai.configure(api_key=api_key)

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

        try:
            # Check if the message contains the command to add a recipe
            if message.lower().startswith("@add recipe"):
                recipe_details = message[len("@add recipe"):].strip()
                title, ingredients, instructions = parse_recipe_details(recipe_details)
                Recipe.objects.create(title=title, ingredients=ingredients, instructions=instructions)
                return JsonResponse({'response': 'Recipe added successfully!'})

            # Use the updated Gemini model to generate a response
            model = genai.GenerativeModel(model_name="gemini-1.5-pro")
            system_prompt = """
            YOU ARE A FRIENDLY AND EXPERT RECIPE RECOMMENDER. YOU SPECIALIZE IN SUGGESTING AND GIVING THE RECIPE.
            ###INSTRUCTIONS###

            - ALWAYS PROVIDE DETAILED, FRIENDLY RESPONSES WITH ONE OR TWO RECOMMENDED DISHES
            - ALWAYS STAY ON TOPIC AND NEVER GO OFF ON OTHER CUISINES OR TOPICS
            - IF INGREDIENTS ARE GIVEN, RECOMMEND RECIPES BASED ON WHAT THE USER HAS
            - IF NO INGREDIENTS OR PREFERENCES ARE GIVEN, SUGGEST POPULAR OR EASY-TO-MAKE INDIAN DISHES
            - MAINTAIN A FRIENDLY TONE
            ONLY WHEN YOU RECIVE THE @add recipe: THEN ONLY ADD THE RECIPE AND NOTHING ELSE OTHERWISE JUST RESPOND WITH THE RECIPE  
            ###ADD RECIPE [THIS IS ONLY FOR ADDING RECIPES, ONLY WHEN YOU RECIVE THE @add recipe: THEN ONLY ADD THE RECIPE AND NOTHING ELSE]###
            IF YOU ARE TOLD TO ADD A RECIPE, THEN ONLY ADD THE RECIPE AND NOTHING ELSE.
            IF YOU WANT TO ADD A RECIPE THEN    @add recipe: Paneer Butter Masala; Paneer, Butter, Tomatoes, Cream, Spices; Fry paneer, make a tomato-based gravy, add cream, and cook with paneer.
            YOU MUST USE THE ABOVE FORMAT.
            """
            full_prompt = f"{system_prompt}\nUser: {message}\nChef:"
            logger.debug(f"Full prompt: {full_prompt}")
            response = model.generate_content(full_prompt)
            chatbot_response = response.text.strip()
            logger.debug(f"Chef response: {chatbot_response}")
            
            # Process the response to convert ** to markdown bold
            processed_response = process_bold_formatting(chatbot_response)
            
            # Generate audio in a separate thread
            thread = threading.Thread(target=generate_audio_async, args=(processed_response, request.session.session_key))
            thread.start()
            
            return JsonResponse({
                'response': processed_response,
                'audio_ready': False
            })
        except Exception as e:
            logger.error("Error generating response: %s", str(e))
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_audio_async(text, session_key):
    tts = gTTS(text=text, lang='en', slow=False)
    filename = f"response_audio_{session_key}.mp3"
    tts.save(filename)
    
    # Update a flag in the session or database to indicate audio is ready
    # For simplicity, we'll use a file-based approach here
    with open(f"audio_ready_{session_key}.txt", "w") as f:
        f.write("ready")

@csrf_exempt
def check_audio_status(request):
    session_key = request.session.session_key
    if os.path.exists(f"audio_ready_{session_key}.txt"):
        os.remove(f"audio_ready_{session_key}.txt")
        return JsonResponse({'audio_ready': True})
    return JsonResponse({'audio_ready': False})

@csrf_exempt
def get_audio(request):
    session_key = request.session.session_key
    filename = f"response_audio_{session_key}.mp3"
    if os.path.exists(filename):
        with open(filename, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        os.remove(filename)
        return JsonResponse({'audio': audio_data})
    return JsonResponse({'error': 'Audio not found'}, status=404)

def generate_audio(text):
    tts = gTTS(text=text, lang='en', slow=False)  # Set slow=False for slightly faster speech
    filename = "response_audio.mp3"
    tts.save(filename)
    
    with open(filename, "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
    
    os.remove(filename)  # Clean up the temporary file
    return audio_data

def parse_recipe_details(details):
    # Simple parser for recipe details
    parts = details.split(';')
    title = parts[0].strip()
    ingredients = parts[1].strip() if len(parts) > 1 else ''
    instructions = parts[2].strip() if len(parts) > 2 else ''
    return title, ingredients, instructions

def process_bold_formatting(text):
    """
    Convert ** bold formatting to HTML bold tags for proper rendering.
    """
    parts = text.split('**')
    for i in range(1, len(parts), 2):
        parts[i] = f'<b>{parts[i]}</b>'
    return ''.join(parts)
