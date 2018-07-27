from flask import Flask, render_template, redirect, request, json, jsonify, url_for
from werkzeug import secure_filename
import csv
import os
import MySQLdb
import time
import datetime
from google.appengine.api import memcache

# These environment variables are configured in app.yaml.
# CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
# CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
# CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

CLOUDSQL_CONNECTION_NAME = "data-visualization-cloud:us-central1:cloud-sql-database"
CLOUDSQL_USER = "root"
CLOUDSQL_PASSWORD = "root"

print("\n Cred :", CLOUDSQL_CONNECTION_NAME, CLOUDSQL_USER)
print("#########\n")

def connect_to_cloudsql():
	# When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
	# will be set to 'Google App Engine/version'.
	if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
		# Connect using the unix socket located at
		# /cloudsql/cloudsql-connection-name.
		cloudsql_unix_socket = os.path.join(
			'/cloudsql', CLOUDSQL_CONNECTION_NAME)

		db = MySQLdb.connect(
			unix_socket=cloudsql_unix_socket,
			user=CLOUDSQL_USER,
			passwd=CLOUDSQL_PASSWORD)

	# If the unix socket is unavailable, then try to connect using TCP. This
	# will work if you're running a local MySQL server or using the Cloud SQL
	# proxy, for example:
	#
	#   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
	#
	else:
		db = MySQLdb.connect(
			host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

	return db

app = Flask(__name__)

db = connect_to_cloudsql()
cursor = db.cursor()
cursor.execute("use my_cloud_db;") 

@app.route('/')
def home():
	return render_template('index.html', script_root = request.script_root)


@app.route('/searchMagnitude', methods=['POST','GET'])
def searchMagnitude():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM quake WHERE mag > " + data['searchWord']+ ";"
		memcache_data = memcache.get(sql)
		if memcache_data is not None:
			result = memcache_data
		else:
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()
			memcache.add(key=sql, value=result, time=3600)
		return jsonify(result)


@app.route('/searchMagnitudeRange', methods=['POST','GET'])
def searchMagnitudeRange():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM quake WHERE mag between " + data['range1'] + " and " + data['range2'] + " and time BETWEEN '"+ data['startDate'] +"' AND '"+ data['endDate'] +"'";
		print(sql)
		memcache_data = memcache.get(sql)
		if memcache_data is not None:
			result = memcache_data
		else:
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()
			memcache.add(key=sql, value=result, time=3600)
		return jsonify(result)

@app.route('/searchMagnitudeIntervals', methods=['POST','GET'])
def searchMagnitudeIntervals():
	if request.method == 'POST':
		data = request.form
		pointer1 = int(data['range1'])
		endPoint = int(data['range2'])
		key = str(data['range1'])+str(data['range2'])+str(data['count'])

		rows = []
		start_time = time.time()
		now = datetime.datetime.now()
		memcache_data = memcache.get(key)
		if memcache_data is not None:
			rows = memcache_data
		else:
			while pointer1 < endPoint :
				pointer2 = pointer1 + 0.1
				result = []

				sql = "SELECT locationSource,time FROM quake WHERE mag between " + str(pointer1)  + " and " + str(pointer2) +" LIMIT 1;"
				cursor.execute(sql)
				row = cursor.fetchone()
				while row:
					row1 = [str(i) for i in row]
					result.append(row1)
					row = cursor.fetchone()

				rows.append(result)

				result = []
				sql = "SELECT Count(*) FROM quake WHERE mag between " + str(pointer1)  + " and " + str(pointer2) +" LIMIT "+data['count']+";"
				print(sql)
				cursor.execute(sql)
				row = cursor.fetchone()
				while row:
					row1 = [str(i) for i in row]
					result.append(row1)
					row = cursor.fetchone()

				rows.append([[pointer1, pointer2],result])

				pointer1 = pointer2 + 0.001
			memcache.add(key=key, value=rows, time=3600)
		total_time = time.time() - start_time
		# print(rows)
		return jsonify(["first select time: " + str(now)]+["total_time: " + str(total_time)] + rows)


@app.route('/searchLocation', methods=['POST','GET'])
def searchLocation():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM(SELECT *,(((acos(sin((" + data['latitude'] + "*(22/7)/180)) * sin((latitude*(22/7)/180))+cos((" + data['latitude'] + "*(22/7)/180)) * cos((latitude*(22/7)/180)) * cos(((" + data['longitude'] + " - longitude)*(22/7)/180))))*180/(22/7))*60*1.1515*1.609344) as distance FROM quake) t WHERE distance <= "+  data['distance']
		print(sql)
		key = str(data['latitude'])+str(data['longitude'])+str(data['distance'])
		memcache_data = memcache.get(key)
		if memcache_data is not None:
			result = memcache_data
		else:
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()
			memcache.add(key=key, value=result, time=3600)
		return jsonify(result)

@app.route('/searchLocationDistance', methods=['POST','GET'])
def searchLocationDistance():
	if request.method == 'POST':
		data = request.form
		res = []
		start_time = time.time()
		key = str(data['latitude'])+str(data['longitude'])
		memcache_data = memcache.get(key)
		if memcache_data is not None:
			result = memcache_data
		else:
			for i in range(1,101,10):
				sql = "SELECT * FROM(SELECT *,(((acos(sin((" + data['latitude'] + "*(22/7)/180)) * sin((latitude*(22/7)/180))+cos((" + data['latitude'] + "*(22/7)/180)) * cos((latitude*(22/7)/180)) * cos(((" + data['longitude'] + " - longitude)*(22/7)/180))))*180/(22/7))*60*1.1515*1.609344) as distance FROM quake) t WHERE distance <= "+  str(i)
				print(sql)
				cursor.execute(sql)
				row = cursor.fetchone()
				result = []
				while row:
					row1 = [str(i) for i in row]
					result.append(row1)
					row = cursor.fetchone()
				res.append({'range': str(i) + " km", 'results': result})
			memcache.add(key=key, value=res, time=3600)
		total_time = time.time() - start_time
	return jsonify(["total_time: " + str(total_time)] + res)
		

@app.route('/searchLocationName', methods=['POST','GET'])
def searchLocationName():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM quake WHERE locationSource = '" + data['name'] + "' and mag between " + data['range1'] + " and " + data['range2'] + ";"
		key = str(data['name'])+str(data['range1'])+str(data['range2'])
		print(sql)
		memcache_data = memcache.get(key)
		if memcache_data is not None:
			result = memcache_data
		else:
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()
			memcache.add(key=key, value=result, time=3600)
		return jsonify(result)
		

@app.route('/searchLocationRange', methods=['POST','GET'])
def searchLocationRange():
	if request.method == 'POST':
		data = request.form
		key = data['latitude1'] + data['latitude2'] + data['longitude1'] + data['longitude2']
		sql = "SELECT * FROM quake WHERE latitude between " + data['latitude1'] + " and " + data['latitude2'] + " and longitude between " + data['longitude1'] + " and " + data['longitude2'] + ";"
		memcache_data = memcache.get(key)
		if memcache_data is not None:
			result = memcache_data
		else:
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()
			memcache.add(key=key, value=result, time=3600)
		return jsonify(result)


if __name__ == '__main__':
	app.run()
