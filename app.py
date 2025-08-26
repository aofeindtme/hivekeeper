from flask import Flask, render_template, request, redirect, url_for, session, g
from datetime import date
import sqlite3
import yaml
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

translations = {}
try:
    with open("config/translations.yaml", encoding="utf-8") as f:
        translations = yaml.safe_load(f)
except FileNotFoundError:
    print("Warning: translations.yaml not found - continue without translations.")
def tr(key):
    lang = g.get("lang", "en")
    return translations.get(lang, {}).get(key, key)
    
# Supported languages
LANGUAGES = {
    "en": "English",
    "de": "Deutsch"
}
    
app.jinja_env.globals.update(tr=tr, LANGUAGES=LANGUAGES, translations=translations)

def load_hives():
    # Beispiel: Dummy-Daten
    return [
        {"id": 1, "name": "Beute A"},
        {"id": 2, "name": "Beute B"},
    ]

@app.before_request
def set_language():
    lang = session.get("lang", "en")
    g.lang = lang

@app.route("/set_language/<lang_code>")
def set_language_route(lang_code):
    if lang_code in LANGUAGES:
        session["lang"] = lang_code
    return redirect(request.referrer or url_for("index"))

with open("config/hivekeeper_entities.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

colony_fields = next(e for e in config["entities"] if e["name"] == "colonies")["fields"]

@app.route("/colonies", methods=["GET", "POST"])
def colonies():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        form_data = {field["name"]: request.form.get(field["name"]) for field in colony_fields}

        conn = sqlite3.connect("data/hivekeeper.db")
        cursor = conn.cursor()

        columns = ", ".join(form_data.keys())
        placeholders = ", ".join(["?"] * len(form_data))
        values = list(form_data.values())

        cursor.execute(f"INSERT INTO colonies ({columns}) VALUES ({placeholders})", values)

        conn.commit()
        conn.close()

        return redirect(url_for("colonies"))

    return render_template("colonies_form.html", fields=colony_fields)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "aofeindt" and request.form["password"] == "150413":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")
    
@app.route("/inspections/new", methods=["GET", "POST"])
def new_inspection():
    if request.method == "POST":
        # Hier kannst du die Formulardaten auswerten und speichern
        data = request.form.to_dict()
        # TODO: speichern in DB
        print("Inspektionsdaten:", data)
        return redirect(url_for("index"))  # oder inspections list
    return render_template(
    "inspections_form.html",
    today=date.today().isoformat(),
    hives=load_hives(),
    translations=translations,
    lang=g.lang
)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))
    
@app.route("/")
def index():
    print(">>> RENDERING index.html from", os.path.abspath("templates/index.html"))
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/test")
def test():
    return "TEST OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
