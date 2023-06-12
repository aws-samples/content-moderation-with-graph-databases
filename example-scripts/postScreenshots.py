import json
import random
import requests
import sys
import boto3


#### Sample code to upload a screenshot from the local directory to S3 

screenshotPath = "screenshots"
def main(bucket,doGameID,doPlayerID,doScreenshots):
	### Pick an image 
	listSSNeg=['nazi.jpg']
	listSSPos=['corridor.jpg']
	listSS=listSSNeg + listSSPos

	if doScreenshots == '0':
		selectedSS=random.choice(listSS)
	elif doScreenshots =="POSITIVE":
		selectedSS=random.choice(listSSPos)	
	elif doScreenshots =="NEGATIVE":
		selectedSS=random.choice(listSSNeg)
	else:
		selectedSS=doScreenshots
	postS3(doGameID,doPlayerID,selectedSS,bucket)


def postS3(gameid,playerid,screenshotFile,bucket):
	### Post to S3 with the filename as GAMEID - PLAYERID - SCREENSHOT NAME 
	rndNumber=random.randint(0,1000)
	keyChoice=str(gameid) + "-" + str(playerid) + "-" + screenshotFile 
	inputFile=screenshotPath + "/" + screenshotFile
	client = boto3.client('s3')
	s3response=client.upload_file(
	Bucket=bucket,
	Key=keyChoice,
	Filename=inputFile
	)
	print ("Uploading to S3 as file: " + keyChoice)

    


if __name__ == "__main__":
	
	try:
		doBucket=sys.argv[1]
		doGameID=sys.argv[2]
		doPlayerID=sys.argv[3]
		doScreenshot=sys.argv[4]
		main(doBucket,doGameID,doPlayerID,doScreenshot)

	except:
		print ("Please ensure the bucket, game ID, player ID and a path to your screenshot is entered. Enter '0' for a random screenshot, or 'NEGATIVE'/'POSITIVE' ") 
				


