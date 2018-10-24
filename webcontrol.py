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
    # dont care about login for now
    if False and not flask.session.get("logged_in"):
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
    bass_r = disko.bass_r*255
    bass_g = disko.bass_g*255
    bass_b = disko.bass_b*255
    high_r = disko.high_r*255
    high_g = disko.high_g*255
    high_b = disko.high_b*255
    low_min = disko.lowpass_min
    low_max = disko.lowpass_max
    high_min = disko.highpass_min
    high_max = disko.highpass_max
    damping = disko.damping
    return flask.render_template("settings.html", **locals())


@app.route("/save", methods=["POST"])
def save():
    bass_r = float(flask.request.form["bass_r"])
    bass_g = float(flask.request.form["bass_g"])
    bass_b = float(flask.request.form["bass_b"])
    high_r = float(flask.request.form["high_r"])
    high_g = float(flask.request.form["high_g"])
    high_b = float(flask.request.form["high_b"])
    disko.set_bass_rgb(bass_r, bass_g, bass_b)
    disko.set_high_rgb(high_r, high_g, high_b)

    disko.lowpass_min = float(flask.request.form["low_min"])
    disko.lowpass_max = float(flask.request.form["low_max"])
    disko.highpass_min = float(flask.request.form["high_min"])
    disko.highpass_max = float(flask.request.form["high_max"])
    disko.damping = float(flask.request.form["brightness"])

    action = "Stop" if disko.running else "Start"
    return home(action)


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host="192.168.2.125", port=80)
