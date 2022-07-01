import traceback
from flask_login import UserMixin
from sqlalchemy import ForeignKey, Column, String, Integer, Float, Date, select, update, delete
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from actionresult import ActionResult
from sqlite_orm import Base, sqlite_engine


class OrderModel(Base):
    __tablename__ = 'customer_order'
    orderid = Column(Integer, primary_key=True)
    oid = Column(Integer, ForeignKey("fish_offer.oid"), nullable=False)
    name = Column(String(), ForeignKey("fish_business.business_name"), nullable=False)
    remarks = Column(String(), nullable=True)
    rating = Column(Integer(), nullable=True)
    amountOfKilos = Column(Float())
    fish_offer = relationship("OfferModel", backref="fish_offer")

    def __repr__(self):
        return f"Offer_Data(Offer-ID={self.oid!r}, Name={self.name!r}, Average-Price={self.name!r}, Description={self.description!r}," \
               f"Rating={self.rating!r}, Business_Name={self.businessname!r}, Product={self.product!r}, Location={self.location!r})"


def create_order():
    pass


def get_order():
    pass


def update_order():
    pass


def delete_order():
    pass