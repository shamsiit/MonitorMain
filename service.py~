import psycopg2
import psycopg2.extras
import sys
import pprint
import json
from flask import Flask
from flask import request,jsonify,abort
import collections

app = Flask(__name__)

def dbConnection():
	connection_credential = 'host=localhost dbname=testdb user=postgres password=ipvision123'
	try:
		return psycopg2.connect(connection_credential)
	except:
		print ('database connection problem')

@app.route('/api/v1/service', methods = ['GET','POST','PUT'])
def services():
	if request.method == 'GET':
                conn = dbConnection()
                cur = conn.cursor()
                try:
                        cur.execute("select array_to_json(array_agg(service)) FROM service")
                except:
                        print("Error executing select")
                results = cur.fetchall()

                return jsonify({'results':results}),200

	elif request.method == 'POST':
		if not request.json or not 'service_name' or not 'pid' or not 'cwd' or not 'env' in request.json:
                        abort(401)
                result = {
                          'service_name': request.json['service_name']
				}
                conn = dbConnection()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
		try:
                        cur.execute("""INSERT INTO service (service_name,pid,cwd,env) VALUES (%s,%s,%s,%s);""",(request.json['service_name'],request.json['pid'], request.json['cwd'], request.json['env']))

                        print(request.json)
                except:
                        print("error inserting")
                        conn.rollback()
                        abort(400)
                conn.commit()

                return jsonify({'results':result}),200
	elif request.method == 'PUT':
		if not request.json or not 'service_id' or not 'service_name' or not 'pid' or not 'cwd' or not 'env' in request.json:
			abort(400)
		res = {
		'service_id':request.json['service_id'],
		'service_name':request.json['service_name'],
		'pid':request.json['pid'],
		'cwd':request.json['cwd'],
		'env':request.json['env']
		}
		conn = dbConnection()
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		try:
			cur.execute("UPDATE service  SET service_name='"+request.json['service_name']+"', pid="+str(request.json['pid'])+", cwd='"+request.json['cwd']+
			"' , env='"+request.json['env']+"'  WHERE service_id="+str(request.json['service_id']) )
		except:
			print("ERROR Updating into service")
			conn.rollback()	
			abort(400)
		conn.commit()

		return jsonify({'results':res}),201
@app.route('/api/v1/service/<int:id>',methods=['GET','DELETE'])
def service_by_id(id):
	if request.method == 'GET':
                conn = dbConnection()
                cur = conn.cursor()
                try:
                        cur.execute("select array_to_json(array_agg(service)) FROM service where service_id="+str(id))
                except:
                        print("Error executing select")
                results = cur.fetchall()

                return jsonify({'results':results})  
	elif request.method == 'DELETE':
		conn = dbConnection()
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		try:
			cur.execute("DELETE FROM service WHERE service_id="+str(id) )
		except:
			print("ERROR DELETING into service")
			conn.rollback()	
			abort(400)
		conn.commit()

		return jsonify({'results':'DELETE'}),201 


@app.route('/welcome')
def greetings():
	return jsonify('true'),200

if __name__=="__main__":
	app.debug = True
	app.run('hdf1',5000)

