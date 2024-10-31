from flask import Flask, render_template, request, redirect, url_for, jsonify #type: ignore
from flask_cors import CORS #type: ignore
import json
import pymysql #type: ignore
import pandas as pd #type: ignore
from dotenv import load_dotenv #type: ignore
import os

app = Flask(__name__)
CORS(app)

load_dotenv()

def get_db_connection():
    # connect to the MySQL database
    conn = pymysql.connect(
        host = os.getenv('DB_HOST'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
        db = os.getenv('DB_NAME')
    )
    return conn

@app.route('/')
def start():
    return render_template('homepage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/add_user', methods = ['POST'])
def add_user():
    data = request.form
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    email = data.get('email')
    phone = data.get('phone')
    gender = data.get('gender')
    password = data.get('password')
    confirm_password = data.get('password2')

    if not all ([first_name, last_name, email, phone, gender, password, confirm_password]):
        #return jsonify({"error": "All fields are required"}), 400
        return render_template('signup.html', message = "All fields are required"), 400

    
    conn = get_db_connection()
    cursor = conn.cursor()

    check_user_exist_query = "SELECT * FROM users WHERE Email = (%s)"
    cursor.execute(check_user_exist_query, (email))
    user = cursor.fetchone()

    if user is not None:
        conn.close()
        #return jsonify({"error": "User already exists"}), 409
        return render_template('signup.html', message = "User already exists"), 400

    
    if password != confirm_password:
        conn.close()
        #return jsonify({"error": "Passwords do not match"}), 400
        return render_template('signup.html', message = "Passwords do not match"), 400
    
    # need to figure out what to do about obtaining the id to give
    insert_query = "INSERT INTO users (UserID, FirstName, LastName, Email, PhoneNumber, Password, Gender) VALUES (%d, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (1, first_name, last_name, email, phone, password, gender))
    conn.commit()
    conn.close()

    # probably need to return id
    #return jsonify({"message": "Account successfully created"}), 201
    return render_template('homepage.html', message = "Account successfully created")


# possibly change the method
@app.route('/delete_user/<int:user_id>', methods = ['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_user_exist_query = "SELECT * FROM users WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (user_id))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        #return jsonify({"error": "User does not exist"}), 409
        # probably need to change the html this refers to
        return render_template('signup.html', message = "User does not exist"), 400
    
    delete_query = "DELETE FROM Users WHERE UserID = (%s)"
    cursor.execute(delete_query, (user_id))
    conn.commit()
    conn.close()

    #return jsonify({"message": "Account successfully deleted"}), 200
    return render_template('homepage.html', message = "Account successfully deleted")


@app.route('/update_user/<int:user_id>', methods = ['PUT'])
def update_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_user_exist_query = "SELECT * FROM users WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (user_id))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        #return jsonify({"error": "User does not exist"}), 409
        # probably need to change the html this refers to
        return render_template('signup.html', message = "User does not exist"), 400
    
    data = request.form
    if 'firstname' in data:
        update_query = "UPDATE users SET FirstName = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('firstname'), user_id))
    if 'lastname' in data:
        update_query = "UPDATE users SET LastName = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('lastname'), user_id))
    if 'email' in data:
        update_query = "UPDATE users SET Email = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('email'), user_id))
    if 'phone' in data:
        update_query = "UPDATE users SET Phone = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('phone'), user_id))
    if 'gender' in data:
        update_query = "UPDATE users SET Gender = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('gender'), user_id))
    if 'password' in data:
        update_query = "UPDATE users SET Password = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('password'), user_id))
    
    # possibly add a check to make sure the new password is confirmed
    conn.commit()
    conn.close()

    #return jsonify({"message": "Account successfully updated"}), 200
    return render_template('homepage.html', message = "Account successfully updated")

@app.route('/sign_in', methods = ['POST'])
def sign_in():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        #return jsonify({"error": "Username and password are required"}), 400
        return render_template('login.html', message = "Username and password are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    check_user_exist_query = "SELECT * FROM users WHERE Email = (%s)"
    cursor.execute(check_user_exist_query, (email))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        #return jsonify({"error": "Incorrect email or password"}), 400
        return render_template('login.html', message = "Incorrect email or password"), 400

    confirm_password = user[5]

    if password != confirm_password:
        conn.close()
        #return jsonify({"error": "Incorrect password"}), 400
        return render_template('login.html', message = "Incorrect password"), 400

    conn.close()
    #return jsonify({"message": "Login successful"}), 200
    return render_template('login.html', message = "Login successful")

if __name__ == '__main__':
    app.run(debug = True)