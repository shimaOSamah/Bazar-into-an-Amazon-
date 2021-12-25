from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
import requests
import re

cach = {}
balanc = {'rep1': 0, 'rep2': 0}

rep1 = "192.168.187.130:5000"
rep2 = "192.168.187.129:5000"

def foo():
    return request.json['inputVar']

app = Flask(__name__)
CORS(app)
CORS(app, support_credentials=True)

@app.route("/login")
@cross_origin(supports_credentials=True)

def login():
  return jsonify({'success': 'ok'})

def addToCach(ky, va):
    if(len(cach) == 10):
        for k, v in cach.items():
            del cach[k]
            break
    cach[ky] = va
    return   

def updateCach(id):
    
    for k in list(cach): 
        y = False  
        x = re.findall('['+id+']+', k)

        if(re.findall("search", k)):
            y = re.findall('['+id+']+', cach[k])

        if(y or x):
            del cach[k]

        elif(k == "info"):
            del cach[k]
    return 

def decide():
    
    if(balanc['rep1'] <= balanc['rep2']):
        balanc['rep1']+=1
        return rep1
        
    else:
        balanc['rep1']+=1
        return rep2



@app.route('/search/<cat>')
def search_api(cat):  
    
    key = 'search/'+cat
    
    if(key in cach):
        res = cach[key]
        del cach[key]
        addToCach(key,res)
        return res

    else:   
        ser = decide()
        r = requests.get("http://"+ser+"/query/search/"+cat)
        addToCach(key, r.text)
        return r.text
        
@app.route('/search')
def search():
    key = 'search'
    
    if(key in cach):
        res = cach[key]
        del cach[key]
        addToCach(key,res)
        return res

    else:
        ser = decide()
        r = requests.get("http://"+ser+"/query/search")
        addToCach(key, r.text)
        return r.text

@app.route('/info/<id>')
def info_api(id):  
    key = 'info/'+id
    
    if(key in cach):
        res = cach[key]
        del cach[key]
        addToCach(key,res)
        return res

    else:
        ser = decide()
        r = requests.get("http://"+ser+"/query/info/"+id)
        addToCach(key, r.text)
        return r.text

@app.route('/info')
def info():  
    key = 'info'
    
    if(key in cach):
        res = cach[key]
        del cach[key]
        addToCach(key,res)
        return res

    else:
        ser = decide()
        r = requests.get("http://"+ser+"/query/info")
        addToCach(key, r.text)
        return r.text

@app.route('/purchase/<id>', methods=["PUT"])
def purchase_api(id): 

    key = "purchase/"+id
    
    if(key in cach):
        res = cach[key]
        del cach[key]
        addToCach(key,res)
        return res

    ser = decide()
    r = requests.put("http://"+ser+"/update/"+id) 
    js = r.json()

    if(js["status"] == "fail, NO such book"):
        addToCach("purchase/"+id, "fail, NO such book")

    else :
        updateCach(id)
    
    return js["status"]

@app.route('/purchase', methods=["PUT"])
def purchase():  
    return "fail, Item ID is needed"


if __name__ == "__main__":
    app.run(debug=True, host='192.168.187.128') 
