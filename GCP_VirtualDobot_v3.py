"""Author: Sameer Kesava"""

from google import auth #for authorization
import os
import time
import dialogflow #Google Natural Language Processing API


json_file = input('Enter path to the json credentials file: ')

#Authorization to login to the project chosen during gcloud init
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = json_file

credentials, project = auth.default()

#Creating a session using the credentials
session_client =  dialogflow.SessionsClient(credentials=credentials)

session_ID = input('Enter a name for session id: ') 

#Final step setting up a session
session = session_client.session_path(project, session_ID)


#Audio Streaming

# Importing module recording, requires installation of sounddevice
from recording_sounddevice import record_stream
# Parameters for recording  
CHUNK = 1024
FORMAT = 'int16' 
CHANNELS = 1 
RATE = 16000

# Creating a threaded object for recording
stream_obj = record_stream(CHUNK, RATE, CHANNELS, FORMAT)
stream_obj.start()


# Defining the audio encoding format to send to the cloud
audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16

# Audio configuration
audio_config = dialogflow.types.InputAudioConfig(audio_encoding = audio_encoding, \
language_code='en', sample_rate_hertz=RATE)



def audio_generator():

    """A generator yielding audio chunks in the StreamingDetectIntent format
        passed to the streaming_detect_intent method of dialogflow"""

    # First message should be of the type below
    query_input = dialogflow.types.QueryInput(audio_config=audio_config)
    yield dialogflow.types.StreamingDetectIntentRequest(session=session, \
                                                               query_input=query_input,\
                                                       single_utterance = True)
    
    while True:
        data = stream_obj.rec()
        yield dialogflow.types.StreamingDetectIntentRequest(input_audio=data, \
                                                           single_utterance = True) 


def coordinate_fn(params):

    """ x, y, z parameters returned from DialogFlow are extracted
        and sent to the move_arm function"""

    coordinates = []
    for i in params:
        coordinates.append(i.number_value)
    virtual_dobot(coordinates)   


def virtual_dobot(coordinates):
    """A virtual dobot function moving the arm to the position dictated.
        Make sure the positions are within the max limits"""
    print('Moving to x = %d, y = %d and z = %d' % (coordinates[0],coordinates[1], coordinates[2]))


try:
    
    while True:    

        requests = audio_generator() #Audio stream generator

        #Sending the streams to the cloud        
        responses = session_client.streaming_detect_intent(requests)
        

        for response in responses:
            print('Intermediate transcript: "{}".'.format(response.recognition_result.transcript))
            # Prints out live speech to text
        
              

        if response.query_result.query_text is not '': 
            #If not silent, run below
            
            if response.query_result.fulfillment_messages[0].text.text[0] == 'STOP':
                # Use 'Close the connection' Intent to end the program
                # Close Dobot connection
                print('Connection Closed. Goodbye!')
                
                break
            
            elif not response.query_result.parameters:             
                # If no parameter is returned like for "Hello, how are you?"
                print(response.query_result)
                
            
            else:
                if len(response.query_result.parameters.get_or_create_list('number-integer').values)!= 3:

                    # If the number of parameters is less than 3
                    print('Please repeat again with sufficient time gap between different parameters')
                    
                
                else:
                    #Passing coordinates to the Dobot to move
                    coordinate_fn(response.query_result.parameters.get_or_create_list('number-integer').values)
                    print(response.query_result)
        
        
        
        time.sleep(1)  


except: # In case there is an error, the stream will be closed.
    #Close Dobot connection
    
    print('Error: Stream Closed')

    

raise SystemExit
