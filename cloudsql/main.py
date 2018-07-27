# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import os
import socket
import time

from flask import Flask, render_template, redirect, request, json, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import numpy as np
from sklearn.cluster import KMeans


app = Flask(__name__)


def is_ipv6(addr):
    """Checks if a given address is an IPv6 address."""
    try:
        socket.inet_pton(socket.AF_INET6, addr)
        return True
    except socket.error:
        return False


# [START example]
# Environment variables are defined in app.yaml.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime())
    user_ip = db.Column(db.String(46))

    def __init__(self, timestamp, user_ip):
        self.timestamp = timestamp
        self.user_ip = user_ip

@app.route('/home')
def home():
    return render_template('index.html', script_root = request.script_root)



@app.route('/searchMagnitudeRange', methods=['POST','GET'])
def searchMagnitudeIntervals():
    if request.method == 'POST':
        data = request.form
        pointer1 = int(data['range1'])
        endPoint = int(data['range2'])
        res = [["range","count"]]
        start_time = time.time()
        now = datetime.datetime.now()
        while pointer1 < endPoint :
            pointer2 = pointer1 + 0.5
            # sql = "SELECT TOP "+data['count']+" * FROM earthquake WHERE mag between " + str(pointer1+0.001)  + " and " + str(pointer2) +" and CONVERT(datetime,LEFT(time,10),126) BETWEEN '"+ data['startDate'] +"' AND '"+ data['endDate'] +"';"
            sql = "SELECT count(*) FROM earthquake WHERE mag between " + str(pointer1+0.001)  + " and " + str(pointer2) +" and CAST(time as DATETIME) BETWEEN '"+ data['startDate'] +"' AND '"+ data['endDate'] +"';"
            
            print(sql)
            rows= db.engine.execute(sql)
            result = []
            for row in rows:
                row1 = [int(i) for i in row]
                result.append(row1)

            res.append([str([pointer1, pointer2]),result[0][0]])

            pointer1 = pointer2
        total_time = time.time() - start_time
        # print(rows)
        return jsonify({"first select time": str(now),"total_time": str(total_time),"result": res})


@app.route('/ageInterval', methods=['POST','GET'])
def ageInterval():
    if request.method == 'POST':
        data = request.form
        rangei = int(data['range1'])
        pointer1 = 0
        endPoint = 100
        res = [["range","count"]]
        start_time = time.time()
        now = datetime.datetime.now()
        while pointer1 < endPoint :
            if not pointer1:
                pointer2 = pointer1 + rangei
            else:
                pointer2 = pointer1 + rangei - 1
            # sql = "SELECT TOP "+data['count']+" * FROM earthquake WHERE mag between " + str(pointer1+0.001)  + " and " + str(pointer2) +" and CONVERT(datetime,LEFT(time,10),126) BETWEEN '"+ data['startDate'] +"' AND '"+ data['endDate'] +"';"
            sql = "SELECT count(*) FROM minnow WHERE age between " + str(pointer1)  + " and " + str(pointer2) +";"
            
            print(sql)
            rows= db.engine.execute(sql)
            result = []
            for row in rows:
                row1 = [int(i) for i in row]
                result.append(row1)

            res.append([str([pointer1, pointer2]),result[0][0]])

            pointer1 = pointer2+1
        total_time = time.time() - start_time
        # print(rows)
        return jsonify({"first select time": str(now),"total_time": str(total_time),"result": res})


@app.route('/visualizeData', methods=['POST','GET'])
def visualizeData():
    if request.method == 'POST':
        data = request.form
        k = int(data['kclusters'])
        rows = db.engine.execute("SELECT " + data['xaxis']+ "," + data['yaxis']+ " FROM titanic3 WHERE " + data['xaxis']+ " IS NOT NULL and " + data['yaxis']+ " IS NOT NULL;") 
        result = []
        X = []
        for row in rows:
            row = list(row)
            X.append(row)

        kmeans = KMeans(n_clusters=k).fit(X)
        centroids = kmeans.cluster_centers_

        print(centroids)
        kmeans_transform = kmeans._transform(X).tolist()
        point_distance = []
        clusters = [[] for i in range(k)]
        for i in range(len(X)):
            c_index = kmeans_transform[i].index(min(kmeans_transform[i]))
            clusters[c_index].append(X[i])
            temp = {"point":X[i], "distance_from_centroid":kmeans_transform[i]}
            point_distance.append(temp)

        return jsonify({"centroids":centroids.tolist(),"pointDistances":point_distance, "clusters": clusters})


@app.route('/percentInfo', methods=['POST','GET'])
def percentInfo():
    if request.method == 'POST':
        data = request.form
        k = int(data['kclusters'])
        rows = db.engine.execute("Select T1.pclass, T1.S, T2.NS from (SELECT pclass,count(pclass) as S FROM titanic3 WHERE sex = '"+data['sex']+"' WHERE survived = 1 Group by pclass) as T1 INNER JOIN (SELECT pclass,count(pclass) as NS FROM titanic3 WHERE sex = '"+data['sex']+"' WHERE survived = 0 Group by pclass) as T2 on T1.pclass = T2.pclass") 
        result = [["PClass","Survived","Not Survived"]]
        for row in rows:
            row1 = [int(i) for i in row]
            result.append(row1)

       
        return jsonify({"result": result})


@app.route('/')
def index():
    user_ip = request.remote_addr

    # Keep only the first two octets of the IP address.
    if is_ipv6(user_ip):
        user_ip = ':'.join(user_ip.split(':')[:2])
    else:
        user_ip = '.'.join(user_ip.split('.')[:2])

    visit = Visit(
        user_ip=user_ip,
        timestamp=datetime.datetime.utcnow()
    )

    db.session.add(visit)
    db.session.commit()

    visits = Visit.query.order_by(sqlalchemy.desc(Visit.timestamp)).limit(10)

    results = [
        'Time: {} Addr: {}'.format(x.timestamp, x.user_ip)
        for x in visits]

    output = 'Last 10 visits:\n{}'.format('\n'.join(results))

    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
# [END example]


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
