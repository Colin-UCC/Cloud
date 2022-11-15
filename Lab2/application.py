import requests
import pymysql as db
from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import InputRequired

application = Flask(__name__)
application.config["SECRET_KEY"] = "This-is-my-secret-key"
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"

conn = db.connect(
    host='-----',
    port=3306,
    user='----',
    password='-----',
    db='----',
)

cursor = conn.cursor()
create_table = """
                    CREATE TABLE IF NOT EXISTS Weather 
                    (name varchar(50), temp varchar(50), 
                    description varchar(50))
                    """

cursor.execute(create_table)


def insert_details(name, temperature, description):
    insert_query = """INSERT INTO Weather (name, temp, description) 
                        VALUES (%s, %s, %s)"""
    cursor.execute(insert_query, (name, temperature, description))
    conn.commit()


def get_details():
    get_query = """SELECT * FROM Weather"""
    cursor.execute(get_query)
    return cursor.fetchall()


class CityForm(FlaskForm):
    city = StringField("City:", validators=[InputRequired()])
    submit = SubmitField("Check Weather")


@application.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html")


@application.route('/weather', methods=["GET", "POST"])
def weather():
    if request.method == "GET":
        return render_template("weather.html", city="")
    else:
        form = CityForm()
        if form.validate_on_submit():
            city = form.city.data
        city = request.form["city"]
        city = str(city)
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=d297ff4804bcb7eff8301c03d8b6b5ce'
        r = requests.get(url.format(city)).json()
        weather = {
            'city': city,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        description = r['weather'][0]['description']
        temperature = r['main']['temp']

        insert_details(city, temperature, description)

        return render_template('weather_response.html', city=city, weather=weather)


@application.route('/stats', methods=["GET", "POST"])
def stats():
    cities = get_details()
    return render_template("stats.html", cities=cities)


if __name__ == "__main__":
    application.run()
