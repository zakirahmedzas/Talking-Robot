#https://github.com/zakirahmedzas
#DROBAN

import google.generativeai as genai
from gtts import gTTS
import tempfile
import os
import speech_recognition as sr  # For microphone input
import pygame
import RPi.GPIO as GPIO  # For controlling GPIO on Raspberry Pi

# GPIO setup
GPIO.setmode(GPIO.BCM)     
LED_PIN1 = 17
LED_PIN2 = 18# The GPIO pin the LED is connected to
GPIO.setup(LED_PIN1, GPIO.OUT)
GPIO.setup(LED_PIN2, GPIO.OUT)

# Configure the Generative AI API with your API key
genai.configure(api_key="AIzaSyDIWA9NFyzXWOh_fNMer8xC-y5O9HXTVvc")

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to generate AI response with a limit on the length
def generate_ai_response(query, max_length=400):
    """
    Generate AI response for the given query with a limit on the text length.
    """
    response = model.generate_content(query)  # Send request
    ai_text = response.text  # Get AI text
    
    # Truncate the response if it's too long
    if len(ai_text) > max_length:
        ai_text = ai_text[:max_length]  # Truncate to max_length characters
    
    return ai_text

# Function to convert AI response text to speech and play it directly
def speak(text, chunk_size=500):
    """
    Convert the provided text to speech and play it. If the text is too long,
    it will be split into smaller chunks for sequential playback.
    """
    # Create a gTTS object in memory (without saving to a file)
    tts = gTTS(text, lang='en')
    
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file_name = temp_file.name
        tts.save(temp_file_name)  # Save the speech to the temporary file
        
        # Use pygame to directly play the MP3 file (faster than conversion with pydub)
        pygame.mixer.init()  # Initialize pygame mixer
        pygame.mixer.music.load(temp_file_name)
        pygame.mixer.music.play()

        # Wait for playback to finish before removing the file
        while pygame.mixer.music.get_busy():  # Wait until music finishes playing
            pass
        
        # Clean up the temporary file (delete it after use)
        os.remove(temp_file_name)

# Function to listen to microphone input and convert to text
def listen_to_microphone():
    """
    Listen to the microphone input, convert it to text, and return the query.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Listening for your question...")
        GPIO.output(LED_PIN1, GPIO.HIGH)  # Turn on LED while listening (Speech is being 
        GPIO.output(LED_PIN2, GPIO.LOW)# Turn off LED on error
processed)
        audio = recognizer.listen(source)  # Listen for input
                      
    try:
        query = recognizer.recognize_google(audio)  # Convert speech to text
        print(f"You said: {query}")
        GPIO.output(LED_PIN2, GPIO.HIGH)  # Blink LED to indicate recognition
        return query
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        GPIO.output(LED_PIN1, GPIO.LOW)  # Turn off LED if no speech is recognized
        GPIO.output(LED_PIN2, GPIO.LOW)# Turn off LED on error
        return None
    except sr.RequestError:
        print("Sorry, there was an issue with the speech recognition service.")
        GPIO.output(LED_PIN1, GPIO.LOW)
        GPIO.output(LED_PIN2, GPIO.LOW)# Turn off LED on error
        return None

# Main program
if __name__ == "__main__":
    print("Welcome to the AI voice prompt generator!")
    print("Please speak your question (say 'exit' to quit):")
    
    while True:
        user_query = listen_to_microphone()  # Listen for user's voice input
        if user_query is None:
            continue
        
        if 'exit' in user_query.lower():
            print("Goodbye!")
            GPIO.cleanup()  # Clean up GPIO when exiting
            break
        
        try:
            ai_response = generate_ai_response(user_query)  # Generate AI response
            print(f"AI: {ai_response}")
            
            # Convert AI response to speech and play it directly
            speak(ai_response)
        except Exception as e:
            print(f"An error occurred: {e}")
