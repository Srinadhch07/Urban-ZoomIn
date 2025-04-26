import mysql.connector
from flask import Flask,render_template, request,redirect,url_for,session
from dotenv import load_dotenv
import os
load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

def connectDB():
    return mysql.connector.connect(
        host = os.environ.get("DB_HOST"),
        user = os.environ.get("DB_USER"),
        password = os.environ.get("DB_PASSWORD"),
        database = os.environ.get("DB_NAME")
    )
print(os.environ.get("DB_HOST"))
print(os.environ.get("DB_USER"))
print(os.environ.get("DB_PASSWORD"))
print(os.environ.get("DB_NAME"))

# def connectDB():
#     return mysql.connector.connect(
#         host = "localhost",
#         user = "root",
#         password = "M1k5i20perfect",
#         database = "shop"
#     )




# Home page - Displays shops
@app.route('/',methods=['POST','GET'])
def home():
    try:
        connection = connectDB()
        cursor = connection.cursor()
        if request.method == "POST":
            category = request.form["category"]
            if category == "all":
                cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id,CONVERT_TZ(last_updated,'+00:00', '+05:30') AS last_updated FROM store")
            elif category:
                cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id,CONVERT_TZ(last_updated,'+00:00', '+05:30') AS last_updated FROM store WHERE category = %s",(category,))
            else:
                cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id,CONVERT_TZ(last_updated,'+00:00', '+05:30') AS last_updated FROM store")
        else:
            cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id,CONVERT_TZ(last_updated,'+00:00', '+05:30') AS last_updated FROM store")
        shops = cursor.fetchall()

        # Render the shops on the home page
        return render_template('index.html', shops = shops)
    except mysql.connector.errors.IntegrityError:
        return "Retrival error"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# store - displays store details
@app.route('/store_page/<int:store_id>',methods=['POST','GET'])
def store_page(store_id):
     try:
        connection = connectDB()
        cursor = connection.cursor()
        cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category FROM store WHERE id = %s",(store_id,))
        store = cursor.fetchone()
        session["store_id"] = store_id
        category = store[5]
        print(category)
        # Conditions for retrieving data
        if category == "food":
            cursor.execute("SELECT item_name,quantity,price,status,CONVERT_TZ(last_updated,'+00:00', '+05:30') AS last_updated FROM food_items WHERE store_id = %s",(store_id,))
            food_items = cursor.fetchall()
            if food_items:
                session["food_items"] = food_items
            else:
                session["food_items"] = []
            if not store:
                return render_template("store.html", error="No store found with this ID.")
        elif category == "general":
            cursor.execute("SELECT item_name,price,status FROM general_items WHERE store_id = %s",(store_id,))
            general_items = cursor.fetchall()
            if general_items:
                session['general_items'] = general_items
            else:
                session['general_items']=[]
            if not store:
                return render_template("store.html", error="No store found with this ID.")
     except mysql.connector.errors.IntegrityError:
        return render_template("store.html", error="Error retrieving data.")
     finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
     # Render the store details on the store page
     if category=="food":
         return render_template('store.html', store = store,food_items = food_items)
     elif category == "general":
         return render_template('general.html',store=store,general_items= general_items)
     else:
         return render_template('test.html')

# category page - Displays shops based on category
@app.route('/category',methods=['POST','GET'])
def category():
    if request.method == "POST":
        category = request.form["category"]
        try:
            connection = connectDB()
            cursor = connection.cursor()
            if category == "all":
                cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id FROM store")
            elif category:
                cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id FROM store WHERE category = %s",(category,))
            else:
                cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id FROM store")
            shops = cursor.fetchall()
            if not shops:
                return render_template("index.html", error="No shops found in this category.")
        except mysql.connector.errors.IntegrityError:
            return render_template("index.html", error="Error retrieving data.")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()

        return render_template('index.html', shops = shops)
    return render_template('index.html')

# Search Page
@app.route('/search',methods=['POST','GET'])
def search():
    if request.method == "POST":
        search = request.form["search"]
        connection = connectDB()
        cursor = connection.cursor()
        cursor.execute("SELECT shop_name,shop_address,status,busy_time,phone,category,id FROM store WHERE shop_name LIKE %s",('%'+search+'%',))
        shops = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', shops = shops)
    return render_template('index.html')

# # Search Bar in General Category
# @app.route('/search_general',methods=['POST','GET'])
# def search_general():
#     if request.method == "POST":
#         search = request.form["search"]
#         connection = connectDB()
#         cursor = connection.cursor()
#         cursor.execute("SELECT item_name,price,status FROM general_items WHERE item_name LIKE %s ",('%'+search+'%',))
#         items = cursor.fetchall()
#         cursor.close()
#         connection.close()
#         return render_template('general.html', product_items = items)
#     return render_template('general.html')

# Register Page
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        connection = connectDB()
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM store WHERE username = %s",(username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return render_template("register.html", error="Username already exists.")
        password = request.form["password"]
        email = request.form["email"]
        phone = request.form["phone"]
        shop_name = request.form["shop_name"]
        shop_address = request.form["shop_address"]
        category = request.form["category"]

        try:
            cursor.execute("INSERT INTO store (username,password,email,phone,shop_name,shop_address,category) VALUES (%s,%s,%s,%s,%s,%s,%s)",(username,password,email,phone,shop_name,shop_address,category))
            connection.commit()
            return redirect(url_for("login"))
        except mysql.connector.errors.IntegrityError:
            return render_template("register.html", error="Username already exists.")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
    return render_template("register.html")

# Login Page
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        connection = connectDB()
        cursor = connection.cursor()
        # Check if username and password are correct
        try:

            cursor.execute("SELECT username,password FROM store WHERE username = %s AND password = %s",(username,password))
            user = cursor.fetchone()
        except mysql.connector.errors.IntegrityError:
            return render_template("login.html", error="Invalid Credentials.")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
        if user:
            session["username"] = username
            return redirect(url_for('profileOwner'))
        else:
            # return "Invalid credentials. Please Try again !"
            return render_template('login.html', error = "Invalid Credentials. Please Try again !")
    return render_template("login.html")

@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            connection = connectDB()
            cursor = connection.cursor()

            # Check if username and password are correct
            cursor.execute("SELECT username,password FROM admin WHERE username = %s AND password = %s",(username,password))
            user = cursor.fetchone()
        except mysql.connector.errors.IntegrityError:
            return render_template("adminlogin.html", error="Invalid Credentials.")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
        if user:
            session["username"] = username
            return redirect(url_for('admin'))
        else:
            # return "Invalid credentials. Please Try again !"
            return render_template('adminlogin.html', error = "Invalid Credentials. Please Try again !")
    return render_template("adminlogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
    if "username" not in session:
        return redirect(url_for('adminlogin'))
    try:
        connection = connectDB()
        cursor = connection.cursor()

        cursor.execute("SELECT shop_name,username,password,phone FROM store")
        shops = cursor.fetchall()
    except mysql.connector.errors.IntegrityError:
        return render_template("admin.html", error="Error retrieving data.")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template("admin.html",shops = shops)

# Admin fcuntionality to delete store
@app.route('/delete_shop',methods=['POST','GET'])
def delete_shop():
    username = request.form["username"]
    try:
        connection = connectDB()
        cursor = connection.cursor()

        # Delete the store from the database
        cursor.execute("DELETE FROM store WHERE username = %s", (username,))
        connection.commit()
        return redirect("admin")
    except mysql.connector.errors.IntegrityError:
        return render_template("admin.html", error="Error deleting store.")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()


@app.route('/profileOwner', methods=['POST', 'GET'])
def profileOwner():
    if "username" not in session:
        return redirect(url_for('login'))

    username = session["username"]
    store_id = None  # Initialize store_id
    store_category = None  # Initialize store_category

    try:
        connection = connectDB()
        cursor = connection.cursor()
        cursor.execute("SELECT id,category FROM store WHERE username = %s", (username,))
        store_row = cursor.fetchone()

        if not store_row:
            return render_template("profileOwner.html", error="No store found with this username.", username=username, store_id=store_id,store_category=store_category)

        store_id,store_category = store_row
        session["store_id"] = store_id
        session["store_category"] = store_category

        if request.method == "POST":
            status = request.form["status"]
            if status == "busy":
                busy_time = request.form["busy_time"]
                cursor.execute("UPDATE store SET status = %s, busy_time = %s WHERE username = %s", (status, busy_time, username))
            else:
                cursor.execute("UPDATE store SET status = %s, busy_time = NULL WHERE username = %s", (status, username))

            connection.commit()
            return render_template("profileOwner.html", success="Status updated successfully.", username=username, store_id=store_id,store_category=store_category)


    except mysql.connector.errors.IntegrityError:
        return render_template("profileOwner.html", error="Error updating status.",username=username, store_id=store_id,store_category=store_category)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template("profileOwner.html", username=username, store_id=store_id, store_category=store_category)

# Food Category Page
@app.route('/add_or_update_food', methods=['POST'])
def add_or_update_food():
    store_id = request.form["store_id"]
    item_name = request.form["item_name"]
    quantity = request.form["quantity"]
    price = request.form["price"]
    status = request.form["status"]

    try:
        connection = connectDB()
        cursor = connection.cursor()

        # Check if item already exists for the store
        cursor.execute("SELECT id FROM food_items WHERE store_id = %s AND item_name = %s", (store_id, item_name))
        existing = cursor.fetchone()

        if existing:
            # Update existing item
            cursor.execute("""
                UPDATE food_items
                SET quantity = %s, price = %s, status = %s
                WHERE store_id = %s AND item_name = %s
            """, (quantity, price, status, store_id, item_name))
        else:
            # Insert new item
            cursor.execute("""
                INSERT INTO food_items (store_id, item_name, quantity, price, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (store_id, item_name, quantity, price, status))

        connection.commit()

    except mysql.connector.Error as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template("profileOwner.html", success="Updated successfully."  , username=session["username"], store_id=store_id,store_category=session["store_category"])


@app.route('/delete_food_item', methods=['POST'])
def delete_food_item():
    store_id = request.form["store_id"]
    item_name = request.form["item_name"]

    try:
        connection = connectDB()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM food_items WHERE store_id = %s AND item_name = %s", (store_id, item_name))
        connection.commit()

    except mysql.connector.Error as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template("profileOwner.html", success="Deleted  successfully."  , username=session["username"], store_id=store_id,store_category=session["store_category"])

# Genaral Category Page
@app.route('/add_or_update_product', methods=['POST'])
def add_or_update_product():
    store_id = request.form["store_id"]
    item_name = request.form["item_name"]
    
    price = request.form["price"]
    status = request.form["status"]

    try:
        connection = connectDB()
        cursor = connection.cursor()

        # Check if item already exists for the store
        cursor.execute("SELECT id FROM general_items WHERE store_id = %s AND item_name = %s", (store_id, item_name))
        existing = cursor.fetchone()

        if existing:
            # Update existing item
            cursor.execute("""
                UPDATE general_items
                SET  price = %s, status = %s
                WHERE store_id = %s AND item_name = %s
            """, ( price, status, store_id, item_name))
        else:
            # Insert new item
            cursor.execute("""
                INSERT INTO general_items (store_id, item_name, price, status)
                VALUES ( %s, %s, %s, %s)
            """, (store_id, item_name, price, status))

        connection.commit()

    except mysql.connector.Error as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template("profileOwner.html", success="Updated successfully."  , username=session["username"], store_id=store_id,store_category=session["store_category"])


@app.route('/delete_product_item', methods=['POST'])
def delete_product_item():
    store_id = request.form["store_id"]
    item_name = request.form["item_name"]

    try:
        connection = connectDB()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM general_items WHERE store_id = %s AND item_name = %s", (store_id, item_name))
        connection.commit()

    except mysql.connector.Error as e:
        return f"Database error: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return render_template("profileOwner.html", success="Deleted  successfully."  , username=session["username"], store_id=store_id,store_category=session["store_category"])

# Displaying general category
@app.route('/general_page', methods=['POST','GET'])

def general_page():

    return render_template('general.html',error="Connected to general page")

@app.route('/logout')
def logout():
    session.pop("username",None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug = False)



