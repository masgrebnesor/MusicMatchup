from flask import Flask, Response
from flask import render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mymusic.db'
app.secret_key = "flask rocks!"

db = SQLAlchemy(app)


if __name__ == '__main__':
    app.run(debug=True)

