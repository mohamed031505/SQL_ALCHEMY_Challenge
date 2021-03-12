import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request
import datetime as dt
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement=Base.classes.measurement
station=Base.classes.station
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#List all routes that are available.

@app.route("/")
def Home():
    """List all available api routes."""
    return (
            f"Welcome to my API" + "\n"
            f"Available Routes<br/>" + "\n"
            f"/api/v1.0/precipitation<br/>" + "\n"
            f"/api/v1.0/stations<br/>" + "\n"
            f"/api/v1.0/tobs<br/>" + "\n"
            f"/api/v1.0/start<br/>"  + "\n"
            f"/api/v1.0/start/enddate<br/>" + "\n"
            f"Start and end date should be in 'YYYY-MM-DD' format"
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_data = session.query(measurement.date, measurement.prcp).all()
    dict_prcp = dict(prcp_data)
    session.close()
    return jsonify(dict_prcp)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(station.station).all()
    session.close()
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = last_date[0]
    year, month, day = map(int, last_date.split("-"))
    year_ago = dt.date(year, month, day) - dt.timedelta(days=365)
    year_ago = (year_ago.strftime("%Y-%m-%d"))
    tobs = session.query(measurement.date, measurement.tobs).all()
    session.close()
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    data_list = []
    
    data = session.query(measurement.date,func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).filter(measurement.date>=start).all()
    
    session.close()
    for data in data:
        dict = {}
        dict["Date"] = data[0]
        dict["Tmin"] = data[1]
        dict["Tavg"] = round(data[2],1)
        dict["Tmax"] = data[2]
        data_list.append(dict)


    return jsonify(data_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    data_list=[]
    session = Session(engine)

    data = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()

    session.close()
    for data in data:
        dict = {}
        dict["Date"] = data[0]
        dict["Tmin"] = data[1]
        dict["Tavg"] = round(data[2],1)
        dict["Tmax"] = data[2]
        data_list.append(dict)


    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)
