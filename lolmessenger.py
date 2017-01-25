# imports 
from flask import Flask, request
import requests
import json
from cassiopeia import riotapi
import sys


#setup + auth tokens
app = Flask(__name__)
#app.config.from_pyfile('config.py')
#NA only 
riotapi.set_region("NA")
riotapi.set_api_key("YOUR-API-KEY-HERE")
page_auth_token = 'EAAaF14INvz4BAPBZAbCZAUOpkDBlHmFxFkYaJPJ83bYeZCwH0kJbe7Ru38IkAJO7P4dFDDKqF4ZBLXb8NV4C1tU461MhSBKoJIdub3Nolrxz11DGuWkpdyGdjlOEBDLIbqqZBeNsvcstCWqtQATSsLyNtKYP8F7e385saBJDulAZDZD'
verify_token = 'my_voice_is_my_password_verify_me'


@app.route('/webhook', methods=['GET'])
#Authenticate for Messenger
def auth():
	req = request.args
	if req.get('hub.verify_token') == verify_token:
		print "Verify token matches"
		return req.get('hub.challenge')
	else:
		print "Invalid token"
		return "Page Not Verified, Invalid verify token"


@app.route('/webhook', methods=['POST'])
#Messages and how to respond to them
# 'help' will show certain structured messages
def send_reply():
	#reply = "Hello World"
	req = request.json["entry"][0]['messaging'][0]
	print req
	sender_id = req['sender']['id']
	reply = req['message']['text']
	print sender_id
	headers = {
		'Content-Type': 'application/json'
	}
	params = {
		'access_token': page_auth_token
	}
	resp = {
		'recipient': {
			'id': sender_id
		},
		'message': {
			'text': reply
		}
	}
	r = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, json=resp, headers=headers)
	sys.stdout.flush()
	return "Reply Sent"

'''

#helper functions
def free_champs():
	#will call riot api and return the free week champs


def is_in_game(summoner_name):
	#check if summoner_name is playing right now


#not a priority, get above two working first
def champ_mastery(summoner_name, champ=None):
	#top 3 champ masteries of summoner_name (Default)
	#Champ mastery of 'champ' (second arg)
	if champ == None:
		#default
	else:

'''


if __name__ == "__main__":
	app.run()
