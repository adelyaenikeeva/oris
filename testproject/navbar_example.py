from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("navbarexample/index.html")

@app.route("/about")
def about():
    return render_template("navbarexample/about.html")

@app.route("/contact")
def contact():
    return render_template("navbarexample/contact.html")

@app.route("/authorization")
def auth():
    return render_template("navbarexample/authorization.html")

if __name__ == "__main__":
    app.run(port=5501)