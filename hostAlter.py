from flask import Flask,request,jsonify,abort
import psycopg2

app = Flask(__name__)

def connect_to_db():
	connecting_string = 'dbname=testdb user=postgres password=ipvision123 host=localhost'
	try:
		return psycopg2.connect(connecting_string) 
	except:
		print ('can not connect to db')

@app.route('/api/host',methods=['GET','POST','PUT','DELETE'])
def host_operation():
	if request.method == 'POST':
		try:
			host_name = request.json['host_name']
			nested_string ="ARRAY["
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

			connection = connect_to_db()
			cursor = connection.cursor()
			cursor.execute("INSERT INTO host (host_name, machine_id, interface , status) VALUES ('"+host_name+"' , '"+str(machine_id)+"' , "+nested_string+" , '"+status+"');")
			
                except Exception,e:
			
			print(e)
                        abort(404)
		connection.commit()
		return jsonify(request.json),200

	elif request.method == 'GET':
		connection = connect_to_db()
		cursor = connection.cursor()
		
		try : 
			cursor.execute("select array_to_json(array_agg(host)) FROM host;")
		except Exception,e:
			print(e)
			print('error occured')
			abort(404)

		results = cursor.fetchall()
		#result_values=[]
		#for row in results:
		#	dict_value = collections.OrderDict()
		#	dict_value['host_id']
		#	dict_value['machine_id']
		#	dict_value[]
		connection.commit()
		return jsonify({'results':results}),200

	elif request.method == 'PUT':
		print("put request")
		connection = connect_to_db()
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
		return jsonify({'updated':request.json}),200

@app.route('/api/host/<int:id>',methods=['GET','DELETE'])
def operation_by_id(id):
	if request.method == 'GET':
		connection = connect_to_db()
		cursor = connection.cursor()
		try:
			cursor.execute("select array_to_json(array_agg(host)) FROM host WHERE \"host_id\"="+str(id))

		except Exception,e:
                        print(e)
                        print('error occured')
                        abort(404)
		results = cursor.fetchall()
		connection.commit()
		return jsonify({'results':results}),200

	elif request.method == 'DELETE':
		connection = connect_to_db()
                cursor = connection.cursor()
		results = []
                try:
                        cursor.execute("select array_to_json(array_agg(host)) FROM host WHERE host_id="+str(id))
                        results = cursor.fetchall()
			cursor.execute("DELETE FROM host WHERE host_id="+str(id))

                except Exception,e:
                        print(e)
                        print('error occured')
                        abort(404)

                connection.commit()
                return jsonify({'deleted':results}),200

app.debug=True
app.run('hdf1',5000)
