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

@app.route('/api/v1/alert', methods = ['GET','POST','PUT'])
def alerts():
	if request.method == 'GET':
                conn = dbConnection()
                cur = conn.cursor()
                try:
                        cur.execute("select array_to_json(array_agg(alert)) FROM alert")
                except:
                        print("Error executing select")
                results = cur.fetchall()

                return jsonify({'results':results}),200

	elif request.method == 'POST':
		response = request.json
                print(response)
                level = str(request.json['level'])
                print(level)
                time = str(request.json['time'])
                print(time)
		service = 'servicename2'
		message = str(request.json['message'])
		print(message)
                data = request.json['data']
                print(type(data))
                series = data['series']
                print(type(series))
                series_data = series[0]
                values = series_data['values']
                value_0 = values[0]
                value = value_0[1]
                print(value)
		tags = series_data['tags']
                host = str(tags['host'])
                print(host)
                details = 'details'
                result = {
				'host':host,
				'service':service,
				'message':message,
				'detail':details,
				'level':level,
				'time':time,
				'value':value
				
				}
                conn = dbConnection()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
		try:
			ptr_str = "SELECT alert_insert("+host+","+service+","+message+","+details+","+level+","+time+","+str(value)+")"
			print(ptr_str)
                        cur.execute("SELECT alert_insert('"+host+"','"+service+"','"+message+"','"+details+"','"+level+"','"+time+"',"+str(value)+")")
                except Exception,e:
			print str(e)
                        print("error inserting")
                        conn.rollback()
                        abort(400)
                conn.commit()

                return jsonify({'results':result}),200
	elif request.method == 'PUT':
		if not request.json or not 'alert_id' or not 'host_name' or not 'service_name' or not 'message' or not 'detail' or not 'level' or not 'time' or not 'value' in request.json:
			abort(400)
		res = {
		'alert_id':request.json['alert_id'],
		'host_name':request.json['host_name'],
		'service_name':request.json['service_name'],
		'message':request.json['message'],
		'detail':request.json['detail'],
		'level':request.json['level'],
		'time':request.json['time'],
		'value':request.json['value']
		}
		conn = dbConnection()
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		try:
			cur.execute("SELECT alert_update("+str(request.json['alert_id'])+",'"+request.json['host_name']+"','"+request.json['service_name']+"','"+request.json['message']+"','"+request.json['detail']+"','"+request.json['level']+"','"+request.json['time']+"',"+str(request.json['value'])+")")
		except:
			print("ERROR Updating into alert")
			conn.rollback()	
			abort(400)
		conn.commit()

		return jsonify({'results':res}),201

if __name__=="__main__":
	app.debug = True
	app.run('hdf1',5000)

