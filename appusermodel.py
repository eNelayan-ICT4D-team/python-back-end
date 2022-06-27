from sqlalchemy import ForeignKey, Column, Integer, Float, String, Date, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AppUserModel(Base):
    __tablename__ = 'app_user'
    user_id = Column(String(), primary_key=True)
    name = Column(String())
    email = Column(String())
    profile_pic = Column(String())
    role = Column(String())
    business_relation = relationship("BusinessModel", uselist=False)
    order_relation = relationship("OrderModel")

    def __repr__(self):
        return f"User_Inventory(id={self.id!r}, name={self.name!r}, email={self.email!r}, profile_pic={self.profile_pic!r})"
