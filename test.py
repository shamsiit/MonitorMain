import psycopg2
import psycopg2.extras
import sys
import pprint
import json
from flask import Flask
from flask import request,jsonify,abort,render_template
import collections


app = Flask(__name__)


@app.route('/welcome')
def greetings():
	return render_template('report.html')

if __name__=="__main__":
	app.debug = True
	app.run('127.0.0.1',5000)

