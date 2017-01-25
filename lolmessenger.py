# imports 
from flask import Flask, request
import requests
import json
from cassiopeia import riotapi


#setup + auth tokens
app = Flask(__name__)
#NA only 
riotapi.set_region("NA")
riotapi.set_api_key("YOUR-API-KEY-HERE")
page_auth_token = 'EAAaF14INvz4BADRdJNuZBQD7zIGcfO6ZBRDUTBZBMUx23z1tV1PiL6AZATcCYsE3k2JIRdM4sxTYxgcJliCXovIrdOXw0OrCI8lT5JNlAcocjSjDqAqmAIRon7kPWZCJ9YXARRHVzpfCcrv3hFZB9lyRVu0C1zOV3bkI1gkNwKywZDZD'
verify_token = 'my_voice_is_my_password_verify_me'


@app.route('/webhook', methods=['GET'])
#Authenticate for Messenger
def auth():
	if request.args.get('hub.verify_token') == verify_token:
		print "Verify token matches"
		return "Page Verified"
	else:
		print "Invalid token"
		return "Page Not Verified, Invalid verify token"


@app.route('/webhook', methods=['POST'])
#Messages and how to respond to them
def send_reply():
	reply = "Hello World"
	req = request.json()
	sender_id = req["sender"]["id"]
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
