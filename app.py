###############################################
# Importing dependencies for comunicating wiht sqlite db
from audioop import avg
import json
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, inspect, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Importing dependencies for data analysis
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt

from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta



################################################
# Database Setup
################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the data into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)
print("123")
# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
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
    """List all available api routes."""
    return (
        f"Welcome to the SQL-Alchemy APP API!<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary."""
    """Return the JSON representation of your dictionary."""
    
    last_measurement = session.query(
        measurement.date).order_by(measurement.date.desc()).first()
    (latest_date, ) = last_measurement
    latest_date = latest_date.date()
    date_year_ago = latest_date - relativedelta(years=1)
    # Query to retreive the data and precipitation scores
    last_year_data = session.query(measurement.date, measurement.prcp).filter(
        measurement.date >= date_year_ago).all()
    
    session.close()

    # Convert the query results to a dictionary
    all_precipication = []
    for date, prcp in last_year_data:
        if prcp != None:
            prcp_dict = {}
            prcp_dict[date] = prcp
            all_precipication.append(prcp_dict)

    # Return JSON representation of dictionary
    return jsonify(all_precipication)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations of the most active station for the last year of data"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Calculate the date 1 year ago from the last data point
    last_measurement = session.query(
        measurement.date).order_by(measurement.date.desc()).first()
    (latest_date, ) = last_measurement
    latest_date = dt.dateime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    last_year_data = latest_date - relativedelta(years=1)

    #Find the most active station
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count().desc()).\
        first()

    # Get the station id of the most active station
    (most_active_station_id, ) = most_active_station
    print(
        f"The station id of the most active station is {most_active_station_id}.")
    
    # Perform a query to retreive the data and temperature scores for the most active station
    last_year_data = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == most_active_station_id).filter(measurement.date >= last_year_data).all()

    session.close()

    # Convert the query result to a dictionary
    all_temperatures = []
    for date, temp in last_year_data:
        if temp != None:
            temp_dict = {}
            temp_dict[date] = temp
            all_temperatures.append(temp_dict)
    # Return the JSON representation of dictionary
    return jsonify(all_temperatures)


@app.route("/api/v1.0/stations")
def stations ():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for stations
    stations = session.query(station.station, station.name,
                            station.latitude, station.longitude, station.elevation).all()
    session.close()

    # Convert the query results to a dictionary
    all_stations = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    # Return the JSON representation of dictionary
    return jsonify(all_stations)

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def determine_temps_daterange(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    """When given the start onlu, calculate TMIN, TAVG, and TMAX for all dates greater than equal to the start date."""
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and the end date inclusive"""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # If we have both start and end date
    if end != None:
        temperature_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).filter(
            measurement.date <= end).all()
    # If we only have a start date
    else:
         temperature_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()

    session.close()

    # Convert the query results to a list
    temperature_list = []
    no_temp_data = False
    for min_temp, avg_temp, max_temp in temperature_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_temp_data = True
        temperature_list.append(min_temp)
        temperature_list.append(avg_temp)
        temperature_list.append(max_temp)

    # Return the JSON representation of dictionary
    if no_temp_data == True:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(temperature_list)

if __name__ == '__main__':
    print("hi")
    app.run(debug=True)
    print("hi")


            


    
