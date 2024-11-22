from flask import Flask, render_template, request, redirect, url_for, session ,jsonify #type: ignore
from flask_cors import CORS #type: ignore
import json
import pymysql #type: ignore
import pandas as pd #type: ignore
from dotenv import load_dotenv #type: ignore
import os
import bcrypt
from datetime import datetime

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('homepage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/homepage')
def homepage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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

    return render_template('homepage.html', user=user)  # Pass user to template
    #return render_template('homepage.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/listingsearch')
def listingsearch():
    return render_template('listingsearch.html')

@app.route('/roommatesearch')
def roommatesearch():
    return render_template('roommatesearch.html')

@app.route('/listings')
def listings():
    return render_template('listings.html')

@app.route('/preferences')
def preferences():
    return render_template('preferences.html')

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
    if 'phone' in data:
         update_query = "UPDATE users SET PhoneNumber = (%s) WHERE UserID = (%s)"
         cursor.execute(update_query, (data.get('phone'), user_id))
    if 'gender' in data:
         update_query = "UPDATE users SET Gender = (%s) WHERE UserID = (%s)"
         cursor.execute(update_query, (data.get('gender'), user_id))
    if 'password' in data:
         hashed_password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt())
         update_query = "UPDATE users SET Password = (%s) WHERE UserID = (%s)"
         cursor.execute(update_query, (hashed_password, user_id))
    
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
    admin = data.get('admin')

    if not email or not password:
        #return jsonify({"error": "Username and password are required"}), 400
        return render_template('login.html', message = "Username and password are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if admin == "true":
        print("true")

        check_admin_exist_query = "SELECT * FROM admins WHERE Email = (%s)"
        cursor.execute(check_admin_exist_query, (email))
        admin = cursor.fetchone()

        if admin is None:
            conn.close()
            return render_template('login.html', message = "Invalid admin account"), 400
        
        conn.close()
        return render_template('homepage.html', message = "Login successful")

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
    return redirect(url_for('homepage'))

@app.route('/logout', methods=['POST'])
def logout():
    # Expire the session cookie manually
    resp = redirect(url_for('login'))
    resp.set_cookie('session', '', expires=datetime(2000, 1, 1))
    session.clear()  # Clear the Flask session data
    return resp

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
        return render_template('listings.html', message = "All fields are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    check_property_exist_query = "SELECT * FROM property WHERE PropertyName = (%s)"
    cursor.execute(check_property_exist_query, (property_name))
    property = cursor.fetchone()

    if property is not None:
        conn.close()
        # change the name to whatever .html file it should be
        return render_template('listings.html', message = "Property already exists"), 400
    
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
    return render_template('listings.html', message = "Account successfully created", property_id = property_id)

@app.route('/delete_property/<int:property_id>', methods = ['POST'])
def delete_property(property_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_property_exist_query = "SELECT * FROM property WHERE PropertyID = (%s)"
    cursor.execute(check_property_exist_query, (property_id))
    property = cursor.fetchone()

    if property is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('property_settings.html', message = "Property does not exist"), 400
    
    delete_query = "DELETE FROM Property WHERE PropertyID = (%s)"
    cursor.execute(delete_query, (property_id))
    conn.commit()
    conn.close()

    return render_template('homepage.html', message = "Property successfully deleted")

@app.route('/update_property/<int:property_id>', methods = ['POST'])
def update_property(property_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    check_property_exist_query = "SELECT * FROM property WHERE PropertyID = (%s)"
    cursor.execute(check_property_exist_query, (property_id))
    property = cursor.fetchone()

    if property is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('property_settings.html', message = "Property does not exist"), 400
    
    data = request.form
    if 'propertyname' in data:
        update_query = "UPDATE property SET PropertyName = (%s) WHERE PropertyID = (%s)"
        cursor.execute(update_query, (data.get('propertyname'), property_id))
    if 'street' in data:
        update_query = "UPDATE property SET Street = (%s) WHERE PropertyID = (%s)"
        cursor.execute(update_query, (data.get('street'), property_id))
    if 'city' in data:
        update_query = "UPDATE property SET City = (%s) WHERE PropertyID = (%s)"
        cursor.execute(update_query, (data.get('city'), property_id))
    if 'state' in data:
        update_query = "UPDATE property SET State = (%s) WHERE PropertyID = (%s)"
        cursor.execute(update_query, (data.get('state'), property_id))
    if 'zipcode' in data:
        update_query = "UPDATE property SET ZipCode = (%s) WHERE PropertyID = (%s)"
        cursor.execute(update_query, (data.get('zipcode'), property_id))
    if 'source' in data:
        update_query = "UPDATE property SET Source = (%s) WHERE PropertyID = (%s)"
        cursor.execute(update_query, (data.get('source'), property_id))
    
    conn.commit()
    conn.close()

    return redirect(url_for('property_settings'))  # This will refresh the page with new data

@app.route('/add_listing/<int:user_id>', methods = ['POST'])
def add_listing(user_id):
    data = request.form
    property_name = data.get('propertyname')
    sq_feet = data.get('squarefeet')
    source = data.get('source')
    price = data.get('price')
    rooms = data.get('rooms')
    title = data.get('title')
    bathrooms = data.get('bathrooms')

    if not all ([property_name, sq_feet, source, price, rooms, title, bathrooms]):
        # change the name to whatever .html file it should be
        return render_template('listings.html', message = "All fields are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    check_property_exist_query = "SELECT PropertyID FROM Property WHERE PropertyName = (%s)"
    cursor.execute(check_property_exist_query, (property_name))
    property_id = cursor.fetchone()

    if property_id is None:
        conn.close()
        # change the name to whatever .html file it should be
        return render_template('listings.html', message = "Property does not exist"), 400 
    
    property_id = property_id[0]

    check_listing_exist_query = """SELECT * FROM listings WHERE OwnerID = (%s) AND PropertyID = (%s) AND 
                                    SquareFeet = (%s) AND Source = (%s) AND Price = (%s) AND 
                                    Rooms = (%s) AND Title = (%s) AND Bathrooms = (%s)"""
    cursor.execute(check_listing_exist_query, (str(user_id), str(property_id), sq_feet, source, price, rooms, title, bathrooms))
    listing = cursor.fetchone()

    if listing is not None:
        conn.close()
        # change the name to whatever .html file it should be
        return render_template('listings.html', message = "Listing already exists"), 400
    
    check_user_exist_query = "SELECT * FROM users WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (str(user_id)))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        # change the name to whatever .html file it should be
        return render_template('listings.html', message = "User not found"), 400
    
    owner_name = user[1] + " " + user[2]

    check_num_listing_query = "SELECT ListingID FROM listings"
    cursor.execute(check_num_listing_query)
    listing = cursor.fetchall()
    listing_id = 0

    if len(listing) > 0:
        listing_id = listing[-1][0] + 1
    else:
        listing_id = 1

    insert_query = "INSERT INTO listings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (str(listing_id), str(user_id), str(property_id), sq_feet, source, price, rooms, title, bathrooms))
    conn.commit()
    conn.close()

    listing_info = {
        "listing_id": listing_id,
        "listing_owner": owner_name,
        "property_name": property_name,
        "listing_title": title,
        "square_feet": sq_feet,
        "rooms": rooms,
        "bathrooms": bathrooms,
        "price": price,
        "source": source
    }

    # change the name to whatever .html file it should be
    return render_template('listings.html', message = "Listing successfully created", listing_id = listing_id, listings = listing_info)

@app.route('/get_listings', methods = ['POST'])
def get_listings():
    conn = get_db_connection()
    cursor = conn.cursor()
    get_listings_query = "SELECT * FROM listings"
    cursor.execute(get_listings_query)
    listings = cursor.fetchall()
    listings_data = []

    for listing in listings:
        listing_id = listing[0]
        owner_id = listing[1]
        property_id = listing[2]

        get_owner_name_query = "SELECT FirstName, LastName FROM users WHERE UserID = (%s)"
        cursor.execute(get_owner_name_query, (str(owner_id)))
        user = cursor.fetchone()
        owner_name = user[0] + " " + user[1]

        get_property_name_query = "SELECT PropertyName FROM property WHERE PropertyID = (%s)"
        cursor.execute(get_property_name_query, (str(property_id)))
        property = cursor.fetchone()
        property_name = property[0]

        title = listing[7]
        sq_feet = listing[3]
        rooms = listing[6]
        bathrooms = listing[8]
        price = listing[5]
        source = listing[4]

        listing_info = {
            "listing_id": listing_id,
            "listing_owner": owner_name,
            "property_name": property_name,
            "listing_title": title,
            "square_feet": sq_feet,
            "rooms": rooms,
            "bathrooms": bathrooms,
            "price": price,
            "source": source
        }

        listings_data.append(listing_info)

    return render_template('listings.html', listings = listings_data)

@app.route('/delete_listing/<int:listing_id>', methods = ['POST'])
def delete_listing(listing_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_listing_exist_query = "SELECT * FROM listings WHERE ListingID = (%s)"
    cursor.execute(check_listing_exist_query, (listing_id))
    listing = cursor.fetchone()

    if listing is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('listings.html', message = "Listing does not exist"), 400
    
    delete_query = "DELETE FROM listings WHERE ListingID = (%s)"
    cursor.execute(delete_query, (listing_id))
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return render_template('homepage.html', message = "Listing successfully deleted")

@app.route('/update_listing/<int:listing_id>', methods = ['POST'])
def update_listing(listing_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    check_listing_exist_query = "SELECT * FROM listing WHERE ListingID = (%s)"
    cursor.execute(check_listing_exist_query, (listing_id))
    listing = cursor.fetchone()

    if listing is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('listings.html', message = "Listing does not exist"), 400
    
    data = request.form
    if 'squarefeet' in data:
        update_query = "UPDATE listing SET SquareFeet = (%s) WHERE ListingID = (%s)"
        cursor.execute(update_query, (data.get('squarefeet'), listing_id))
    if 'source' in data:
        update_query = "UPDATE listing SET Source = (%s) WHERE ListingID = (%s)"
        cursor.execute(update_query, (data.get('source'), listing_id))
    if 'price' in data:
        update_query = "UPDATE listing SET Price = (%s) WHERE ListingID = (%s)"
        cursor.execute(update_query, (data.get('price'), listing_id))
    if 'rooms' in data:
        update_query = "UPDATE listing SET Rooms = (%s) WHERE ListingID = (%s)"
        cursor.execute(update_query, (data.get('rooms'), listing_id))
    if 'title' in data:
        update_query = "UPDATE listing SET Title = (%s) WHERE ListingID = (%s)"
        cursor.execute(update_query, (data.get('title'), listing_id))
    if 'bathrooms' in data:
        update_query = "UPDATE listing SET Bathrooms = (%s) WHERE ListingID = (%s)"
        cursor.execute(update_query, (data.get('bathrooms'), listing_id))
    
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return redirect(url_for('listings'))  # This will refresh the page with new data

@app.route('/view_listing_info/<int:listing_id>', methods = ['POST'])
def view_listing_info(listing_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    check_listing_exist_query = "SELECT * FROM listings WHERE ListingID = (%s)"
    cursor.execute(check_listing_exist_query, (listing_id))
    listing = cursor.fetchone()

    if listing is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('view_listing.html', message = "Listing does not exist"), 400

    get_property_id_query = "SELECT PropertyID, Source FROM listings WHERE ListingID = (%s)"
    cursor.execute(get_property_id_query, (str(listing_id)))
    property = cursor.fetchone()
    property_id = property[0]
    listing_source = property[1]

    get_property_info = "SELECT * FROM property WHERE PropertyID = (%s)"
    cursor.execute(get_property_info, (str(property_id)))
    property = cursor.fetchone()

    property_name = property[1]
    street = property[2]
    city = property[3]
    state = property[4]
    zip_code = property[5]
    property_source = property[6]

    property_info = {
        "property_name": property_name,
        "street": street,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "property_source": property_source,
        "listing_source": listing_source
    }

    review_data = get_review_data(property_id)

    get_listing_interest_query = "SELECT UserID FROM listing_interest WHERE ListingID = (%s)"
    cursor.execute(get_listing_interest_query, (str(listing_id)))
    listing_interest_user = cursor.fetchall()

    user_data = []

    for user in listing_interest_user:
        user_id = user[0]

        get_user_contact_info = "SELECT FirstName, LastName, Email, PhoneNumber FROM users WHERE UserID = (%s)"
        cursor.execute(get_user_contact_info, (str(user_id)))
        user = cursor.fetchone()

        user_name = user[0] + " " + user[1]
        email = user[2]
        phone_number = user[3]

        user_info = {
            "user_id": user_id,
            "user_name": user_name,
            "email": email,
            "phone_number": phone_number
        }
        user_data.append(user_info)
    return render_template('listing_popup.html', property_info = property_info, review_info = review_data, user_info = user_data)

@app.route('/listings', methods = ['POST'])
def manage_your_listings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    get_listings_query = "SELECT * FROM listings WHERE UserID = (%s)"
    cursor.execute(get_listings_query, str(user_id))
    listings = cursor.fetchall()

    listings_data = []

    for listing in listings:
        listing_id = listing[0]
        owner_id = listing[1]
        property_id = listing[2]

        get_owner_name_query = "SELECT FirstName, LastName FROM users WHERE UserID = (%s)"
        cursor.execute(get_owner_name_query, (str(owner_id)))
        user = cursor.fetchone()
        owner_name = user[0] + " " + user[1]

        get_property_name_query = "SELECT PropertyName FROM property WHERE PropertyID = (%s)"
        cursor.execute(get_property_name_query, (str(property_id)))
        property = cursor.fetchone()
        property_name = property[0]

        title = listing[7]
        sq_feet = listing[3]
        rooms = listing[6]
        bathrooms = listing[8]
        price = listing[5]
        source = listing[4]

        listing_info = {
            "listing_id": listing_id,
            "listing_owner": owner_name,
            "property_name": property_name,
            "listing_title": title,
            "square_feet": sq_feet,
            "rooms": rooms,
            "bathrooms": bathrooms,
            "price": price,
            "source": source
        }

        listings_data.append(listing_info)

    return render_template('listings.html', listings = listings_data)

@app.route('/add_review/<int:property_id>/<int:user_id>', methods = ['POST'])
def add_review(property_id, user_id):
    data = request.form
    rating = data.get('rating')
    review_date = data.get('reviewdata')
    review = data.get('review')

    if not all ([rating, review_date, review]):
        # probably need to change the html this refers to
        return render_template('property_review.html', message = "All fields are required"), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    check_property_exist_query = "SELECT * FROM property WHERE PropertyID = (%s)"
    cursor.execute(check_property_exist_query, (property_id))
    property = cursor.fetchone()

    if property is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('property_review.html', message = "Property does not exist"), 400
    
    check_user_exist_query = "SELECT * FROM user WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (user_id))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('property_review.html', message = "User does not exists"), 400
    
    check_num_reviews_query = "SELECT ReviewID FROM reviews"
    cursor.execute(check_num_reviews_query)
    review = cursor.fetchall()

    review_id = 0

    if len(review) > 0:
        review_id = review[-1][0] + 1
    else:
        review_id = 1

    insert_query = "INSERT INTO reviews VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (str(review_id), str(property_id), str(user_id), rating, review_date, review))
    conn.commit()
    review_data = get_review_data(property_id)
    conn.close()
        
    # probably need to change the html this refers to
    return render_template('property_review.html', reviews = review_data, message = "Review added successfully!")   

def get_review_data(property_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    property_query = "SELECT * FROM reviews WHERE PropertyID = (%s)"
    cursor.execute(property_query, (str(property_id)))
    reviews = cursor.fetchall()

    property_name_query = "SELECT PropertyName, Street FROM property WHERE PropertyID = (%s)"
    cursor.execute(property_name_query, (str(property_id)))
    property = cursor.fetchall()
    property_name = property[0][0]
    property_location = property[0][1]

    review_data = {
        "id": property_id,
        "name": property_name,
        "location": property_location,
        "reviews": []
    }

    for i in range(len(reviews)):
        review_id = reviews[i][0]
        user_id = reviews[i][2]
        rating = reviews[i][3]
        date = reviews[i][4].strftime('%Y-%m-%d')
        review = reviews[i][5]

        user_name_query = "SELECT FirstName, LastName FROM users WHERE UserID = (%s)"
        cursor.execute(user_name_query, (str(user_id)))
        user_name = cursor.fetchall()
        name = user_name[0][0] + " " + user_name[0][1]

        reivew_dict = {
            "review_id": review_id,
            "user_id": user_id,
            "user_name": name,
            "date": date,
            "review": review,
            "rating": rating
        }

        review_data['reviews'].append(reivew_dict)

    return review_data

@app.route('/delete_review/<int:review_id>', methods = ['POST'])
def delete_review(review_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_review_exist_query = "SELECT * FROM reviews WHERE ReviewID = (%s)"
    cursor.execute(check_review_exist_query, (review_id))
    review = cursor.fetchone()

    if review is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('property_review.html', message = "Review does not exist"), 400
    
    delete_query = "DELETE FROM reviews WHERE ReviewID = (%s)"
    cursor.execute(delete_query, (review_id))
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return render_template('property_review.html', message = "Review successfully deleted")

@app.route('/update_review/<int:review_id>', methods = ['POST'])
def update_review(review_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    check_review_exist_query = "SELECT * FROM reviews WHERE ReviewID = (%s)"
    cursor.execute(check_review_exist_query, (review_id))
    review = cursor.fetchone()

    if review is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('property_review.html', message = "Review does not exist"), 400
    
    data = request.form
    if 'rating' in data:
        update_query = "UPDATE reviews SET Rating = (%s) WHERE ReviewID = (%s)"
        cursor.execute(update_query, (data.get('rating'), review_id))
    if 'reviewdate' in data:
        update_query = "UPDATE reviews SET ReviewDate = (%s) WHERE ReviewID = (%s)"
        cursor.execute(update_query, (data.get('reviewdate'), review_id))
    if 'description' in data:
        update_query = "UPDATE reviews SET Description = (%s) WHERE ReviewID = (%s)"
        cursor.execute(update_query, (data.get('description'), review_id))
    
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return redirect(url_for('listings'))  # This will refresh the page with new 

@app.route('/add_preferences/<int:user_id>', methods = ['POST'])
def add_preferences(user_id):
    data = request.form
    zip_code = data.get('zipcode')
    budget = data.get('budget')
    rooms = data.get('rooms')
    property_type = data.get('propertytype')
    lease_duration = data.get('leaseduration')

    if not all ([zip_code, budget, rooms, property_type, lease_duration]):
        # probably need to change the html this refers to
        return render_template('add_preferences.html', message = "All fields are required"), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    check_user_exist_query = "SELECT * FROM users WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (str(user_id)))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('add_preferences.html', message = "User does not exist. Create an account"), 400
    
    check_num_preferences_query = "SELECT PreferenceID FROM preferences"
    cursor.execute(check_num_preferences_query)
    preferences = cursor.fetchall()
    preference_id = 0

    if len(preferences) > 0:
        preference_id = preferences[-1][0] + 1
    else:
        preference_id = 1

    insert_query = "INSERT INTO preferences VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (str(preference_id), str(user_id), zip_code, budget, rooms, property_type, lease_duration))
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return render_template('add_preferences.html', message = "Account successfully created", preference_id = preference_id)

@app.route('/delete_preferences/<int:preference_id>', methods = ['POST'])
def delete_preferences(preference_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_preference_exist_query = "SELECT * FROM preferences WHERE PreferenceID = (%s)"
    cursor.execute(check_preference_exist_query, (preference_id))
    preference = cursor.fetchone()

    if preference is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('preferences.html', message = "Preferences do not exist"), 400
    
    delete_query = "DELETE FROM preferences WHERE PreferenceID = (%s)"
    cursor.execute(delete_query, (preference_id))
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return render_template('settings.html', message = "Preferences successfully deleted")

@app.route('/update_preferences/<int:preference_id>', methods = ['POST'])
def update_preferences(preference_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    check_preference_exist_query = "SELECT * FROM preferences WHERE PreferenceID = (%s)"
    cursor.execute(check_preference_exist_query, (preference_id))
    preference = cursor.fetchone()

    if preference is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('preferences.html', message = "Preference does not exist"), 400
    
    data = request.form
    if 'zipcode' in data:
        update_query = "UPDATE preferences SET ZipCode = (%s) WHERE PreferenceID = (%s)"
        cursor.execute(update_query, (data.get('zipcode'), preference_id))
    if 'budget' in data:
        update_query = "UPDATE preferences SET Budget = (%s) WHERE PreferenceID = (%s)"
        cursor.execute(update_query, (data.get('budget'), preference_id))
    if 'rooms' in data:
        update_query = "UPDATE preferences SET Rooms = (%s) WHERE PreferenceID = (%s)"
        cursor.execute(update_query, (data.get('rooms'), preference_id))
    if 'propertytype' in data:
        update_query = "UPDATE preferences SET PropertyType = (%s) WHERE PreferenceID = (%s)"
        cursor.execute(update_query, (data.get('propertytype'), preference_id))
    if 'leaseduration' in data:
        update_query = "UPDATE preferences SET LeaseDuration = (%s) WHERE PreferenceID = (%s)"
        cursor.execute(update_query, (data.get('leaseduration'), preference_id))
    
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return # redirect(url_for('listings'))  # This will refresh the page with new 

@app.route('/add_listing_interest/<int:listing_id>/<int:user_id>', methods = ['POST'])
def add_listing_interest(listing_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    check_listing_exist_query = "SELECT * FROM listings WHERE ListingID = (%s)"
    cursor.execute(check_listing_exist_query, (str(listing_id)))
    listing = cursor.fetchone()

    if listing is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('add_listing_interest.html', message = "Listing does not exist"), 400

    check_user_exist_query = "SELECT * FROM users WHERE UserID = (%s)"
    cursor.execute(check_user_exist_query, (str(user_id)))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('add_preferences.html', message = "User does not exist. Create an account"), 400
    
    check_num_listing_interest_query = "SELECT ListingInterestGroupID FROM listing_interest"
    cursor.execute(check_num_listing_interest_query)
    listing_interest = cursor.fetchall()
    listing_interest_id = 0

    if len(listing_interest) > 0:
        listing_interest_id = listing_interest[-1][0] + 1
    else:
        listing_interest_id = 1

    insert_query = "INSERT INTO preferences VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (str(listing_interest_id), str(listing_id), str(user_id)))
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return render_template('add_listing_interest.html', message = "Listing interest successfully created", listing_interest_id = listing_interest_id)

@app.route('/delete_listing_interest/<int:listing_interest_id>', methods = ['POST'])
def delete_listing_interest(listing_interest_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    check_listing_interest_exist_query = "SELECT * FROM listing_interest WHERE ListingInterestGroupID = (%s)"
    cursor.execute(check_listing_interest_exist_query, (listing_interest_id))
    listing_interest = cursor.fetchone()

    if listing_interest is None:
        conn.close()
        # probably need to change the html this refers to
        return render_template('listing_interests.html', message = "Listing interests do not exist"), 400
    
    delete_query = "DELETE FROM listing_interest WHERE ListingInterestGroupID = (%s)"
    cursor.execute(delete_query, (listing_interest_id))
    conn.commit()
    conn.close()

    # probably need to change the html this refers to
    return render_template('listing_interest.html', message = "Listing interest successfully deleted")

@app.route('/roommate_search', methods = ['POST'])
def roommate_search():
    conn = get_db_connection()
    cursor = conn.cursor()

    get_preferences_query = "SELECT * FROM preferences"
    cursor.execute(get_preferences_query)
    preferences = cursor.fetchall()

    roommate_data = []

    for preference in preferences:
        user_id = preference[1]
        get_user_name_query = "SELECT FirstName, LastName, Email, PhoneNumber, Gender FROM users WHERE UserID = (%s)"
        cursor.execute(get_user_name_query, (str(user_id)))
        user = cursor.fetchone()

        user_name = user[0] + " " + user[1]
        email = user[2],
        phone = user[3],
        gender = user[4],
        zip_code = preference[2]
        budget = preference[3]
        rooms = preference[4]
        property_type = preference[5]
        lease_duration = preference[6]

        roommate_info = {
            "name": user_name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "zip_code": zip_code,
            "budget": budget,
            "rooms": rooms,
            "property_type": property_type,
            "lease_duration": lease_duration
        }

        roommate_data.append(roommate_info)
    return render_template('roommatesearch.html', roommates = roommate_data)

if __name__ == '__main__': 
    app.run(debug = True)