# imports 
from flask import Flask, request
import requests
import json
import rito


app = Flask(__name__)

#Page Authentication Token for the page which the messenger will be accessed from
page_auth_token = ''
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

def free_champs():
	#will call riot api and return the free week champs


def is_in_game(summoner_name):
	#check if summoner_name is playing right now
	


def champ_mastery(summoner_name, champ=None):
	#top 3 champ masteries of summoner_name (Default)
	#Champ mastery of 'champ' (second arg)
	if champ == None:
		#default
	else:


if __name__ == "__main__":
	app.run()
