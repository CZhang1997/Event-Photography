
from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session

from bson.objectid import ObjectId
import pymongo

app = Flask(__name__)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["photo"]
myusers = mydb["users"]
myitems = mydb["items"]
mycarts = mydb["carts"]

# mysql = MySQL()

# # MySQL configurations
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
# app.config['MYSQL_DATABASE_DB'] = 'TodoList'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['MYSQL_DATABASE_PORT'] = 3306
# mysql.init_app(app)

# pip3 install flask-mysql
# use todolist;
# drop table tbl_user;
# CREATE TABLE tbl_user( userid INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(30) , email VARCHAR(30),password VARCHAR(30));
# CREATE TABLE tbl_todo( id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(30) , description VARCHAR(60), userid int(11), isComplete boolean);

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
        return render_template('userHome.html', username = session.get('name'))
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showAddItem')
def showAddItem():
    return render_template('addItem.html')

@app.route('/showCarts')
def showCarts():
    return render_template('showCarts.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        record = myusers.find_one({"email":email})
        record['_id'] = str(record['_id'])
        if record['password'] == password:
            session['user'] = record['_id']
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

    # validate the received values
    if name and email and password:
        new = {"name": name, "email": email, "password": password, "level": 0}
        _id = myusers.insert_one(new)
        session['user'] = _id
        return json.dumps({'message': 'Video created successfully !', "_id": _id})
    else:
        return json.dumps({'html':'<span>Enter the required fields!</span>'})

@app.route('/addItem',methods=['POST'])
def addItem():
    # read the posted values from the UI
    try:
        if session.get('user'):
            name = request.form['name']
            available = request.form['available']
            price = request.form['price']
            newItem = {"name": name , "available": available, "price": price }
            _id = myitems.insert_one(newItem)
            return json.dumps({"message": "add item done"})
        else:
            return json.dumps({"code":404 , "message":"please login first"})

    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/getItems', methods=['GET'])
def getTodoList():
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


@app.route('/addCarts',methods=['POST'])
def addCarts():
    # read the posted values from the UI
    try:
        if session.get('user'):
            # name = request.form['name']
            # available = request.form['available']
            # price = request.form['price']
            itemId = request.form['id']
            userId = session.get('user')
            # newItem = {"name": name , "available": available, "price": price, "itemId": itemId, "userId": userId }
            newItem = {"itemId": itemId, "userId": userId}
            _id = mycarts.insert_one(newItem)
            return json.dumps({"message": "add carts done"})
        else:
            return json.dumps({"code":404 , "message":"please login first"})

    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/getCarts', methods=['GET'])
def getCarts():
    try:
        if session.get('user'):
            userId = session.get('user')
            response = []
            for record in mycarts.find({"userId": userId}):
                record['_id'] = str(record['_id'])
                itemId = record["itemId"]
                item = myitems.find_one({"_id": ObjectId(itemId)})
                record["name"] = item["name"]
                record["available"] = item["available"]
                record["price"] = item["price"]
                response.append(record)
            return json.dumps(response)
        else:
            return json.dumps({"code":404 , "message":"please login first"})
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/deleteCartItem/<id>', methods=['DELETE'])
def deleteVideo(id):
	query = { '_id':  ObjectId(id) }
	mycarts.delete_one(query)
	return json.dumps({'message': 'cart item deleted successfully !'})

if __name__ == "__main__":
    app.run()
