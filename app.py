from flask import Flask, request, redirect, url_for, render_template, abort 
app = Flask(__name__)    

@app.route('/')
def resume():
    return render_template("pages/resume.html", title="Resume")

@app.route('/contacts')
def contacts():
    return render_template("pages/contacts.html", title="Contact")

if __name__ == "__main__":
    app.run()  # Launch built-in web server and run this Flask webapp, debug=True