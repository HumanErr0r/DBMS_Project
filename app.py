from flask import Flask, render_template, request, redirect, url_for, session ,jsonify #type: ignore
from flask_cors import CORS #type: ignore
import json
import pymysql #type: ignore
import pandas as pd #type: ignore
from dotenv import load_dotenv #type: ignore
import os
import bcrypt

app = Flask(__name__)
app.secret_key = 'TheSecretKey'
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

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get current user data from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE UserID = %s", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    # Store in session for easy access in template
    if user:
        session['firstname'] = user[1]
        session['lastname'] = user[2]
        session['email'] = user[3]

    return render_template('settings.html', user=user)  # Pass user to template

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
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if password != confirm_password:
        conn.close()
        #return jsonify({"error": "Passwords do not match"}), 400
        return render_template('signup.html', message = "Passwords do not match"), 400
    
    check_num_users_query = "SELECT UserID FROM users"
    cursor.execute(check_num_users_query)
    user = cursor.fetchall()

    user_id = 0

    if len(user) > 0:
        user_id = user[-1][0] + 1
    else:
        user_id = 1

    insert_query = "INSERT INTO users (UserID, FirstName, LastName, Email, PhoneNumber, Password, Gender) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (str(user_id), first_name, last_name, email, phone, hashed_password, gender))
    conn.commit()
    conn.close()

    return render_template('login.html', message = "Account successfully created", user_id = user_id)


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


@app.route('/update_user/<int:user_id>', methods = ['POST'])
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
        print("Form data received:", request.form)
        update_query = "UPDATE users SET FirstName = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('firstname'), user_id))
    if 'lastname' in data:
        update_query = "UPDATE users SET LastName = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('lastname'), user_id))
    if 'email' in data:
        update_query = "UPDATE users SET Email = (%s) WHERE UserID = (%s)"
        cursor.execute(update_query, (data.get('email'), user_id))
    # if 'phone' in data:
    #     update_query = "UPDATE users SET Phone = (%s) WHERE UserID = (%s)"
    #     cursor.execute(update_query, (data.get('phone'), user_id))
    # if 'gender' in data:
    #     update_query = "UPDATE users SET Gender = (%s) WHERE UserID = (%s)"
    #     cursor.execute(update_query, (data.get('gender'), user_id))
    # if 'password' in data:
    #     hashed_password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt())
    #     update_query = "UPDATE users SET Password = (%s) WHERE UserID = (%s)"
    #     cursor.execute(update_query, (hashed_password, user_id))
    
    # possibly add a check to make sure the new password is confirmed
    conn.commit()
    conn.close()

    #return jsonify({"message": "Account successfully updated"}), 200
    return redirect(url_for('settings'))  # This will refresh the page with new data

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

    confirm_password = str(user[5])

    if not(bcrypt.checkpw(password.encode('utf-8'), confirm_password.encode('utf-8'))):
        conn.close()
        #return jsonify({"error": "Incorrect password"}), 400
        return render_template('login.html', message = "Incorrect password"), 400

    # Store user info in session
    session['user_id'] = user[0]  # Assuming UserID is first column
    session['email'] = user[3]    # Assuming Email is fourth column
    session['name'] = f"{user[1]} {user[2]}"  # Assuming FirstName and LastName are second and third columns

    conn.close()
    return render_template('menu.html', message="Login successful")

@app.route('/add_property', methods = ['POST'])
def add_property():
    data = request.form
    property_name = data.get('propertyname')
    street = data.get('street')
    city = data.get('city')
    state = data.get('state')
    zip_code = data.get('zipcode')
    source = data.get('source')

    if not all ([property_name, street, city, state, zip_code, source]):
        # change the name to whatever .html file it should be
        return render_template('add_property.html', message = "All fields are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    check_property_exist_query = "SELECT * FROM property WHERE PropertyName = (%s)"
    cursor.execute(check_property_exist_query, (property_name))
    property = cursor.fetchone()

    if property is not None:
        conn.close()
        # change the name to whatever .html file it should be
        return render_template('add_property.html', message = "Property already exists"), 400
    
    check_num_property_query = "SELECT PropertyID FROM property"
    cursor.execute(check_num_property_query)
    property = cursor.fetchall()
    property_id = 0

    if len(property) > 0:
        property_id = property[-1][0] + 1
    else:
        property_id = 1

    insert_query = "INSERT INTO property (PropertyID, PropertyName, Street, City, State, ZipCode, Source) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (str(property_id), property_name, street, city, state, zip_code, source))
    conn.commit()
    conn.close()

    # change the name to whatever .html file it should be
    return render_template('property.html', message = "Account successfully created", property_id = property_id)

if __name__ == '__main__':
    app.run(debug = True)