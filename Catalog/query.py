from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
from tempfile import NamedTemporaryFile
import shutil
import pandas as pd
import csv
import json
import requests

def foo():
    return request.json['inputVar']

app = Flask(__name__)
CORS(app)
CORS(app, support_credentials=True)

@app.route("/login")
@cross_origin(supports_credentials=True)

def login():
  return jsonify({'success': 'ok'})

def update_db(id, v):
    filename = 'db.csv'
    tempfile = NamedTemporaryFile(mode='w', delete=False)

    fields = ['id', 'title', 'category', 'quantity', 'price']

    with open(filename, 'r') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)
        writer = csv.DictWriter(tempfile, fieldnames=fields)
        for row in reader:
            if row['id'] == id:
                row['quantity'] = str(v)
            row = {'id': row['id'], 'title': row['title'], 'category': row['category'], 'quantity': row['quantity'], 'price': row['price']}
            writer.writerow(row)

    shutil.move(tempfile.name, filename)
    return 

def make_json(csvFilePath):
     
    jsonArray = []
     
    # Open a csv reader called DictReader
    csvf = open(csvFilePath, encoding='utf-8')
    csvReader = csv.DictReader(csvf)

    for row in csvReader:
        jsonArray.append(row)
    
    return jsonArray  

@app.route('/query/search/<cat>')
def search(cat):  

    data  = pd.read_csv('db.csv', header=0, delimiter=",")
    data2 = (data[(data.category == cat)])
    data2 = data2.drop(columns=['category', 'quantity', 'price'])
    data2.to_csv('output.csv', index=False)
    return json.dumps((make_json('output.csv')),indent=4)

@app.route('/query/search')
def search_():  

    jsonArray = make_json('db.csv')
    for element in jsonArray: 
        del element['category']
        del element['quantity']
        del element['price']
    return json.dumps(jsonArray,indent=4)

@app.route('/query/info/<id>')
def info(id):  
    
    data  = pd.read_csv('db.csv', header=0, delimiter=",")
    data2 = (data[(data.id == int(id))])
    data2 = data2.drop(columns=['category', 'id'])
    data2.to_csv('output.csv', index=False)
    return json.dumps((make_json('output.csv')),indent=4)

@app.route('/query/info')
def info_():
    jsonArray = make_json('db.csv')
    for element in jsonArray: 
        del element['category']
        del element['id']

    return json.dumps(jsonArray,indent=4)


@app.route('/update/<id>', methods=["PUT"])
def order(id):  

    data  = pd.read_csv('db.csv', header=0, delimiter=",")
    

    if(data[(data.id == int(id))].empty):
        return {"status":"fail, NO such book"}

    q = int(data[(data.id == int(id))]['quantity'])
    jsonArray = make_json('db.csv')
    name = jsonArray[int(id)-1]['title']
    if(q == 0):
        return {"status":"fail, all soled"}
    
    q-=1

    r = requests.put("http://192.168.187.129/alert/"+str(id)+"/"+str(q))
    js = r.json() 

    if(js["status"] == "done"):
        update_db(id,q)
        return {"status":"bought book "+name}
    else:
        return {"status":"failed, somthing went wrong"}


@app.route('/forward/<id>/<q>', methods=["PUT"])
def forward(id, q):  
    update_db(id,int(q))
    return {"status":"done"}

if __name__ == "__main__":
    app.run(debug=True, host='192.168.187.130') 

