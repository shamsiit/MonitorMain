import psycopg2
import psycopg2.extras
import sys
import pprint
import json
from flask import Flask
from flask import request,jsonify,abort,render_template
import collections

import argparse
import pandas as pd

from influxdb import DataFrameClient
import json
import dateutil.parser as parser

host='38.127.68.166'
port=48086
user = ''
password = ''
dbname = 'telegraf'

app = Flask(__name__)

def dbConnection():
	connection_credential = 'host=127.0.0.1 dbname=testdb user=postgres password=ipvision123'
	try:
		return psycopg2.connect(connection_credential)
	except Exception as e:
		print str(e)
		print ('database connection problem')

@app.route('/api/v1/report', methods = ['GET','POST','PUT'])
def services():
	if request.method == 'GET':
		conn = dbConnection()
                cur = conn.cursor()
                try:
                        #cur.execute("select array_to_json(array_agg(report)) FROM report")
			cur.execute("select * FROM report")
                except:
                        print("Error executing select")
                results = cur.fetchall()
		list_res = []
		for row in results:
			d = collections.OrderedDict()
			d['report_id'] = row[0]
			d['host_id'] = row[1]
			d['sub_system_id'] = row[2]
			d['report_json'] = json.loads(row[3])
			d['time'] = row[4]
			list_res.append(d)

                return jsonify({'results':list_res}),200,{'Access-Control-Allow-Origin': '*'}

	elif request.method == 'POST':
		if not request.json or not 'host_id' or not 'sub_system_id' or not 'fromDate' or not 'toDate' or not 'time' in request.json:
                        abort(401)

		print("Entered......")

		conn = dbConnection()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

		try:
			cur.execute("select host_name FROM host where host_id="+str(request.json['host_id']))
                except:
                        print("Error executing select")
                results_host = cur.fetchall()
		host_name = ''
		for row in results_host:
			host_name = row[0]
		print(host_name+".....")

		try:
			cur.execute("select sub_system_name FROM sub_system where sub_system_id="+str(request.json['sub_system_id']))
                except:
                        print("Error executing select")
                results_sub_system = cur.fetchall()
		sub_system_name = ''
		for row in results_sub_system:
			sub_system_name = row[0]

		json_data = {}

		if sub_system_name=='cpu':
			print("In cpu")
			client = DataFrameClient(host, port, user, password, dbname)
			toDate = request.json['toDate'].replace("/","-")+":00"
			fromDate = request.json['fromDate'].replace("/","-")+":00"
			query = "select * from cpu  where cpu = 'cpu-total' AND host='"+host_name+"' AND (time<='"+toDate+"' OR time>='"+fromDate+"') limit 10"
			print(query)
			data = client.query("select * from cpu  where cpu = 'cpu-total' AND host='"+host_name+"' AND (time<='"+toDate+"' OR time>='"+fromDate+"') limit 10")
			dataframe = data['cpu']
			dict={}
       		 	dict["usage_idle"]=json.loads(dataframe['usage_idle'].to_json(orient='values'))
        		dict["usage_user"]=json.loads(dataframe['usage_user'].to_json(orient='values'))
        		dict["usage_softirq"]=json.loads(dataframe['usage_softirq'].to_json(orient='values'))
        		dict["usage_system"]=json.loads(dataframe['usage_system'].to_json(orient='values'))
			list = dataframe.index.tolist()
			list_final = []
			for x in list:
				date = (parser.parse(str(x)))
				iso = date.isoformat()
				list_final.append(iso)
        		dict["index"] = list_final
        		json_data = dict
			#print(json.dumps(json_data))
			print("After influx query")


                print("before postgres query")
		print(request.json['time'])

		query = """INSERT INTO report (host_id,sub_system_id,report_json,time) VALUES (%(int)s,%(int)s,%(json)s,%(timestamp)s)"""
		data = {'int':request.json['host_id'],'int':request.json['sub_system_id'],'json':json.dumps(json_data),'timestamp':request.json['time']}

		try:
                        cur.execute(query,data)
			print("After postgres query")

                except Exception as e:
			print str(e)
                        print("error inserting")
                        conn.rollback()
                        abort(400)
                conn.commit()

		result = {
			"host_id":request.json['host_id'],
			"sub_system_id":request.json['sub_system_id'],
			"report_json": json.dumps(json_data),
			"fromDate": request.json['fromDate'],
			"toDate": request.json['toDate'],
			"time": request.json['time']
				}

                return jsonify({'results':result}),200,{'Access-Control-Allow-Origin': '*'}
	elif request.method == 'PUT':
		if not request.json or not 'report_id' or not 'host_id' or not 'sub_system_id' or not 'report_json' or not 'time' in request.json:
			abort(400)
		res = {
			"report_id":request.json['report_id'],
			"host_id":request.json['host_id'],
			"sub_system_id":request.json['sub_system_id'],
			"report_json": request.json['report_json'],
			"time": request.json['time']
				}
		conn = dbConnection()
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

		query = """UPDATE report SET host_id=(%s),sub_system_id=(%s),report_json=(%s),time=(%s) WHERE report_id=(%s)"""
		data = (request.json['host_id'],request.json['sub_system_id'],json.dumps(request.json['report_json']),request.json['time'],request.json['report_id'],)

		try:
			cur.execute(query,data)
		except Exception as e:
			print str(e)
			print("ERROR Updating into service")
			conn.rollback()	
			abort(400)
		conn.commit()

		return jsonify({'results':res}),201,{'Access-Control-Allow-Origin': '*'}
@app.route('/api/v1/report/<int:id>',methods=['GET','DELETE'])
def service_by_id(id):
	if request.method == 'GET':
                conn = dbConnection()
                cur = conn.cursor()
                try:
                        cur.execute("select * FROM report where report_id="+str(id))
                except:
                        print("Error executing select")
                results = cur.fetchall()
		list_res = []
		for row in results:
			d = collections.OrderedDict()
			d['report_id'] = row[0]
			d['host_id'] = row[1]
			d['sub_system_id'] = row[2]
			d['report_json'] = json.loads(row[3])
			d['time'] = row[4]
			list_res.append(d)

                return jsonify({'results':list_res}),{'Access-Control-Allow-Origin': '*'} 
	elif request.method == 'DELETE':
		conn = dbConnection()
		cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		try:
			cur.execute("DELETE FROM report WHERE report_id="+str(id) )
		except:
			print("ERROR DELETING into report")
			conn.rollback()	
			abort(400)
		conn.commit()

		return jsonify({'results':'DELETE'}),201,{'Access-Control-Allow-Origin': '*'}

@app.route("/api/v1/subsystem",methods = ["POST","GET","PUT"])
def subsystem():
	if request.method == "POST":
		try :
			if not request.json or not "sub_system_name" in request.json:
				abort(400)

			values = {
				'sub_system_name' : request.json['sub_system_name']
			}

			sub_system_name = request.json['sub_system_name']
			conn = dbConnection()
			cur = conn.cursor()

			print ('request json sub_system_name : ' + sub_system_name)
			
			cur.execute("INSERT INTO sub_system (sub_system_name) VALUES ('" + sub_system_name +"');")
		except:
			print ("ERROR while insert into sub_system table")
			conn.rollback()
			abort(400)
			
		conn.commit()

		return jsonify(request.json),200,{'Access-Control-Allow-Origin': '*'}

	elif request.method == 'GET':
		conn = dbConnection()
		cur = conn.cursor()
		try:
			cur.execute(" select * FROM sub_system;")
		except Exception,e:
			print(e)
			print('error occured')

			abort(404)

		data = cur.fetchall()
		list_res = []
		for row in data:
			d = collections.OrderedDict()
			d['sub_system_id'] = row[0]
			d['sub_system_name'] = row[1]
			list_res.append(d)

		conn.commit()
		return jsonify({'data': list_res}),200,{'Access-Control-Allow-Origin': '*'}

	elif request.method=='PUT':
		conn = dbConnection()
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

		return jsonify({'updated' : request.json}),200,{'Access-Control-Allow-Origin': '*'} 


@app.route('/api/v1/subsystem/<int:sub_system_id>', methods=['GET','DELETE'])
def sub_system_operation_by_id(sub_system_id):
	if request.method == 'GET':
		conn = dbConnection()
		cur = conn.cursor()

		try:
			cur.execute("select * FROM sub_system WHERE \"sub_system_id\"="+str(sub_system_id))

		except:
			print ('Error while getting data..')
			abort(404)
		
		data = cur.fetchall()
		list_res = []
		for row in data:
			d = collections.OrderedDict()
			d['sub_system_id'] = row[0]
			d['sub_system_name'] = row[1]
			list_res.append(d)
		conn.commit()

		return jsonify({'data':list_res}),200,{'Access-Control-Allow-Origin': '*'}

	if request.method == 'DELETE':
		conn = dbConnection()
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

		return jsonify({'data':data}),200,{'Access-Control-Allow-Origin': '*'}

@app.route('/api/v1/host',methods=['GET','POST','PUT','DELETE'])
def host_operation():
	if request.method == 'POST':
		try:
			host_name = request.json['host_name']
			nested_string ="ARRAY["
			print(type(request.json['interface']))
                        for nested_value in request.json['interface']:
				nested_string += "("
				nested_string += "'"
				nested_string += str(nested_value['ip'])
				nested_string += "'"
				nested_string += ","
				nested_string += "'"
				nested_string += nested_value['netmask']
				nested_string += "'"
				nested_string += ")::interface_type"
				nested_string += ","
			nested_string = nested_string.rstrip(",")	
			nested_string +=  "]"

			machine_id = request.json['machine_id']
			status = request.json['status']
			print(host_name)
			print(str(machine_id))
			print(nested_string)
			print(status)

			connection = dbConnection()
			cursor = connection.cursor()
			cursor.execute("INSERT INTO host (host_name, machine_id, interface , status) VALUES ('"+host_name+"' , '"+str(machine_id)+"' , "+nested_string+" , '"+status+"');")
			
                except Exception,e:
			
			print(e)
                        abort(404)
		connection.commit()
		return jsonify(request.json),200,{'Access-Control-Allow-Origin': '*'}

	elif request.method == 'GET':
		connection = dbConnection()
		cursor = connection.cursor()
		
		try : 
			cursor.execute("select * FROM host;")
		except Exception,e:
			print(e)
			print('error occured')
			abort(404)

		results = cursor.fetchall()
		list_res = []
		for row in results:
			d = collections.OrderedDict()
			d['host_id'] = row[0]
			d['host_name'] = row[1]
			d['machine_id'] = row[2]
			d['interface'] = row[3]
			d['status'] = row[4]
			list_res.append(d)
		connection.commit()
		return jsonify({'results':list_res}),200,{'Access-Control-Allow-Origin': '*'}

	elif request.method == 'PUT':
		print("put request")
		connection = dbConnection()
		cursor = connection.cursor()
		try:
			print("in try")
			host_id = request.json['host_id']
			host_name = request.json['host_name']
			nested_string ="ARRAY["
                        for nested_value in request.json['interface']:
				print("in for")
				nested_string += "("
				nested_string += "'"
				nested_string += str(nested_value['ip'])
				nested_string += "'"
				nested_string += ","
				nested_string += "'"
				nested_string += nested_value['netmask']
				nested_string += "'"
				nested_string += ")::interface_type"
				nested_string += ","
			nested_string = nested_string.rstrip(",")	
			nested_string +=  "]"

			machine_id = request.json['machine_id']
			status = request.json['status']
			print(host_name)
			print str(machine_id)
			print(nested_string)
			print(status)
			cursor.execute("UPDATE host SET host_name='"+host_name+"', machine_id='"+str(machine_id)+"', interface="+nested_string+" , status='"+status+"'  WHERE host_id="+str(host_id))
	
                except Exception,e:
			print("ERROR UPDATING")		
			print str(e)
			connection.rollback()
                        abort(400)

		connection.commit()
		return jsonify({'updated':request.json}),200,{'Access-Control-Allow-Origin': '*'}

@app.route('/api/v1/host/<int:id>',methods=['GET','DELETE'])
def host_operation_by_id(id):
	if request.method == 'GET':
		connection = dbConnection()
		cursor1 = connection.cursor()
		try:
			cursor.execute("select * FROM host WHERE \"host_id\"="+str(id))

		except Exception,e:
                        print(e)
                        print('error occured')
                        abort(404)
		results = cursor.fetchall()
		list_res = []
		for row in results:
			d = collections.OrderedDict()
			d['host_id'] = row[0]
			d['host_name'] = row[1]
			d['machine_id'] = row[2]
			d['interface'] = row[3]
			d['status'] = row[4]
			list_res.append(d)
		connection.commit()
		return jsonify({'results':list_res}),200,{'Access-Control-Allow-Origin': '*'}

	elif request.method == 'DELETE':
		connection = dbConnection()
                cursor = connection.cursor()
		results = []
                try:
                        cursor.execute("select * FROM host WHERE host_id="+str(id))
                        results = cursor.fetchall()
			list_res = []
			for row in results:
				d = collections.OrderedDict()
				d['host_id'] = row[0]
				d['host_name'] = row[1]
				d['machine_id'] = row[2]
				d['interface'] = row[3]
				d['status'] = row[4]
				list_res.append(d)
			cursor.execute("DELETE FROM host WHERE host_id="+str(id))

                except Exception,e:
                        print(e)
                        print('error occured')
                        abort(404)

                connection.commit()
                return jsonify({'deleted':list_res}),200,{'Access-Control-Allow-Origin': '*'}

@app.route('/api/v1/alert', methods = ['GET','POST','PUT'])
def alerts():
	if request.method == 'GET':
                conn = dbConnection()
                cur = conn.cursor()
		
                try:
                        cur.execute("select * FROM alert")
                except:
                        print("Error executing select")
                results = cur.fetchall()
		list_res = []
		for row in results:
			d = collections.OrderedDict()
			d['alert_id'] = row[0]
			d['host_id'] = row[1]
			d['service_id'] = row[2]
			d['message'] = row[3]
			d['detail'] = row[4]
			d['level'] = row[5]
			d['time'] = row[6]
			d['value'] = row[7]
			list_res.append(d)

                return jsonify({'results':list_res}),200,{'Access-Control-Allow-Origin': '*'}

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

                return jsonify({'results':result}),200,{'Access-Control-Allow-Origin': '*'}
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

		return jsonify({'results':res}),201,{'Access-Control-Allow-Origin': '*'}


@app.route('/api/v1/alert/<int:alert_id>', methods=['GET','DELETE'])
def alert_operation_by_id(alert_id):
	if request.method == 'GET':
		conn = dbConnection()
		cur = conn.cursor()

		try:
			cur.execute("select * FROM alert WHERE \"alert_id\"="+str(alert_id))

		except:
			print ('Error while getting data..')
			abort(404)
		
		results = cur.fetchall()
		list_res = []
		for row in results:
			d = collections.OrderedDict()
			d['alert_id'] = row[0]
			d['host_id'] = row[1]
			d['service_id'] = row[2]
			d['message'] = row[3]
			d['detail'] = row[4]
			d['level'] = row[5]
			d['time'] = row[6]
			d['value'] = row[7]
			list_res.append(d)
		conn.commit()

		return jsonify({'data':list_res}),200,{'Access-Control-Allow-Origin': '*'}

	if request.method == 'DELETE':
		conn = dbConnection()
		cur = conn.cursor()

		list_res = []

		try:
			cur.execute("select * FROM alert WHERE \"alert_id\"="+str(alert_id))
			results = cur.fetchall()
			for row in results:
				d = collections.OrderedDict()
				d['alert_id'] = row[0]
				d['host_id'] = row[1]
				d['service_id'] = row[2]
				d['message'] = row[3]
				d['detail'] = row[4]
				d['level'] = row[5]
				d['time'] = row[6]
				d['value'] = row[7]
				list_res.append(d)
			cur.execute("DELETE FROM alert WHERE alert_id = "+str(alert_id))
		except:
			print ('Error while deleting data..')
			abort(404)
		
		conn.commit()

		return jsonify({'data':list_res}),200,{'Access-Control-Allow-Origin': '*'}


@app.route('/welcome')
def greetings():
	return render_template('report.html')

@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/show_report/<int:report_id>')
def show_report(report_id):
	return render_template('report_with_option.html',rep_id=report_id)

@app.route('/show_table/<int:report_id>')
def show_table(report_id):
	return render_template('table.html',rep_id=report_id)

@app.route('/test_submit',methods = ["POST"])
def test_submit():
	if request.method == 'POST':
		if not request.json or not 'host_id' or not 'sub_system_id' or not 'fromDate' or not 'toDate' or not 'time' in request.json:
                        abort(401)
                result = {
			"host_id":request.json['host_id'],
			"sub_system_id":request.json['sub_system_id'],
			"fromDate": request.json['fromDate'].replace("/","-")+":00",
			"toDate": request.json['toDate'].replace("/","-")+":00",
			"time" : request.json['time']
				}

                return jsonify({'results':result}),200,{'Access-Control-Allow-Origin': '*'}

@app.route('/data')
def data():
	client = DataFrameClient(host, port, user, password, dbname)
	data = client.query("select * from cpu  where cpu = 'cpu-total' AND host='etlnode1' limit 10")
	dataframe = data['cpu']
	dict={}
       	dict["usage_idle"]=json.loads(dataframe['usage_idle'].to_json(orient='values'))
        dict["usage_user"]=json.loads(dataframe['usage_user'].to_json(orient='values'))
        dict["usage_softirq"]=json.loads(dataframe['usage_softirq'].to_json(orient='values'))
        dict["usage_system"]=json.loads(dataframe['usage_system'].to_json(orient='values'))
        dict["index"] = dataframe.index.tolist()
        return jsonify(dict),200,{'Access-Control-Allow-Origin': '*'}

if __name__=="__main__":
	app.debug = True
	app.run('127.0.0.1',5000,threaded=True)

