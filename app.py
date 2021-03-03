import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Passenger = Base.classes.passenger


# Flask Setup
app = Flask(__name__)


# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precips():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    test = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    datetest = datetime.strptime(test[0], "%Y-%m-%d").date()
    type(datetest)
    # Starting from the most recent data point in the database. 

    # # Calculate the date one year from the last date in data set.
    year_ago = datetest - dt.timedelta(days=365)
    print(year_ago)
    # Perform a query to retrieve the data and precipitation scores
    datestrings = session.query(Measurement.date).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date).all()

    dates = []
    for onedate in datestrings:
        convert = datetime.strptime(onedate[0], "%Y-%m-%d").date()
        dates.append(convert)

    measurements = session.query(Measurement.prcp).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date).all()

    measures = []
    for onemeasure in measurements:
        measures.append(onemeasure[0])

    precip_dict = {k:v for k,v in zip(dates,measures)}

    session.close()

    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(Passenger.name, Passenger.age, Passenger.sex).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_passengers = []
    for name, age, sex in results:
        passenger_dict = {}
        passenger_dict["name"] = name
        passenger_dict["age"] = age
        passenger_dict["sex"] = sex
        all_passengers.append(passenger_dict)

    return jsonify(all_passengers)


if __name__ == '__main__':
    app.run(debug=True)
