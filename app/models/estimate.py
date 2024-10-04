from sqlalchemy import Boolean, Column, Index, Integer, String

from app.core.database.session import Base
from app.models.mixins import TimeAuditMixin


class Vehicle(Base, TimeAuditMixin):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=True)
    make = Column(String(250), nullable=True)
    model = Column(String(250), nullable=True)
    trim = Column(String(500), nullable=True)
    dealer_name = Column(String(500), nullable=True)
    dealer_street = Column(String(500), nullable=True)
    dealer_city = Column(String(500), nullable=True)
    dealer_state = Column(String(500), nullable=True)
    dealer_zip = Column(String(500), nullable=True)
    listing_price = Column(Integer, nullable=True)
    listing_mileage = Column(Integer, nullable=True)
    used = Column(Boolean, nullable=True)
    certified = Column(Boolean, nullable=True)
    style = Column(String(500), nullable=True)
    driven_wheels = Column(String(500), nullable=True)
    engine = Column(String(500), nullable=True)
    vin = Column(String(500), unique=True, nullable=True)
    fuel_type = Column(String(500), nullable=True)
    exterior_color = Column(String(500), nullable=True)
    interior_color = Column(String(500), nullable=True)
    seller_website = Column(String(500), nullable=True)
    first_seen_date = Column(String(500), nullable=True)
    last_seen_date = Column(String(500), nullable=True)
    dealer_vdp_last_seen_date = Column(String(500), nullable=True)
    listing_status = Column(String(500), nullable=True)


Index("ix_vehicle_make_model", Vehicle.make, Vehicle.model)
Index("ix_vehicle_price_mileage", Vehicle.listing_price, Vehicle.listing_mileage)
