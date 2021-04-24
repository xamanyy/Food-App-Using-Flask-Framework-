# IMPORT FIREBASE PACKAGES AND STUFFS

import firebase_admin
from firebase_admin import credentials, firestore

# IMPORT FLASK AND OTHER PACKAGES FROM FLASK

from flask import Flask, jsonify, request, redirect, abort

import json
import requests

from math import sin, cos, sqrt, atan2, radians


# FLASK INITIALIZATION

app = Flask(__name__)


# FIREBASE INITIALIZATION SETUP

if not firebase_admin._apps:
    cred = credentials.Certificate(
        'food-app.json')
    default_app = firebase_admin.initialize_app(cred)
store = firestore.client()


# FIRST END POINT LOCAL REST API TO STORE JSON DATA OF RESTAURATS INTO FIREBASE

@app.route('/foodapp', methods=["POST"])
# FIRST FUNCTION TO ADD RESTAURANTS
def addRestaurants():
    data = request.get_json(force=True)

# ADDING ALL THE DATA INTO EMPTY DICTIONARY
    dit = {}
    dit["name"] = data.get("name")
    dit["mobile"] = data.get("mobile")
    dit["imageUrl"] = data.get("imageUrl")
    dit["location"] = {
        "lat": data.get("lat"),
        "long": data.get("long")
    }
    dit["rest_type"] = data.get("rest_type")
    dit["rest_id"] = data.get("rest_id")
    dit["created_date"] = firestore.SERVER_TIMESTAMP

# STORING ALL THE DATA INTO COLLECTION CALLED RESTAURANTS
    store.collection("RESTAURANTS").add(dit)

    # RETURN THE RESPONSE INTO JSON FORMAT USING JSONIFY IT IS BEING DONE
    return jsonify({"Response": 200})

# SECOND END POINT LOCAL API TO SEARCH RESTAURANTS BY THEIR ID


@app.route('/searchById', methods=['POST'])
def searchByid():
    data = request.get_json(force=True)
    rest_id = data.get('rest_id')

    rest = []

    docs = store.collection("RESTAURANTS").where(
        "rest_id", "==", rest_id).stream()

    for doc in docs:
        rest.append(doc.to_dict())

        return jsonify("Response", 500, rest)

# SEARCH RESTAURANTS UNDER SOME RANGE


@app.route('/searchByRange', methods=['POST'])
def searchByRange():
    data = request.get_json(force=True)

    docs = store.collection("RESTAURANTS").stream()

    rest_list = []

    R = 6373.0

    myLat = data.get('latitude')
    myLong = data.get('longitude')
    raneg = data.get('rang')

    for singleRestauant in docs:
        dit = singleRestauant.to_dict()
        restLat = dit.get('location').get("lat")
        restLong = dit.get('location').get("long")

        lat2 = radians(myLat)
        lat1 = radians(restLat)
        long2 = radians(myLong)
        long1 = radians(restLong)

        dLat = lat2 - lat1
        dLong = long2 - long1

        a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLong / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        if(distance <= raneg):
            rest_list.append(dit)

    return jsonify({"Responde": 200, "Restaurantlist": rest_list})


# ADDING MENUS TO THE RESTAURANTS

@app.route('/restMenu', methods=['POST'])
def menu():
    data = request.get_json(force=True)
    menuId = data.get('menuId')
    rest_id = data.get('rest_id')
    menuItems = data.get('menuItems')

    dit = {}

    dit['menuId'] = menuId
    dit['rest_id'] = rest_id
    dit['menuItems'] = menuItems
    dit['createDate'] = firestore.SERVER_TIMESTAMP

    docs = store.collection('MENUS').add(dit)

    return jsonify(docs[1].get().id)


# ADD MENU ITEMS IN THE MENU COLLECTION OF FIRESTORE

@app.route('/addmenuItem', methods=['POST'])
def addmenuItems():
    data = request.get_json(force=True)

    menuId = data.get('menuId')
    menuItem = data.get('menuItem')

    doc = store.collection('MENUS').document(menuId)
    doc.update({u'menuItems': firestore.ArrayUnion([menuItem])})

    return jsonify({"Respone": 200})


# RESPONSIBLE FOR RUNNING THE APP IN DEFAULT LOCAL PORT AND HOST
if(__name__ == "__main__"):
    app.run(debug=True)
