from __future__ import print_function
import json
import base64
import json
import logging
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
logger = logging.getLogger(__name__)
import requests
import os

### Function to read from the kinesis stream the chat data. 
### It will then call the Comprehend engine to detect negative sentiment 

def lambda_handler(event, context):
    for record in event['Records']:
       #Kinesis data is base64 encoded so decode here
       base64record=record["kinesis"]["data"]
       payload=base64.b64decode(base64record)
       decodedpayload=payload.decode('UTF-8')
       # Load the JSON object  
       print ("Starting Sentiment Analysis")
       print ("Input: " + str(decodedpayload))
       jsonInput=json.loads(decodedpayload);
       # the chat data is contained in the "data" field 
       returnedSentiment=analyzetext(jsonInput["data"])

       API_ENDPOINT = os.environ['API_ENDPOINT']
       # if we see negative sentiment pass it to the API endpoint to record the abuse 
       if returnedSentiment == "NEGATIVE":
           print ("NEGATIVE SENTIMENT DETECTED - Game ID:" + jsonInput["gameid"] + " Username: " + jsonInput["playerid"] + " Type: " + jsonInput["type"]);
           httpcall=requests.put(API_ENDPOINT + "/recordAbuse",data={"gameid": jsonInput["gameid"], "playerid":jsonInput["playerid"] , "abusetype":jsonInput["type"], "abusecontent":jsonInput["data"]}, timeout=30)
           print (httpcall)    
           print (httpcall.content)
       else:
           print("Positive sentiment, ending")

def analyzetext(inputText):
    # call the comprehend library 
    comp_detect = ComprehendDetect(boto3.client('comprehend'))
    if len(inputText) < 2:
        inputText ="no text"
    print ("Analyzing Sentiment of speech")
    # use the ComprehendDetect Class
    sentiment=comp_detect.detect_sentiment(inputText,"en")
    print(f"Sentiment detected: {sentiment['Sentiment']}")
    return sentiment['Sentiment']; 

    

# Prebuilt class to use Comprehend 
class ComprehendDetect:
    """Encapsulates Comprehend detection functions."""
    def __init__(self, comprehend_client):
        """
        :param comprehend_client: A Boto3 Comprehend client.
        """
        self.comprehend_client = comprehend_client


    def detect_languages(self, text):
        """
        Detects languages used in a document.

        :param text: The document to inspect.
        :return: The list of languages along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_dominant_language(Text=text)
            languages = response['Languages']
            logger.info("Detected %s languages.", len(languages))
        except ClientError:
            logger.exception("Couldn't detect languages.")
            raise
        else:
            return languages

    def detect_entities(self, text, language_code):
        """
        Detects entities in a document. Entities can be things like people and places
        or other common terms.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The list of entities along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_entities(
                Text=text, LanguageCode=language_code)
            entities = response['Entities']
            logger.info("Detected %s entities.", len(entities))
        except ClientError:
            logger.exception("Couldn't detect entities.")
            raise
        else:
            return entities

    def detect_key_phrases(self, text, language_code):
        """
        Detects key phrases in a document. A key phrase is typically a noun and its
        modifiers.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The list of key phrases along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_key_phrases(
                Text=text, LanguageCode=language_code)
            phrases = response['KeyPhrases']
            logger.info("Detected %s phrases.", len(phrases))
        except ClientError:
            logger.exception("Couldn't detect phrases.")
            raise
        else:
            return phrases

    def detect_pii(self, text, language_code):
        """
        Detects personally identifiable information (PII) in a document. PII can be
        things like names, account numbers, or addresses.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The list of PII entities along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_pii_entities(
                Text=text, LanguageCode=language_code)
            entities = response['Entities']
            logger.info("Detected %s PII entities.", len(entities))
        except ClientError:
            logger.exception("Couldn't detect PII entities.")
            raise
        else:
            return entities

    def detect_sentiment(self, text, language_code):
        """
        Detects the overall sentiment expressed in a document. Sentiment can
        be positive, negative, neutral, or a mixture.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The sentiments along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=text, LanguageCode=language_code)
            logger.info("Detected primary sentiment %s.", response['Sentiment'])
        except ClientError:
            logger.exception("Couldn't detect sentiment.")
            raise
        else:
            return response

    def detect_syntax(self, text, language_code):
        """
        Detects syntactical elements of a document. Syntax tokens are portions of
        text along with their use as parts of speech, such as nouns, verbs, and
        interjections.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The list of syntax tokens along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_syntax(
                Text=text, LanguageCode=language_code)
            tokens = response['SyntaxTokens']
            logger.info("Detected %s syntax tokens.", len(tokens))
        except ClientError:
            logger.exception("Couldn't detect syntax.")
            raise
        else:
            return tokens
            
            
