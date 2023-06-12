import base64
from urllib.parse import parse_qs
import datetime
from gremlin_python.process.traversal import Cardinality
import random
import os 

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T

id = T.id
single = Cardinality.single
#### This function acts as the interface to the Neptune database. It is designed to sit behind an API Gateway.
#### It accepts the following paths with the HTTP form data set for the variables:
#### PUT /createGame – requires ‘gameid’ to be set 
#### PUT /createPlayer  - requires ‘playerid’ to be set 
#### PUT /playerPlaysGame – requires ‘playerid’ and ‘gameid’ to be set 
#### PUT /playerTransaction – requires ‘playerid’,’gameid’,’transactionid’ and ‘transactionvalue’
#### PUT /recordAbuse - requires 'playerid','gameid','transactionid','transactionvalue' 
#### GET /resetNeptune

def lambda_handler(event, context):
    # Get the path being requested 
    try:
        rawPath=event["rawPath"]
    except:
        rawPath="missing"
    try:
    # grab the body of the request and decode 
        requestbody=event["body"]
        requestdecode=base64.b64decode(requestbody)
        decodedpayload=requestdecode.decode('UTF-8')
        inputvars=parse_qs(decodedpayload)
    except:
        requestbody="missing"
        inputvars=""
    # direct to the appropriate function 
    if rawPath == '/createGame':
        responsereturn=createGame(inputvars)
    elif rawPath == '/createPlayer':
        responsereturn=createPlayer(inputvars)
    elif rawPath == '/playerPlaysGame':
        responsereturn=playerPlaysGame(inputvars)
    elif rawPath == '/playerTransaction':
        responsereturn=playerTransaction(inputvars)
    elif rawPath == '/resetNeptune':
        responsereturn=clearNeptune(inputvars)
    elif rawPath == '/recordAbuse':
        responsereturn=recordAbuse(inputvars)
    else:
        responsereturn = 'Unknown action'
    
    ## return a response 
    return {
        'statusCode': 200,
        'body': "Response: " + responsereturn
    }

## add a game to the neptune database 
def createGame(inputvars):
    newGameId=inputvars["gameid"][0]    
    g,remoteConn=createNeptune()
    
    try:
        # Add the Game to neptune and record the game ID and timestamp 
        neptuneResponse=g.addV('game').property(id, newGameId).property('gameid',newGameId).property('timestamp',datetime.datetime.now()).next() 
        print(g.V().valueMap().limit(10).toList())
        print(g.V().values('gameid').toList())
        return ("Game Created")
        remoteConn.close()

    except:
        # Neptune query failed 
        return ("Error - game ID either already exists or is in the incorrect format - " + newGameId)
        remoteConn.close()

## create the player 
def createPlayer(inputvars):
    newPlayerId=inputvars["playerid"][0]    
    g,remoteConn=createNeptune()
    # add the player to the neptune database with playerID and timestamp 
    try:
        neptuneResponse=g.addV('player').property(id, newPlayerId).property('playerid',newPlayerId).property('timestamp',datetime.datetime.now()).next() 
        print(g.V().values('playerid').toList())
        return ("Player Created " + newPlayerId)
        remoteConn.close()

    except:
    # neptune db failed 
        return ("Error - Player ID either already exists or is in the incorrect format - " + newPlayerId)
        remoteConn.close()

# record that a player has participated in a game    
def playerPlaysGame(inputvars):
    playerId=inputvars["playerid"][0]    
    gameId=inputvars["gameid"][0]    
    durationPercentage=inputvars["durationPercentage"][0]            

    g,remoteConn=createNeptune()
    
    ## add the link between the player and the game - i.e. Vertex -> Edge 
    try:
        neptuneResponse=g.V(playerId).addE('played').to(__.V(gameId)).property('duration', durationPercentage).next()
        neptuneResponse=g.V(gameId).addE('wasplayedby').to(__.V(playerId)).property('duration', durationPercentage).next()

        return ("Player " + playerId + " played " + gameId + " for " + durationPercentage +"%")
        remoteConn.close()

    except:
        return ("Error - game or player ID doesn't exist or format error: " + "Player " + playerId + " played " + gameId + " for " + durationPercentage +"%")
        remoteConn.close()

# money transaction by a player 
def playerTransaction(inputvars):
    playerId=inputvars["playerid"][0]    
    transactionValue=inputvars["transactionvalue"][0]    
    transactionId=inputvars["transactionid"][0]
    g,remoteConn=createNeptune()
    
    # record the transaction in neptune and create a link - i.e. vertex->edge to the player 
    try:
        neptuneResponse=g.addV('transaction').property(id, transactionId).property('transactionid',transactionId).property('transactionvalue',transactionValue).property('playerid',playerId).property('timestamp',datetime.datetime.now()).next() 
        neptuneResponse=g.V(playerId).addE('madetransaction').to(__.V(transactionId)).next()
        neptuneResponse=g.V(transactionId).addE('transactionby').to(__.V(playerId)).next()

        return ("Player " + playerId + " made transaction of ID " + transactionId + " for " + transactionValue +"USD")
        remoteConn.close()
  
    except:
        return ("Error - transaction error. Transaction either already exists or player doesn't exist.  " + "Player " + playerId + " made transaction of ID " + transactionId + " for " + transactionValue +"USD")
        remoteConn.close()

# record an abusive incident - i.e. chat, screenshot, audio
def recordAbuse(inputvars):
    playerId=inputvars["playerid"][0]    
    gameId=inputvars["gameid"][0]    
    abuseType=inputvars["abusetype"][0]
    abusecontent=inputvars["abusecontent"][0]
    abuseId="a" + str(random.randint(100000,900000))
    g,remoteConn=createNeptune()
    
    # create the abuse event and then connect the Vertex together - i.e. create an edge between them 
    try:
        neptuneResponse=g.addV('abuse').property(id,abuseId).property('abuseid',abuseId).property('abusetype',abuseType).property('abusecontent',abusecontent).property('timestamp',datetime.datetime.now()).next() 
        neptuneResponse=g.V(playerId).addE('wasabusive').to(__.V(abuseId)).next()
        neptuneResponse=g.V(gameId).addE('abuseingame').to(__.V(abuseId)).next()

        return ("Player " + playerId + " was abusive (" + str(abuseId) + ") in game " + gameId)
    except:
    # neptune failed to add the abuse     
        return ("Error - abuse not registered. The game or player do not exist or there is a format error: " + "Player " + playerId + " was abusive (" + str(abuseId) + ") in game " + gameId)
    
    remoteConn.close()

### remove the contents of the neptune db 
def clearNeptune(inputvars):
    g,remoteConn=createNeptune()
    g.V().drop().iterate()
    return ("Cleared Neptune")
    remoteConn.close()

# create the connection to Neptune 
def createNeptune():
    graph = Graph()
    CLUSTER_ENDPOINT = os.environ['CLUSTER_ENDPOINT']
    CLUSTER_PORT = os.environ['CLUSTER_PORT']
    remoteConn = DriverRemoteConnection('wss://' + CLUSTER_ENDPOINT + ":" + CLUSTER_PORT + '/gremlin','g')

    
    g = graph.traversal().withRemote(remoteConn)

    return g,remoteConn 
    
