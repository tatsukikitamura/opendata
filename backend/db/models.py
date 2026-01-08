from sqlalchemy import Column, String, Integer, Float, Boolean, Index
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
    train_number = Column(String, index=True)  # Added index!
    weekday_type = Column(String, index=True)
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('ix_departure_lookup', 'train_number', 'station_name', 'weekday_type'),
        Index('ix_station_railway_time', 'station_name', 'railway_name', 'departure_time', 'weekday_type'),
    )

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


# =============================================================================
# Routing Data (Unified Master Data)
# =============================================================================

class Station(Base):
    """
    Unified station master data.
    Stores stations from all operators (JR, Metro, Toei) in a single table.
    """
    __tablename__ = "stations"

    id = Column(String, primary_key=True, index=True)  # e.g., "odpt.Station:JR-East.Chuo.Tokyo"
    name_ja = Column(String, index=True)
    name_en = Column(String)
    railway_id = Column(String, index=True)
    station_code = Column(String, nullable=True) # e.g., "M17"
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

class Railway(Base):
    """
    Unified railway master data.
    """
    __tablename__ = "railways"

    id = Column(String, primary_key=True, index=True) # e.g., "odpt.Railway:JR-East.ChuoRapid"
    name_ja = Column(String, index=True)
    name_en = Column(String)
    operator_id = Column(String, index=True)

class RouteEdge(Base):
    """
    Graph edges for routing.
    Represents a direct connection between two stations.
    Pre-calculated from timetables or GTFS.
    """
    __tablename__ = "route_edges"

    id = Column(Integer, primary_key=True, index=True)
    from_station_id = Column(String, index=True)
    to_station_id = Column(String, index=True)
    time_minutes = Column(Float)  # Cost in minutes
    railway_id = Column(String, index=True) # Owner of this edge (or None for transfers)
    type = Column(String, default="ride") # "ride" or "transfer"


