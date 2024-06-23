import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import subprocess as sp
import google.generativeai as genai
import os
from googletrans import Translator
from ratelimit import limits, sleep_and_retry
from google.cloud import translate_v2 as translate

# Configure Gemini API
os.environ["API_KEY"] = "AIzaSyC36Q_f62Y5cUTZrRk7jO0lJvg-MIrFEVA"  # Replace with your actual API key
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Paths for applications
paths = {
    'notepad': "C:\\Windows\\System32\\notepad.exe",
    'calculator': "C:\\Windows\\System32\\calc.exe",
    'files': "C:\\Windows\\explorer.exe",
    'control': "C:\\Windows\\System32\\control.exe",
}

# Initialize text-to-speech engine
engine = pyttsx3.init()


# Function to speak text
def speak(text, language="en"):
    # Set language for speech synthesis
    voices = engine.getProperty('voices')
    if language == "en":
        engine.setProperty('voice', voices[0].id)  # English
    elif language == "es":
        engine.setProperty('voice', voices[1].id)  # Spanish
    elif language == "fr":
        engine.setProperty('voice', voices[2].id)  # French
    elif language == "hi":
        engine.setProperty('voice', voices[3].id)  # Hindi
    elif language == "te":
        engine.setProperty('voice', voices[4].id)  # Telugu

    engine.say(text)
    engine.runAndWait()

# Function to listen for voice commands
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("You Said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return ""

# Function to greet the user
def greet():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
        print("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
        print("Good Afternoon!")
    else:
        speak("Good Evening!")
        print("Good Evening!")
    speak("How can I assist you?")
    print("How can I assist you?")

# Function to open applications
def open_application(app_name):
    if app_name in paths:
        sp.Popen(paths[app_name], shell=True)
        speak(f"Opening {app_name}")
    else:
        speak(f"Sorry, I don't have access to open {app_name}")

@sleep_and_retry
@limits(calls=1, period=2)  # Limit to 5 requests per second
# Function to translate text
def translate_text(text, target_language="en"):
    """Translates text using the googletrans library."""
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

def save_response_to_file(response_text, filename="gemini_responses.txt"):
    """Saves the response text to a file at the specified path."""
    try:
        # Create the full path to the file
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop") # Get the path to your Desktop
        full_file_path = os.path.join("D:/Personal Bot", filename) # Combine Desktop path and filename

        with open(full_file_path, "a", encoding="utf-8") as file:
            file.write(response_text + "\n\n")
        print(f"Response saved to {full_file_path}")
    except Exception as e:
        print(f"Error saving response to file: {e}")

# Main function to handle voice commands and responses
def main():
    greet()
    output_language = "en"  # Default output language

    while True:
        text = listen().lower()

        # Handle specific commands
        if "youtube" in text:
            video_url = "https://www.youtube.com/"
            webbrowser.open(video_url)
            speak("Opening YouTube.")
        elif "tell me today's news" in text:
            news_url = "https://news.google.com/"
            webbrowser.open(news_url)
            speak("Opening Google News.")
        elif "open chat gpt" in text:
            gpt_url = "https://chat.openai.com/"
            webbrowser.open(gpt_url)
            speak("Opening ChatGPT.")
        elif "open google" in text:
            web_url = "https://www.google.com/"
            webbrowser.open(web_url)
            speak("Opening Google.")
        elif "open mail 1" in text:
            mail1_url = "https://mail.google.com/mail/u/0/#inbox"
            webbrowser.open(mail1_url)
            speak("Opening your primary Gmail inbox.")
        elif "open mail 2" in text:
            mail2_url = "https://mail.google.com/mail/u/0/#inbox"
            webbrowser.open(mail2_url)
            speak("Opening your primary Gmail inbox.")
        elif "open classrooms" in text:
            class_url = "https://classroom.google.com/h"
            webbrowser.open(class_url)
            speak("Opening Google Classroom.")
        elif "open weather" in text:
            weather_url = "https://www.accuweather.com/en/us/santa-rosa/95401/weather-forecast/327139"
            webbrowser.open(weather_url)
            speak("Opening weather forecast.")
        elif "open calculator" in text:
            open_application("calculator")
        elif "open notepad" in text:
            open_application("notepad")
        elif "open files" in text:
            open_application("files")
        elif "open control" in text:
            open_application("control")
        elif "change language to english" in text:
            output_language = "en"
            speak("Output language set to English.", output_language)
        elif "change language to spanish" in text:
            output_language = "es"
            speak("Output language set to Spanish.", output_language)
        elif "change language to french" in text:
            output_language = "fr"
            speak("Output language set to French.", output_language)
        elif "change language to hindi" in text:
            output_language = "hi"
            speak("Output language set to Hindi.", output_language)
        elif "change language to telugu" in text:
            output_language = "te"
            speak("Output language set to Telugu.", output_language)
        else:
            # Use Gemini to process the input as a question or a request
            response = model.generate_content(text)

            # Check if response contains a valid Part
            if response.candidates[0].content.parts:
                # Print the response in the original language
                print(response.text)  

                # Translate and speak the response
                translated_response = translate_text(response.text, target_language=output_language)
                speak(translated_response, language=output_language)
                # Save the translated response to the file
                save_response_to_file(translated_response)
            else:
                # Handle cases where the response does not have a valid Part (e.g., safety blocked)
                print("The response does not contain a valid Part. Check the `candidate.safety_ratings` or adjust the model settings.")
                speak("I'm sorry, I can't answer that question right now. Please try again.", language=output_language)
                speak("Do you have any other requests?", language=output_language)
                continue_response = listen().lower()
                if "no" in continue_response:
                    break

if __name__ == "__main__":
    main()
