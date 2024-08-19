from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha

# Speech engine initilisation
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 = male, 1 = female
activationWord = 'nimbus' # Single word

# Configure browser
# Set the path
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Wolfram Alpha Client
appId = '456QTE-JRT7P9E749'
wolframClient = wolframalpha.Client(appId)

# Variable to store user's name
user_name = None

def speak(text, rate = 120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
    

def parseCommand():
    listener = sr.Recognizer()
    print('Listening for a command')
    
    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)
        
    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'The input speech was: {query}')
    except Exception as exception:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        print(exception)
        return 'None'
    
    return query

def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No wikipedia result')
        return 'No result received'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.option[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframAlpha(query = ''):
    response = wolframClient.query(query)
    
    # @sucess: Wolfram Alpha was able to resolve the query
    # #numpods: Number of results returned
    # pod: List of results. This can also contain subpods
    if response['@success'] == 'false':
        return 'Could not computer'
    
    # Query resolved
    else:
        result = ''
        # Question
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        # May contain the answer, has the highest confidence value
        # if it's primary, or has the tile of result or definition, then it's the official result
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Get the result
            result = listOrDict(pod1['subpod'])
            # Remove the bracketed section
            return result.split('(')[0]
        else:
            question = listOrDict(pod0['subpod'])
            # Remove the bracketed section
            return question.split('(')[0]
            # Search wikipedia instead
            speak('Computation failed. Querying universal databank.')
            search_wikipedia(question)
            
def confirm_name():
    speak('Is that correct? Say yes or no.')
    response = parseCommand().lower()
    return response

# Main loop
if __name__ == '__main__':
    speak('All systems nominal, I am nimbus, a speech recognition LLM')
    
    while True:
        # Parse as a list
        query = parseCommand().lower().split()
        
        if query[0] == activationWord:
            query.pop(0)
            
            # List commands

            if query[0] == 'say':
                if 'hello' in query:
                    speak('Greetings, to you.') 
                else:
                    query.pop(0) # Remove say
                    speech = ' '.join(query)
                    speak(speech)
                    
            if query[0] == 'what' and query[1] == 'is' and query[2] == 'my' and query[3] == 'name':
                if user_name is not None:
                    speak(f'Your name is {user_name}')
                else:
                    speak('I do not know your name yet. Please tell me your name first.')
                    
            if query[0] == 'set' and query[1] == 'my' and query[2] == 'name' and query[3] == 'to':
                new_name = ' '.join(query[4:])
                speak(f'You want to set your name to {new_name}.')
                
                if confirm_name() == 'yes':
                    user_name = new_name
                    speak(f'Your name has been set to {user_name}')
                else:
                    speak('Let me know your name again. You can just say your name directly.')
                    while True:
                        new_name_direct = parseCommand().lower()
                        if new_name_direct:
                            user_name = new_name_direct
                            speak(f'Your name has been set to {user_name}')
                            break
                     
            # Navigation
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening...')
                query = ' '.join(query[2:])
                webbrowser.get('chrome').open_new(query)
                
            # Wikipedia
            if query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Querying the universal databank.')
                speak(search_wikipedia(query))
                
            # Wolfram Alpha
            if query[0] == 'compute' or query[0] == 'computer':
                query = ' '.join(query[1:])
                speak('computing')
                try:
                    result = search_wolframAlpha(query)
                    speak(result)
                except:
                    speak('Unable to compute')
                    
            # Note taking
            if query[0] == 'log':
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(newNote)
                speak('Note written')
                
            if query[0] == 'exit':
                speak('Goodbye')
                break