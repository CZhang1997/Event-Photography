
from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session
import hashlib
from bson.objectid import ObjectId
import pymongo

app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["photo"]
myusers = mydb["users"]
myitems = mydb["items"]
mycarts = mydb["carts"]

app.secret_key = 'secret key can be anything!'


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html', userLevel = session.get('level'))
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/admin')
def admin():
    if session.get('user'):
        return render_template('admin.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    session.pop('level',None)
    return redirect('/')

@app.route('/showAddItem')
def showAddItem():
    return render_template('addItem.html')

@app.route('/showCarts')
def showCarts():
    return render_template('showCarts.html', userLevel = session.get('level'))

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        password = hashlib.sha1(password.encode()).hexdigest()
        record = myusers.find_one({"email":email})
        record['_id'] = str(record['_id'])
        if record['password'] == password:
            session['user'] = record['_id']
            session['level'] = record['level']
            return redirect('/userHome')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
    except Exception as e:
        return render_template('error.html',error = str(e))


@app.route('/signUp',methods=['POST'])
def signUp():

    # read the posted values from the UI
    name = request.form['inputName']
    email = request.form['inputEmail']
    password = request.form['inputPassword']
    password = hashlib.sha1(password.encode()).hexdigest()
    # validate the received values
    if name and email and password:
        new = {"name": name, "email": email, "password": password, "level": 0}
        _id = myusers.insert_one(new).inserted_id
        print(str(_id))
        session['user'] = str(_id)
        session['level'] = 0
        return json.dumps({'message': 'Video created successfully !', "_id": str(_id)})
    else:
        return json.dumps({'html':'<span>Enter the required fields!</span>'})

@app.route('/items',methods=['POST'])
def addItem():
    # read the posted values from the UI
    try:
        if session.get('user'):
            name = request.form['name']
            available = request.form['available']
            price = request.form['price']
            if price[0] == '$':
                price = float(price[1:])
            newItem = {"name": name , "available": available, "price": price }
            _id = myitems.insert_one(newItem)
            return json.dumps({"message": "add item done"})
        else:
            return json.dumps({"code":404 , "message":"please login first"})

    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/items', methods=['GET'])
def getItems():
    try:
        if session.get('user'):
            response = []
            for record in myitems.find():
                record['_id'] = str(record['_id'])
                response.append(record)
            return json.dumps(response)
        else:
            return json.dumps({"code":404 , "message":"please login first"})
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/users', methods=['PUT'])
def checkUsername():
    email = request.form['inputEmail']
    record = myusers.find_one({"email": email })
    # print(record)
    return json.dumps({"exist": record != None})

@app.route('/items/<id>', methods=['DELETE'])
def deleteItem(id):
    if session.get('user'):
	    query = { '_id':  ObjectId(id) }
	    myitems.delete_one(query)
	    return json.dumps({'message': 'Video deleted successfully !'})
    else:
        return json.dumps({"code":404 , "message":"please login first"})

@app.route('/items/<id>', methods=['PUT'])
def updateItem(id):
    if session.get('user'):
        query = { '_id':  ObjectId(id) }
        name = request.form['name']
        available = request.form['available']
        price = request.form['price']
        if price[0] == '$':
            price = float(price[1:])
        newItem ={"$set": {"name": name , "available": available, "price": price }}
        myitems.update_one(query, newItem)
        return json.dumps({'message': 'Video deleted successfully !'})
    else:
        return json.dumps({"code":404 , "message":"please login first"})

@app.route('/carts',methods=['POST'])
def addCarts():
    # read the posted values from the UI
    try:
        if session.get('user'):
            itemId = request.form['id']
            userId = session.get('user')
            newItem = {"itemId": itemId, "userId": userId}
            _id = mycarts.insert_one(newItem)
            return json.dumps({"message": "add carts done"})
        else:
            return json.dumps({"code":404 , "message":"please login first"})

    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/carts', methods=['GET'])
def getCarts():
    try:
        if session.get('user'):
            userId = session.get('user')
            response = []
            for record in mycarts.find({"userId": userId}):
                record['_id'] = str(record['_id'])
                itemId = record["itemId"]
                item = myitems.find_one({"_id": ObjectId(itemId)})
                if item == None:
                    continue
                record["name"] = item["name"]
                record["available"] = item["available"]
                record["price"] = item["price"]
                response.append(record)
            return json.dumps(response)
        else:
            return json.dumps({"code":404 , "message":"please login first"})
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/carts/<id>', methods=['DELETE'])
def deleteCartsItem(id):
	query = { '_id':  ObjectId(id) }
	mycarts.delete_one(query)
	return json.dumps({'message': 'cart item deleted successfully !'})

if __name__ == "__main__":
    app.run()
