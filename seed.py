from sqlalchemy import create_engine  
from sqlalchemy import Column, Integer, Text, Boolean, DateTime  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from cassiopeia import riotapi
from datetime import datetime
import requests
import json
import os


riot_api_key = os.environ['RIOT_API_KEY']
riotapi.set_region("NA")
riotapi.set_api_key(riot_api_key)

db_string = os.environ["DATABASE_URL"]
SQLALCHEMY_TRACK_MODIFICATIONS = True
db = create_engine(db_string)
Base = declarative_base()  


class Champ(Base):  
    __tablename__ = 'champ_info'
    champ_id = Column(Integer, primary_key=True)
    champ_name = Column(Text)
    is_free = Column(Boolean, default=False)
    date_info_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Session = sessionmaker(db)
session = Session()
Base.metadata.create_all(db)

all_champs = riotapi.get_champions()

for champion in all_champs:
	champ = Champ(champ_id=champion.id, champ_name=champion.name)
	champ_exist = session.query(Champ).filter_by(champ_id = champion.id).first()
	if not champ_exist:
		session.add(champ)
		session.commit()