import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os

engine=pyttsx3.init('sapi5')
voices=engine.getProperty('voices')

engine.setProperty('voice',voices[0].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour=int(datetime.datetime.now().hour)
    if hour>=0 and hour<=12:
        speak("goodmorning!")
    elif hour>12 and hour<=18:
        speak("good afternoon")
    else:
        speak("good evening")
    speak("Namaste")
def takecommand():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        print("listening....")
        r.pause_threshold=1
        audio=r.listen(source)
        try:
            print("recognizing.....")
            query=r.recognize_google(audio,language="en-us")
            print(f"user said:{query}\n")
        except Exception as e:
            print("say that again please")
            return "none"
        return query
if __name__=="__main__":
    wishMe()
    while True:
        query=takecommand().lower()
        if 'wikipedia' in query:
            speak('searching wikipedia....')
            query=query.replace('wikipedia',"")
            results=wikipedia.summary(query,sentences=2)
            speak("according to wikipedia....")
            speak(results)
        elif 'open youtube' in query:
            speak("opening youtube....")
            webbrowser.open('youtube.com')
        elif 'time now' in query:
            strtime=datetime.datetime.now().strftime('%H:%M:%S')
            speak(strtime)
        elif 'play music' in query:
            song_dir="D://music"
            songs=os.listdir(song_dir)
            print(songs)
            os.startfile(os.path.join(song_dir,songs[0]))
            
    

