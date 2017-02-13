import psycopg2
import psycopg2.extras

from flask import Flask,request,jsonify,abort,request

import collections

app = Flask(__name__)

def database_connection():
	connection_string = "dbname=testdb user=postgres password=postgres host=localhost"
	try:
		print("trying to connect . . .")
		return psycopg2.connect(connection_string)
	except:
		print("couldnot connect to DB")

@app.route("/api/subsystem",methods = ["POST","GET","PUT"])
def subsystem():
	if request.method == "POST":
		try :
			if not request.json or not "sub_system_name" in request.json:
				abort(400)

			values = {
				'sub_system_name' : request.json['sub_system_name']
			}

			sub_system_name = request.json['sub_system_name']
			conn = database_connection()
			cur = conn.cursor()

			print ('request json sub_system_name : ' + sub_system_name)
			
			cur.execute("INSERT INTO sub_system (sub_system_name) VALUES ('" + sub_system_name +"');")
		except:
			print ("ERROR while insert into sub_system table")
			conn.rollback()
			abort(400)
			
		conn.commit()

		return jsonify(request.json),200

	elif request.method == 'GET':
		conn = database_connection()
		cur = conn.cursor()
		try:
			cur.execute(" select array_to_json(array_agg(sub_system)) FROM sub_system;")
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
			if not request.json or not "sub_system_id" or not "sub_system_name" in request.json:
				abort(400)

			values = {
				'sub_system_id' : request.json['sub_system_id'],
				'sub_system_name' : request.json['sub_system_name']
			}

			sub_system_id = request.json['sub_system_id']
			sub_system_name = request.json['sub_system_name']
			
			print ('request json sub_system_name : ' + sub_system_name)
			
			cur.execute("UPDATE sub_system SET sub_system_name = '"+sub_system_name+"' WHERE sub_system_id = " + str(sub_system_id))
		except:
			print ("ERROR while update into sub_system table")
			conn.rollback()
			abort(400)
			
		conn.commit()

		return jsonify({'updated' : request.json}),200 


@app.route('/api/subsystem/<int:sub_system_id>', methods=['GET','DELETE'])
def sub_system_operation_by_id(sub_system_id):
	if request.method == 'GET':
		conn = database_connection()
		cur = conn.cursor()

		try:
			cur.execute("select array_to_json(array_agg(sub_system)) FROM sub_system WHERE \"sub_system_id\"="+str(sub_system_id))

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
			cur.execute("select array_to_json(array_agg(sub_system)) FROM sub_system WHERE \"sub_system_id\"="+str(sub_system_id))
			data = cur.fetchall()
			cur.execute("DELETE FROM sub_system WHERE sub_system_id = "+str(sub_system_id))
		except:
			print ('Error while deleting data..')
			abort(404)
		
		
		conn.commit()

		return jsonify({'data':data}),200

if __name__ == '__main__':
	app.debug = True;
	app.run('127.0.0.1',5000)
