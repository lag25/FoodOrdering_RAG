from sqlalchemy import Column, Integer, String, Boolean
try:
    from database import Base
except:
    from .database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer,primary_key = True, index= True)
    name = Column(String, index=True)
    address = Column(String,index=True)
    google_maps_link = Column(String,index=True)
    description = Column(String,index=True)

class Foods(Base):
    __tablename__ = "foods"

    id = Column(Integer,primary_key=True,index=True)
    restaurant_id = Column(Integer,index=True)
    name = Column(String, index=True)
    description = Column(String,index=True)
    price = Column(Integer, index = True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    first_name = Column(String,index=True)
    last_name = Column(String,index=True)
    email = Column(String,index=True)
    address = Column(String,index=True)
    phone = Column(Integer,index=True)
    eat_nv = Column(Boolean,index=True)  #Non Veg Preference


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer,primary_key=True,index=True)
    dish_details = Column(String,index=True)
    customer_first_name = Column(String,index=True)
    customer_last_name = Column(String,index=True)
    customer_address = Column(String,index=True)
    restaurant_name = Column(String,index=True)
    time = Column(String,index=True)
    date = Column(String,index=True)
