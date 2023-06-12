import random
import sys
import boto3
# Sample script to post audio files to S3 bucket for analysis 

# define the path to your audio files 
audioPath = "audio"
def main(bucket,doGameID,doPlayerID,doComment):
	# some pre-canned audio files 
	listAudioNeg=['i_hate_you_loser.mp3','get_off_game.mp3']
	listAudioPos=['that_was_an_amazing_shot.mp3','capture_the_flag.mp3']
	listAudio=listAudioNeg + listAudioPos

	# determine whether to use a random audio file or a user defined one 
	if doComment == '0':
		selectedAudio=random.choice(listAudio)
	elif doComment =="POSITIVE":
		selectedAudio=random.choice(listAudioPos)	
	elif doComment =="NEGATIVE":
		selectedAudio=random.choice(listAudioNeg)
	else:
		selectedAudio=doComment
	postS3(bucket,doGameID,doPlayerID,selectedAudio)

# Upload audio file to an S3 bucket with the playerID and gameID in the filename 
def postS3(bucket,gameid,playerid,audioFile):
	rndNumber=random.randint(0,1000)
	keyChoice=str(gameid) + "-" + str(playerid) + "-" + audioFile + str(rndNumber) + ".mp3"
	inputFile=audioPath + "/" + audioFile
	client = boto3.client('s3')
	s3response=client.upload_file(
	Bucket=bucket,
	Key=keyChoice,
	Filename=inputFile
	)
	print ("Uploading to S3 as file: " + keyChoice)


if __name__ == "__main__":
	
	try:
		bucket=sys.argv[1]
		doGameID=sys.argv[2]
		doPlayerID=sys.argv[3]
		doComment=sys.argv[4]
		main(bucket,doGameID,doPlayerID,doComment)
		
	except:
		print ("Please ensure the bucket, game ID, player ID and a path to your audio is entered. Enter '0' for a random audio, or 'NEGATIVE'/'POSITIVE'. ")
	

				


