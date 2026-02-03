
# Imports

import os
from dotenv import load_dotenv
from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup

# App Setup

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('SQL_HOST')
app.config['MYSQL_USER'] = os.getenv('SQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('SQL_PASS')
app.config['MYSQL_DB'] = os.getenv('SQL_DB')

mysql = MySQL(app)

# Flask Pages

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    
    query = request.args.get("query") or ""

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute(f"SELECT * FROM media WHERE Title LIKE '%{query}%'; ")

    media = cursor.fetchall()

    cursor.close()

    return render_template("index.html", media=media)

@app.route('/add', methods = ['GET','POST'])
def add():
    if request.method == 'GET':
        return render_template("add.html")
    
    else:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        form = request.form
        print(form)
        query = f"INSERT INTO Media (title, url, imgUrl) VALUES ('{form['title']}','{form['url']}','{form['imgUrl']}');"

        cursor.execute(query)

        mysql.connection.commit()

        cursor.close()

        return redirect("/")

@app.route('/edit/<int:id>', methods = ['GET','POST'])
def edit(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(f"SELECT * FROM media WHERE id = {id}")
        mediaItem = cursor.fetchone()

        cursor.close()

        return render_template("edit.html", item=mediaItem)
    
    else:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        form = request.form
        query = f"UPDATE Media SET title='{form['title']}', url='{form['url']}', imgUrl='{form['imgUrl']}' WHERE id = {id};"

        cursor.execute(query)

        mysql.connection.commit()

        cursor.close()

        return redirect("/")

@app.route('/delete/<int:id>', methods = ['GET','POST'])
def delete(id):
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(f"SELECT * FROM media WHERE id = {id}")
        mediaItem = cursor.fetchone()

        cursor.close()

        return render_template("delete.html", item=mediaItem)
    
    else:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        form = request.form
        print(form)
        query = f"DELETE FROM Media WHERE id = {id}"

        cursor.execute(query)

        mysql.connection.commit()

        cursor.close()

        return redirect("/")

# Logic Functions

# Gets IMG via provided URL
@app.route('/getPreviewImg', methods = ['POST'])
def getPreviewImg():
    
    # Get Data
    data = request.get_json()
    url = data.get("url", "") or ""
    imgUrl = ""

    # Try get Preview Img
    try:
        if url:
            html = requests.get(url).text

            parsedHtml = BeautifulSoup(html, features='lxml')

            imgUrl = parsedHtml.find("meta", property="og:image").get("content")

            if imgUrl[0] == "/":
                imgUrl = url + imgUrl

    except Exception as e:
        print(e)
        imgUrl = ""

    print(imgUrl)

    return jsonify({
        "url": imgUrl
    })


app.run(debug=True)