import speech_recognition as sr

def main():
    # speech to text
    r = sr.Recognizer()
    
    # mic access
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 4
    
        print("Listening...")
        audio = r.listen(source)
        
        print("Processing audio...")
        stt = r.recognize_google(audio)
        
        print("You said: ", stt)
        
main()