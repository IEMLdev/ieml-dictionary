from flask import Flask
app = Flask(__name__)
from yaml import load
import os

ROOT_PARADIGMS = os.listdir('dictionary')

@app.route('/')
def index():
    return "\n".join(ROOT_PARADIGMS)

@app.route('/<file_name>')
def root_paradigm(file_name):
	assert file_name in ROOT_PARADIGMS
	file_name = os.path.join('dictionary', file_name) 
	with open(file_name) as fp:

		return str(load(fp))