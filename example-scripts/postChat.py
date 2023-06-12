import json
import random
import sys
import boto3


#### Sample code that is able to take input from the CLI and post the chat message to the API Gateway 

def main(streamname,doGameID,doPlayerID,doComment):
	### Determine which phrase to use 
	listPhrasesNeg=['i hate you','you are rubbish at this','you suck','get out of this game you loser']
	listPhrasesPos=['great shot','shoot that way','meet me at the flag','go and kill that guy over there','you are playing really well']
	listPhrases=listPhrasesNeg + listPhrasesPos
	
	if doComment == '0':
		selectedComment=random.choice(listPhrases)
	elif doComment =="POSITIVE":
		selectedComment=random.choice(listPhrasesPos)	
	elif doComment =="NEGATIVE":
		selectedComment=random.choice(listPhrasesNeg)
	else:
		selectedComment=doComment
	print ("Posting Comment: " + selectedComment)
	postKinesis(streamname,doGameID,doPlayerID,selectedComment)


def postKinesis(streamname,gameid,playerid,comment):
	### Post the chat comment and game ID,PlayerID to Kinesis 
	jsonObject ={"gameid" : gameid,"playerid" : playerid, "type" : "chat", "data": comment}
	passToKinesis=json.dumps(jsonObject)
	kinesisClient=boto3.client('kinesis');
	kinesisResponse=kinesisClient.put_record(
            StreamName=streamname,
            Data=passToKinesis,
            PartitionKey='1'
            );
	print ("Posting to Kinesis Stream: " + str(jsonObject)); 


    


if __name__ == "__main__":
	
	try:
		doStream=sys.argv[1]
		doGameID=sys.argv[2]
		doPlayerID=sys.argv[3]
		doComment=sys.argv[4]
		main(doStream,doGameID,doPlayerID,doComment)
		
		
	except:
		print ("Please ensure the stream, game ID, playerID and comment type is selected. For comments you may enter '0' for random, 'NEGATIVE' for a negative comment, 'POSITIVE' for a postive comment, or enter one of your own" )
				


