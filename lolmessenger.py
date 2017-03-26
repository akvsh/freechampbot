# imports 
import sys
import os
import json

from sqlalchemy import create_engine  
from sqlalchemy import Column, Integer, Text, Boolean, DateTime  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from cassiopeia import riotapi
from flask import Flask, request
import requests
from datetime import datetime
from cassiopeia import riotapi


#setup + auth tokens
app = Flask(__name__)
riot_api_key = os.environ['RIOT_API_KEY']
riotapi.set_region("NA")
riotapi.set_api_key(riot_api_key)
page_auth_token = os.environ['PAT']
verify_token = 'my_voice_is_my_password_verify_me'
help_txt = "commands"
free_champs_txt = "free champs this week"
invalid_cmd_error = " Or your command was invalid, type in 'commands' to get a full list of available commands!"
all_champs_url = "https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?dataById=true&api_key=" + riot_api_key
all_champs = requests.get(all_champs_url).json()["data"]
champ_to_id = {}
help_msg = """Supported messages: 
NOTE: The square brackets are required around the fields

* 'free champs this week'

* 'is summoner [summoner_username] in game?'

* 'top champ masteries for [summoner_username]'

* 'summoner [summoner_username] mastery of champion [champion_name]'

* 'is [server_name] server up?'

* 'set region [region]' for player stats in other regions run this first
"""


db_string = os.environ["DATABASE_URL"]
SQLALCHEMY_TRACK_MODIFICATIONS = True
db = create_engine(db_string)
Base = declarative_base()  


class Champ(Base):  
    __tablename__ = 'champ_info'
    champ_id = Column(Integer, primary_key=True, unique=True)
    champ_name = Column(Text)
    is_free = Column(Boolean, default=False)
    date_info_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Session = sessionmaker(db)
session = Session()
Base.metadata.create_all(db)

# ----- HELPER FUNCTIONS ------ #

def get_free_champs_lst():
	free_champs_url = "https://na.api.pvp.net/api/lol/na/v1.2/champion?freeToPlay=true&api_key=" + riot_api_key
	free_champs = requests.get(free_champs_url).json()["champions"]
	lst_free_champs = [champ["id"] for champ in free_champs]
	print("Free Champs IDs:")
	print(lst_free_champs)
	return lst_free_champs

def update_free_champs_db(free_champs_ids):
	names_lst = []
	for c_id in free_champs_ids:
			champ = session.query(Champ).filter_by(champ_id = c_id).first()
			names_lst.append(champ.champ_name)
			print("Updating for: " +  champ.champ_name)
			print("Current status: " + str(champ.is_free))
			champ.is_free = True
			session.commit()
			
	return names_lst

def get_free_champs():
	print("All Champs:")
	print(all_champs)
	free_champs_db_lst = list(session.query(Champ).filter_by(is_free = True))

	#No free champs updated yet
	if free_champs_db_lst == []:
		lst_free_champs = get_free_champs_lst()
		lst_names = update_free_champs_db(lst_free_champs)
	#There is a list of free champs
	else:

		date_updated = free_champs_db_lst[0].date_info_updated
		num_days_passed =  (datetime.now().date() - date_updated).days
		#update free champ list every day
		if num_days_passed >= 1:
			lst_free_champs = get_free_champs_lst()
			for champ in free_champs_db_lst:
				champ.is_free = False
				session.commit()
			lst_names = update_free_champs_db(lst_free_champs)
		else:
			lst_names = []
			for champ in free_champs_db_lst:
				lst_names.append(champ.champ_name)
	print(lst_names) # see free champs list
	return lst_names


def get_username(msg):
	name = msg.lower()
	index1 = name.index("[")
	index2 = name.index("]")
	name = msg[index1+1:index2]
	return name

def get_champion_name(msg):
	champ = msg.lower()
	start_index = champ.index("champion")
	index1 = champ.index("[", start_index)
	index2 = champ.index("]", start_index)
	champ = msg[index1+1:index2]
	return champ


def get_server(msg):
	server = msg.lower()
	index1 = server.index("[")
	index2 = server.index("]")
	server = msg[index1+1:index2]
	return server

def get_server_status():
	servs = json.loads(riotapi.get_shard().to_json())
	print(servs)
	status = []
	for service in servs["services"]:
		status.append("\n" + service["name"]+ " - " + service["status"] + "\n")
		if len(service["incidents"]) != 0:
			for update in service["incidents"]:
				status.append("\t * " + update["updates"][0]["content"] + "\n")

	#status = [service["name"]+": "+service["status"]+"\n" for service in servs["services"]]
	return status

@app.route('/webhook', methods=['GET'])
#Authenticate for Messenger
def auth():
	req = request.args
	if req.get('hub.verify_token') == verify_token:
		print("Verify token matches")
		return req.get('hub.challenge')
	else:
		print("Invalid token")
		return "Page Not Verified, Invalid verify token"


@app.route('/webhook', methods=['POST'])
#Messages and how to respond to them
# 'help' will show certain structured messages

def send_reply():
	#reply = "Hello World"
	req = request.json["entry"][0]['messaging'][0]
	print(req)

	sender_id = req['sender']['id']
	sender_msg = req['message']['text']
	msg_lower = sender_msg.lower()

	if msg_lower == help_txt:
		reply = help_msg

	elif msg_lower == free_champs_txt:
		#call riot api to get list of free champs
		free_champs = get_free_champs()
		reply = "Free champs for this week: \n" + "".join("- "+champ+"\n" for champ in free_champs)

	elif "is summoner" in msg_lower and "in game" in msg_lower:
		username = get_username(sender_msg)
		print("U: " + username)
		try:
			user = riotapi.get_summoner_by_name(username)
		except:
			reply = "This player doesn't exist in this region!" + invalid_cmd_error
		else:		
			curr_game = riotapi.get_current_game(user)
			if curr_game is None:
				reply = "They aren't in a game right now!"
			else:
				reply = "Yes! They are in a game :)"

	elif "server up?" in msg_lower:
		server = get_server(sender_msg)
		try:
			riotapi.set_region(server)
		except:
			reply = "Invalid Region!" + invalid_cmd_error
		else:
			serv_status = get_server_status()
			reply = "".join(serv_status)
		finally:
			riotapi.set_region("NA")

	elif "top champ masteries" in msg_lower:
		username = get_username(sender_msg)
		summoner = riotapi.get_summoner_by_name(username)
		print("Username for masteries: " + username)
		reply = ""
		try:
			masteries = riotapi.get_top_champion_masteries(summoner)
			for c in masteries:
				champ = json.loads(c.to_json())
				champ_id = str(champ['championId'])
				print("champ_id: " + champ_id)
				champ_name = all_champs[champ_id]['name']
				reply += champ_name + "\n" 
				champ_level = str(champ['championLevel'])
				reply += "- Level: " +  champ_level + "\n"
				champ_points = str(champ['championPoints'])
				reply += "- Total Points: " +  champ_points + "\n"
				print("champ_name: " + champ_name)
			total_mastery_score = riotapi.get_champion_mastery_score(summoner)
		except:
			reply = "This player doesn't exist in this region!" + invalid_cmd_error
		else:		
			reply += "Total Mastery Score: " +  str(total_mastery_score)
			print("Total Mastery Score: " +  str(total_mastery_score))
			
	elif "mastery of champion" in msg_lower:
		username = get_username(sender_msg)
		summoner = riotapi.get_summoner_by_name(username)
		print(json.loads(summoner.to_json()))
		champ_name = get_champion_name(sender_msg)
		champ = riotapi.get_champion_by_name(champ_name)
		print("User: " + username)
		print("Champ: " + champ_name)
		try:
			print("getting champ_mastery")
			champ_mastery = riotapi.get_champion_mastery(summoner, champ)
			print("to json")
		except:
			reply = "Invalid username/champion!" + invalid_cmd_error
		else:	
			reply = "Mastery here"
			print(champ_mastery)


	elif "set region" in msg_lower:
		region = msg.lower()
		index1 = region.index("[")
		index2 = region.index("]")
		region = region[index1+1:index2]
		try:
			riotapi.set_region(region)
		except:
			reply = "Invalid Region!" + invalid_cmd_error
		else:
			reply = "Region set to " + region

	else:
		reply = sender_msg
	
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


if __name__ == "__main__":
	app.run()
