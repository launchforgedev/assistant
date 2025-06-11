import speech_recognition as sr
import pyttsx3
import datetime
import pywhatkit
import pyautogui


# Initialize the speech engine

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good morning!")  
    elif hour >= 12 and hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("Hello this is vera how can i help you today?")

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.pause_threshold=1.0
        r.phrase_threshold=0.3
        r.sample_rate = 48000
        r.dynamic_energy_threshold=True
        r.operation_timeout=5
        r.non_speaking_duration=0.5
        r.dynamic_energy_adjustment=2
        r.energy_threshold=4000
        r.phrase_time_limit = 10
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-us")
            print(f"User said: {query}\n")
        except Exception as e:
            print("Say that again please...")
            return "none"
        return query.lower()

if __name__ == "__main__":
    wishMe()
    
    while True:
        query = takecommand()

        # Perform tasks based on the query
        if 'open' in query:
            app_name=query.replace('open','')
            speak('opening....')
            pyautogui.press('super')
            pyautogui.typewrite(app_name)
            pyautogui.sleep(0.7)
            pyautogui.press('enter')
        elif 'close' in query:
            pyautogui.hotkey('alt','f4')
            speak('Done sir.....')
        elif 'play' in query:
            songname=query.replace('play','')
            speak('sure sir playing'+songname)
            pywhatkit.playonyt(songname)
            
        elif 'screenshot' in query:
            im1=pyautogui.screenshot()
            im2=pyautogui.screenshot('img.png')
        elif 'switch tab' in query:
            pyautogui.hotkey('ctrl','tab')
        elif 'search' in query:
            his=query.replace('search','')
            pywhatkit.search(his)
        elif 'sleep' in query:
            speak('sure sir but u can wake me up anytime' )
            sleep_mode=True
        
            
            