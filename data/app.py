import numpy as np
import datetime as dt
import pandas as pd
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

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Aloha and Welcome to Hawaii Weather."""
    return (
        f"Aloha Hawaii Weather:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
         )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation"""
    # Query weather precipitation
    results = session.query(Measurement.date,Measurement.prcp).all()

    # Convert list of tuples into normal list
    prcp_by_date = list(np.ravel(results))
    session.close()
    return jsonify(prcp_by_date)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query stations
    results = session.query(Station.station).all()

     # Convert list of tuples into normal list
    stations = list(np.ravel(results))
    session.close()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Temperatures by stations"""
  
    # Query most Active Station
    active = session.query(Measurement.station, func.count(Measurement.id)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.id).desc()).all()
    active_list = list(np.ravel(active))
     
    # Query weather temperatures    
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_list[0]).\
        filter(Measurement.date >= (dt.date(2017,8,23) - dt.timedelta(days=365))).all() 
    tmps = list(np.ravel(results))

    session.close()
    return jsonify(tmps)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end = None):
    if end == None:
        session = Session(engine)
    
        results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
    
        temps = list(np.ravel(results))
        session.close()
        return jsonify(temps)
     
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),\
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
     # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)


