# import packages

from flask import Flask, render_template, request, redirect, session, flash
import flaskybot_train
import mysql.connector
import os
import pymongo
import datetime
import speech_recognition as sr
import pyttsx3

###################-------------- creating sessions------------------------------------------ ##########################

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)

###################################------------------MYSQL---------------------########################################

conn = mysql.connector.connect(host="localhost", user="root", password="", database="login_validation")
cursor = conn.cursor()


###################------------------rendering first page LOGIN PAGE---------------------##############################

@app.route('/')
def login():
    return render_template('login.html')


#############----------------If LOGIN successful then go to index page-------------------##############################

@app.route("/home")
def home():
    if 'user_id' in session:
        return render_template("/index.html")
    else:
        return redirect('/')


#############---------------- sending and retrieving data and storing in MONGODB -------------------####################

@app.route("/get")
def get_bot_response():
    client = pymongo.MongoClient(
        "mongodb+srv://demo:demo@cluster0.kll4c.mongodb.net/chat_bot?retryWrites=true&w=majority"
    )

    myDb = client['chat_bot']
    myDbCol = myDb["qus_ans_data"]
    userText = request.args.get('msg')
    myDict = {
        "user_data": userText,
        "bot_data": str(flaskybot_train.chat_response(userText)),
        "date": datetime.datetime.now()
    }
    x = myDbCol.insert_one(myDict)

    # reply with voice
    botResponse = flaskybot_train.chat_response(userText)
    engine = pyttsx3.init()
    rate = engine.getProperty("rate")
    engine.setProperty("rate", 80)
    engine.say(botResponse)
    client.close()
    engine.runAndWait()
    return str(botResponse)


##########################---------------- AFTER CLICKING MIC : VOICE  -------------------##############################

@app.route('/speech', methods=["POST"])
def speech():
    if request.method == "POST":
        r = sr.Recognizer()
        engine = pyttsx3.init()

        with sr.Microphone() as source:
            audio = r.listen(source)

            try:
                userText = request.args.get('msg')
                text = r.recognize_google(audio)
                if text in str(flaskybot_train.chat_response(userText)):
                    reply = userText
                    rate = engine.getProperty("rate")
                    engine.setProperty("rate", 100)
                    engine.say(reply)
                    engine.runAndWait()
                    return render_template('index.html')

            except:
                error = "Sorry, can't read"
                engine.say(error)
                engine.runAndWait()
                return render_template('index.html')
    else:
        return render_template('index.html')


###############################----------------LOGIN_VALIDATION--------------------#####################################

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')
    cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s ", (email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['user_id'] = users[0][0]
        flash('Logged in Successfully!')
        return redirect('/home')
    else:
        flash('Entered Details already exists or are  invalid ')
        return redirect('/')


###########################---------------- RENDERING REGISTER PAGE -------------------#################################

@app.route('/register')
def register():
    return render_template('register.html')


#############################---------------- NEW  REGISTRATION -------------------####################################

@app.route('/register_validation', methods=['POST'])
def register_validation():
    name = request.form.get('namereg')
    email = request.form.get('emailreg')
    password = request.form.get('passwordreg')

    if not len(password) >= 5:
        flash('Password must be at least 5 characters in length')
        return render_template('register.html')
    else:
        cursor.execute("INSERT INTO user (id,name,email,password) VALUES (NULL,%s,%s,%s)", (name, email, password))

        conn.commit()
        conn.close()

        return render_template('index.html')

################################------------------LOGOUT---------------#################################################

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

#########################################------MAIN-----------##########################################################

if __name__ == "__main__":
    app.run(debug=True)