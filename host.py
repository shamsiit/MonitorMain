import psycopg2
import psycopg2.extras
from flask import Flask,request,jsonify,abort,request
import collections

app = Flask(__name__)

def database_connection():
	connection_string = "dbname=mydb user=postgres password=postgres host=localhost"
	try:
		print("trying to connect . . .")
		return psycopg2.connect(connection_string)
	except:
		print("couldnot connect to DB")

@app.route("/api/host",methods = ["POST","GET","PUT"])
def host():
	if request.method == "POST":
	
		try :
			if not request.json or not "host_name" in request.json:
				abort(400)

			values = {
				'host_name' : request.json['host_name']
			}

			host_name = request.json['host_name']
			conn = database_connection()
			cur = conn.cursor()

			print ('request json host_name : ' + host_name)
			
			cur.execute("INSERT INTO host (host_name) VALUES ('" + host_name +"');")
		except:
			print ("ERROR while insert into host table")
			conn.rollback()
			abort(400)
			
		conn.commit()

		return jsonify(request.json),200

	elif request.method == 'GET':
		conn = database_connection()
		cur = conn.cursor()
		try:
			cur.execute(" select array_to_json(array_agg(host)) FROM host;")
		except Exception,e:
			print(e)
			print('error occured')

			abort(404)

		data = cur.fetchall()

		conn.commit()
		return jsonify({'data': data}),200

	elif request.method=='PUT':
		conn = database_connection()
		cur = conn.cursor()

		try :
			if not request.json or not "host_id" or not "host_name" in request.json:
				abort(400)

			values = {
				'host_id' : request.json['host_id'],
				'host_name' : request.json['host_name']
			}

			host_id = request.json['host_id']
			host_name = request.json['host_name']
			
			print ('request json host_name : ' + host_name)
			
			cur.execute("UPDATE host SET host_name = '"+host_name+"' WHERE host_id = " + str(host_id))
		except:
			print ("ERROR while update into host table")
			conn.rollback()
			abort(400)
			
		conn.commit()

		return jsonify({'updated' : request.json}),200 


@app.route('/api/host/<int:host_id>', methods=['GET','DELETE'])
def host_operation_by_id(host_id):
	if request.method == 'GET':
		conn = database_connection()
		cur = conn.cursor()

		try:
			cur.execute("select array_to_json(array_agg(host)) FROM host WHERE \"host_id\"="+str(host_id))

		except:
			print ('Error while getting data..')
			abort(404)
		
		data = cur.fetchall()
		conn.commit()

		return jsonify({'data':data}),200

	if request.method == 'DELETE':
		conn = database_connection()
		cur = conn.cursor()

		data = []

		try:
			cur.execute("select array_to_json(array_agg(host)) FROM host WHERE \"host_id\"="+str(host_id))
			data = cur.fetchall()
			cur.execute("DELETE FROM host WHERE host_id = "+str(host_id))
		except:
			print ('Error while deleting data..')
			abort(404)
		
		conn.commit()

		return jsonify({'data':data}),200

if __name__ == '__main__':
	app.debug = True;
	app.run('127.0.0.1',5000)
