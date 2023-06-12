import boto3
import random
import requests
import os
### Function to recieve event from S3 Bucket when a new screenshot is uploaded 
### Screenshot file name should be GAMEID - PLAYERID - SCREENSHOTNAME

def lambda_handler(event, context):
    for record in event['Records']:
        ### START IMAGE MODERATION 
        ### Obtain the object key, split out gameid, playerid and screenshot name 
        randomnumber=random.randint(0,900000);
        bucketname=record["s3"]["bucket"]["name"]; 
        objectname=record["s3"]["object"]["key"]; 
        print ("Starting Image Moderation")
        splitobject=objectname.split("-");
        gameid=splitobject[0];
        playerid=splitobject[1]; 
        print ("Game ID: " + gameid + " Player ID: " + playerid + " Screenshot: " +  objectname)

        #### Pass image to Rekognition 
        rek_client = boto3.client('rekognition')

        jobname="screenshot" + str(randomnumber);
        image_file(jobname, bucketname, objectname, rek_client,gameid,playerid)
        
## Function takes the required file from S3 and passes it to Rekognition         
def image_file(job_name, bucketname, file_uri, rek_client,gameid,playerid):
    response=rek_client.detect_moderation_labels(
        Image={
            'S3Object': {
                'Bucket': bucketname,
                'Name': file_uri
                }
            }
    )
    try:
        ## Only takes the first Moderaiton label
        labelName=response["ModerationLabels"][0]["Name"]
        parentName=response["ModerationLabels"][0]["ParentName"]
    except:
        labelName=""
        parentName=""
    
    if labelName:
        #### If detects moderation event call the API Gateway to record the abusive content 
        print ("Moderation Event: " + labelName + " / " + parentName )
        labelString=labelName + " / " + parentName
        API_ENDPOINT = os.environ['API_ENDPOINT']

        httpcall=requests.put(API_ENDPOINT + "/recordAbuse",data={"gameid": gameid, "playerid":playerid , "abusetype":"screenshot", "abusecontent":labelString})

    else:
        print ("No moderation event detected")
