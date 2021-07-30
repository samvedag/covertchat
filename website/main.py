from flask import Flask, render_template, url_for, redirect, request, session
from flask import flash, jsonify
from client import Client
from threading import Thread
import time

NAME_KEY = 'name'
client = None
messages = []

app = Flask(__name__)
app.secret_key = "samveda"

def disconnect():
    """
    call this before the client disconnects from server
    """
    global client
    if client:
        client.disconnect()
    return "none"

@app.route("/login", methods = ['POST','GET'])
def login():
    """
    displays main login page and handles saving name in session
    :exception POST
    :return: None
    """
    disconnect()
    if request.method == "POST":  # if user input a name
        name = request.form["inputName"]
        if len(name) >= 2:
            session[NAME_KEY] = name
            flash(f'You were successfully logged in as {name}.')
            return redirect(url_for("home"))
        else:
            flash("Name must be longer than 1 character.")

    return render_template("login.html", **{"session": session})


@app.route("/logout")
def logout():
    """
    logs the user out by popping name from session
    :return: None
    """
    session.pop(NAME_KEY, None)
    flash("You were logged out.")
    return redirect(url_for("login"))


@app.route("/")
@app.route("/home")
def home(): 
    """
    displays home page if logged in
    :return: None
    """
    global client
    if NAME_KEY not in session:
        return redirect(url_for("login"))
    client = Client(session[NAME_KEY])
    return render_template("index.html", **{'login':True, 'session':session})

@app.route('/send_message/', methods = ['GET'])
def send_message(url=None):
    """
    called from js to send messages
    :param url:
    """
    global client
    msg = request.args.get('val')
    # print (msg)
    # print ('send clicked') 
    if client:
        client.send_message(msg)
    
    return 'none'


@app.route("/get_messages")
def get_messages():
    return jsonify({'messages':messages})


def update_messages():
    """
    updates the local list of messages
    :return: None
    """
    run = True
    while run:
        time.sleep(0.1)  # update every 1/10 of a second
        if not client:
            continue
        new_messages = client.get_messages()  # get any new messages from client
        # add to local list of messages
        messages.extend(new_messages)
        for msg in new_messages:  # display new messages
            print(msg)
            if msg == "{quit}":
                run = False
                break


if __name__ == "__main__":
    Thread(target=update_messages).start()
    app.run(debug=True)