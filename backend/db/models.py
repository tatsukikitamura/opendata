from sqlalchemy import Column, String, Integer, Float, Boolean
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


# =============================================================================
# Train Status (from odpt:TrainInformation API)
# =============================================================================

class TrainStatus(Base):
    """
    Records train operation status from odpt:TrainInformation API.
    Each record represents the status of a railway line at a specific point in time.
    """
    __tablename__ = "train_statuses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, index=True)        # Collection time (ISO format, JST)
    railway_id = Column(String, index=True)       # e.g., "odpt.Railway:JR-East.ChuoRapid"
    railway_name = Column(String, index=True)     # e.g., "ChuoRapid" or "中央線快速"
    operator = Column(String)                     # e.g., "odpt.Operator:JR-East"
    status = Column(String)                       # e.g., "平常運転", "運行情報あり", "お知らせ"
    status_text = Column(String)                  # Detailed description (delay reason, etc.)
    is_delayed = Column(Boolean, default=False, index=True)  # True if not normal operation

