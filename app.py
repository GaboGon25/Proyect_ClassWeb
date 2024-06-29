from flask import Flask, render_template, redirect, request

app= Flask(__name__)

#INDEX
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        pass
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        pass
    else:
        return render_template("register.html")
    
@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        pass
    else:
        return render_template("create.html")
    
@app.route("/courses", methods=["POST", "GET"])
def courses():
    if request.method == "POST":
        pass
    else:
        return render_template("courses.html")
    
@app.route("/courses_details", methods=["POST", "GET"])
def courses_details():
    if request.method == "POST":
        pass
    else:
        return render_template("courses_details.html")
    
@app.route("/categories", methods=["POST", "GET"])
def categories():
    if request.method == "POST":
        pass
    else:
        return render_template("categories.html")

if __name__ == '__main__':
    app.run(debug=True)

