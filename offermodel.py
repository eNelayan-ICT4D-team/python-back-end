from sqlalchemy import ForeignKey, Column, Integer, Float, String, Date, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from appusermodel import AppUserModel
from actionresult import ActionResult

Base = declarative_base()


class OfferModel(Base):
    __tablename__ = 'fish_offer'
    oid = Column(Integer, primary_key=True)
    name = Column(String())
    pricePerKilo = Column(Float())
    category = Column(String(), nullable=True)
    description = Column(String(), nullable=True)
    amountOfKilos = Column(Float())
    expiration = Column(Date(), nullable=True)
    user_relationship = relationship("AppUserModel", back_populates="app_user")
    # one-to-one relationship -> https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

    def __repr__(self):
        return f"Offer_Data(Offer-ID={self.oid!r}, Name={self.name!r}, Average-Price={self.name!r}, Description={self.description!r}," \
               f"Rating={self.rating!r}, Business_Name={self.businessname!r}, Product={self.product!r}, Location={self.location!r})"


def create_offer():
    pass


def get_business():
    pass


def update_business():
    pass


def delete_business():
    pass