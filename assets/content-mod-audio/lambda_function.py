import json
import os 
import time
import boto3
import random
import requests
### Function to recieve event from S3 Bucket when a new audio file is is uploaded 
### Audio file name should be GAMEID - PLAYERID - AUDIO NAME
### After the audio is transcribed it will then be sent back to the Kinesis stream for chat files 

def lambda_handler(event, context):
    for record in event['Records']:

        ## obtain the S3 object 
        randomnumber=random.randint(0,900000);
        bucketname=record["s3"]["bucket"]["name"]; 
        objectname=record["s3"]["object"]["key"]; 
        
        splitobject=objectname.split("-");
        gameid=splitobject[0];
        username=splitobject[1]; 
        
        
        s3url="s3://" + bucketname + "/" + objectname;
        print ("Starting Transcribe:")
        print ("Game ID: " + gameid + ". Username: " + username); 
        print (s3url); 
        ### transcribe the audio file 
        transcribe_client = boto3.client('transcribe')

        jobname="translatejob" + str(randomnumber);
        output=transcribe_file(jobname, s3url, transcribe_client)
        print ("Transcription: " + output); 
        
        ### pass the object back to kinesis for chat analysis 
        jsonObject ={
            "gameid" : gameid,
            "playerid" : username,
            "type" : "audio",
            "data": output
        }
        passToKinesis=json.dumps(jsonObject)
        KINESIS_STREAM = os.environ['KINESIS_STREAM']

        kinesisClient=boto3.client('kinesis');
        kinesisResponse=kinesisClient.put_record(
            StreamName=KINESIS_STREAM,
            Data=passToKinesis,
            PartitionKey='1'
            );
        print ("Passing to translation back into the Chat Kinesis Stream")    
        print (kinesisResponse); 
        
def transcribe_file(job_name, file_uri, transcribe_client):

    ### Call the AWS Transcribe service and wiat for a response 
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            if job_status == 'COMPLETED':
                transcript=requests.get(job['TranscriptionJob']['Transcript']['TranscriptFileUri']).json()
                
                return (transcript["results"]["transcripts"][0]["transcript"])
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)





