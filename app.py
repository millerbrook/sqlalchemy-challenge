import numpy as np
from datetime import datetime as dt
import datetime
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
Measurement = Base.classes.measurement
Station = Base.classes.station


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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/"

    )


@app.route("/api/v1.0/precipitation")
def precips():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to retrieve the last 12 months of precipitation data. 
    # Starting from the most recent data point in the database. 

    test = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    datetest = dt.strptime(test[0], "%Y-%m-%d").date()
   
    # Calculate the date one year from the last date in data set.
    year_ago = datetest - datetime.timedelta(days=365)
    year_ago = year_ago.strftime('%y-%m-%d')
    # Perform a query to retrieve the data and precipitation scores
    datestrings = session.query(Measurement.date).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date).all()

    dates = []
    for onedate in datestrings:
        dates.append(onedate[0])

    measurements = session.query(Measurement.prcp).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date).all()

    measures = []
    for onemeasure in measurements:
        measures.append(onemeasure[0])

    precip_dict = {dates[i]:measurements[i] for i in range(len(dates))}

    session.close()

    return jsonify(precip_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Station.station)

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tempObs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Rank stations by count in descending order
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    #Choose first station
    most_active_station = station_counts[0][0]
    #Query dates and temps associated with this station
    #Note it repeats lots of earlier query process--is this what is wanted?
    # Design a query to retrieve the last 12 months of precipitation data. 
    test = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    datetest = dt.strptime(test[0], "%Y-%m-%d").date()
   
    # Calculate the date one year from the last date in data set.
    year_ago = datetest - datetime.timedelta(days=365)
    year_ago = year_ago.strftime('%y-%m-%d')
    # Perform a query to retrieve the data and precipitation scores
    datestrings = session.query(Measurement.date).\
        filter(Measurement.date > year_ago).\
        filter(Measurement.station == most_active_station).\
        order_by(Measurement.date).all()

    dates = []
    for onedate in datestrings:
        dates.append(onedate[0])

    # Starting from the most recent data point in the database. 

    temperatures = session.query(Measurement.tobs).\
        filter(Measurement.date > year_ago).\
        filter(Measurement.station == most_active_station).\
        order_by(Measurement.date).all()

    temp_list = []
    for onetemp in temperatures:
        temp_list.append(onetemp[0])

    activeStation_dict = {dates[i]:temp_list[i] for i in range (len(dates))}

    #Close out the session
    session.close()

    return jsonify(activeStation_dict)
    
@app.route("/api/v1.0/<start>")
def sinceStart(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Queries to calculate TMIN, TAVG, and TMAX since start date
    #use func
    try:
        maxTemp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).first()
    except: 
        maxTemp = "Sorry I didn't recognize the dates"
    try:
        minTemp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).first()
    
    except:
        minTemp = ""
    
    try:
        avgTemp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).first()
    except:
        avgTemp = ""

    #Close out the session
    session.close()

    return f"Since {start}, maximum Temperature is {maxTemp}, minimum temperature is {minTemp}, and average temperature is {avgTemp}" 

@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Queries to calculate TMIN, TAVG, and TMAX since start date
    #use func
    try:
        maxTemp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    except:
        maxTemp = "Sorry I didn't recognize the dates"
    try:
        minTemp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    except:
        minTemp = ""
    try:
        avgTemp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    except:
        avgTemp = ""

    #Close out the session
    session.close()

    return f"Between {start} and {end}, maximum Temperature is {maxTemp}, minimum temperature is {minTemp}, and average temperature is {avgTemp}"

if __name__ == '__main__':
    app.run(debug=True)
