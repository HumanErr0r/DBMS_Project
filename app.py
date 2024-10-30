from flask import Flask, render_template, request, redirect, url_for, jsonify #type: ignore
from flask_cors import CORS #type: ignore
import json
import pymysql #type: ignore
import pandas as pd #type: ignore

app = Flask(__name__)
CORS(app)

def get_db_connection():
    # connect to the MySQL database
    conn = pymysql.connect(
        host = "localhost",
        user = "root",
        #password = "YOUR DB PASSWORD",
        db = "dbms_project"
    )
    return conn

@app.route('/add_user', methods = ['POST'])
def add_user():
    data = request.get_json()
    first_name = data.get('first name')
    last_name = data.get('last name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    gender = data.get('gender')

    if not all ([first_name, last_name, email, password, phone, gender]):
        return jsonify({"error": "All fields are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    check_user_exist_query = "SELECT * FROM users WHERE Email = (%s)"
    cursor.execute(check_user_exist_query, (email))
    user = cursor.fetchone()

    if user is not None:
        conn.close()
        return jsonify({"error": "User already exists"}), 409
    
    insert_query = "INSERT INTO users (UserID, FirstName, LastName, Email, PhoneNumber, Password, Gender) VALUES (%d, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (1, first_name, last_name, email, phone, password, gender))
    conn.commit()
    conn.close()


    # probably need to return id
    return jsonify({"message": "Account successfully created"}), 201

# possibly change the method
@app.route('/delete_user/<int:user_id>', methods = ['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_user_exist_query = "SELECT * FROM users WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (user_id))
    user = cursor.fetchone()

    if user is not None:
        conn.close()
        return jsonify({"error": "User does not exist"}), 409
    
    delete_query = "DELETE FROM Users WHERE UserID = (%s)"
    cursor.execute(delete_query, (user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Account successfully deleted"}), 200

@app.route('/update_user/<int:user_id>', methods = ['PUT'])
def update_user(user_id):
    return

if __name__ == '__main__':
    app.run(debug = True)