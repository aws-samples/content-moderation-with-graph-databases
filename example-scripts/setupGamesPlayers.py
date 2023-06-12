from urllib.parse import parse_qs
import random
import requests
import sys

# Script to generate a number of players, games, player->game instances and money transactions 

def main(doReset,doPlayers,doGames,doPPP,doTransactions,endpoint):
	
	print ("Reset: " + str(doReset) + " Players: " + str(doPlayers) + " Games: " + str(doGames) + " PlayerGames: " + str(doPPP) + " Transactions: " + str(doTransactions))
	# Specify a range of inputs 
	range_player_min=10
	range_player_max=30
	range_game_min=100
	range_game_max=120
	
	number_gamelinks=200
	number_transactions=20
	
	### Reset the database 
	if doReset == 1:
		print ("Resetting Neptune DB")
		httpcall=requests.get(endpoint + "/resetNeptune")      
		print (httpcall.content)
	
	### create players 
	if doPlayers == 1:
		for i in range (range_player_min,range_player_max):
			newPlayerId="p" + str(i) 
			createPlayer(newPlayerId)	
	
	# create games 
	if doGames == 1:
		for i in range (range_game_min,range_game_max):
			newGameId="g" + str(i) 
			createGame(newGameId)
	### create the links between players and games 
	if doPPP == 1:
		for i in range (0,number_gamelinks):
			rndPlayer=str(random.randint(range_player_min,range_player_max-1))
			rndGame=str(random.randint(range_game_min,range_game_max-1))
			# Pick an random duration of play, weighted towards longer play 
			durationList=[1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
			randomDuration=random.choices(durationList, weights=(1,1,1,2,2,3,3,4,5,6,10,15,15,15,20,20,20,25,25,25,30))
		
			rndPlayer="p" + str(rndPlayer) 
			rndGame="g" + str(rndGame) 

			playerPlaysGame(rndGame, rndPlayer, randomDuration[0])

	### cash transactions 
	if doTransactions == 1:	
		for i in range (0,number_transactions):
			rndPlayer=str(random.randint(range_player_min,range_player_max-1))
			rndPlayer="p" + str(rndPlayer) 			
			rndTransactionId="t" + str(random.randint(10000,90000))
			rndTransactionValue=str(random.randint(1,20))
			playerTransaction(rndPlayer,rndTransactionValue,rndTransactionId)
		
def createPlayer(playerId):
	print ("Creating player: " + playerId)
	httpcall=requests.put(endpoint + "/createPlayer",data={"playerid": playerId })
	print (httpcall.content)

def createGame(gameId):
	print ("Creating game: " + gameId)
	httpcall=requests.put(endpoint + "/createGame",data={"gameid": gameId })
	print (httpcall.content)

def playerPlaysGame(gameid,playerid,duration):
	duration=str(duration)
	print ("Player " + playerid + " will play in game " + gameid + " for " + duration + "%")
	httpcall=requests.put(endpoint + "/playerPlaysGame",data={"gameid": gameid , "playerid": playerid , "durationPercentage": duration })
	print (httpcall.content)

def playerTransaction(playerid, transactionvalue, transactionid):
	print ("Player " + playerid + " made a transaction: " + transactionid + " for " + transactionvalue + "USD")
	httpcall=requests.put(endpoint + "/playerTransaction",data={"transactionid": transactionid , "playerid": playerid , "transactionvalue": transactionvalue })
	print (httpcall.content)

if __name__ == "__main__":
	
	try:
		endpoint=sys.argv[1]
		doReset=sys.argv[2]
		doPlayers=sys.argv[3]
		doGames=sys.argv[4]
		doPPP=sys.argv[5]
		doTransactions=sys.argv[6]
		print ("Running with defined values")
	except:
		doReset=1
		doPlayers=1
		doGames=1
		doPPP=1		
		doTransactions=1
		print ("Running with random values")
	main(doReset,doPlayers,doGames,doPPP,doTransactions,endpoint)


