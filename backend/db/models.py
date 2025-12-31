from sqlalchemy import Column, String, Integer, Float
from .database import Base

class StationDeparture(Base):
    __tablename__ = "station_departures"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, index=True)
    station_name = Column(String, index=True)
    railway_id = Column(String, index=True)
    railway_name = Column(String, index=True)
    direction = Column(String)
    departure_time = Column(String, index=True)
    train_type = Column(String)
    destination_station = Column(String)
    train_number = Column(String)
    weekday_type = Column(String, index=True)

class StationOrder(Base):
    __tablename__ = "station_orders"

    id = Column(Integer, primary_key=True, index=True)
    railway_id = Column(String, index=True)
    railway_name = Column(String, index=True)
    station_id = Column(String, index=True)
    station_name = Column(String, index=True)
    station_index = Column(Integer)

class StationInterval(Base):
    __tablename__ = "station_intervals"

    id = Column(Integer, primary_key=True, index=True)
    from_station = Column(String, index=True)
    to_station = Column(String, index=True)
    railway_name = Column(String, index=True)
    time_minutes = Column(Float)
