import flask
import os
import diskolight

app = flask.Flask(__name__)
disko = diskolight.Diskolight()

@app.route("/")
def home(action="Start"):
    # dont care about login for now
    return flask.render_template('main.html', action=action)
    if not flask.session.get('logged_in'):
        return flask.render_template('login.html')
    else:
        return flask.render_template('main.html', action=action)

@app.route("/login", methods=["POST"])
def login():
    if flask.request.form['password'] == open("pwd.txt").read().strip() and flask.request.form['username'] == 'leddj':
        flask.session["logged_in"] = True
    else:
        flask.flash("You cannot pass!")
    return home()

@app.route("/start", methods=["GET", "POST"])
def start():
    if not flask.session.get("logged_in"):
        return flask.render_template("login.html")
    else:
        if not disko.running:
            disko.start()
            return home("Stop")
        else:
            disko.stop()
            return home("Start")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    return flask.render_template("settings.html")

@app.route("/save", methods=["POST"])
def save():
    print(flask.request.form["bass_r"])
    return home()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host="192.168.2.125", port=80)
