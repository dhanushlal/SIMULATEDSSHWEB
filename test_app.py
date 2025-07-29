from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
    return "Flask is working!"

if _name_ == "_main_":
    app.run()
