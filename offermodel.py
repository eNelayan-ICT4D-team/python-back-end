from sqlalchemy import ForeignKey, Column, Integer, Float, String, Date, select, update
from sqlalchemy.orm import Session, relationship
import traceback
from flask_login import UserMixin
from sqlalchemy import Column, String, select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from actionresult import ActionResult
from sqlite_orm import Base, sqlite_engine


class OfferModel(Base):
    __tablename__ = 'fish_offer'
    oid = Column(Integer, primary_key=True)
    name = Column(String(), ForeignKey("fish_business.business_name"), nullable=False)
    pricePerKilo = Column(Float())
    category = Column(String(), nullable=True)
    description = Column(String(), nullable=True)
    amountOfKilos = Column(Float())
    expiration = Column(Date(), nullable=True)
    fish_business = relationship("BusinessModel", backref="fish_business")

    # one-to-one relationship -> https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

    def __repr__(self):
        return f"Offer_Data(Offer-ID={self.oid!r}, Name={self.name!r}, Average-Price={self.name!r}, Description={self.description!r}," \
               f"Rating={self.rating!r}, Business_Name={self.businessname!r}, Product={self.product!r}, Location={self.location!r})"


def create_offer():
    pass


def get_offer():
    pass


def update_offer():
    pass


def delete_offer():
    pass
