from sqlalchemy import ForeignKey, Column, Integer, Float, String, Date, select, update, insert, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from appusermodel import AppUserModel
from actionresult import ActionResult

Base = declarative_base()


class BusinessModel(Base):
    __tablename__ = 'fish_business'
    id = Column(Integer, primary_key=True)
    owner_user_id = Column(String(), ForeignKey("app_user.user_id"), nullable=False)
    avg_price = Column(Float(), nullable=True)
    description = Column(String(), nullable=True)
    rating = Column(Float(), nullable=True)
    business_name = Column(String(), nullable=True)
    products = Column(String(), nullable=True)  # array of offer-IDs keep getting updated
    location = Column(String())
    user_relationship = relationship("AppUserModel", back_populates="app_user")
    # one-to-one relationship -> https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html

    def __repr__(self):
        return f"Business_Data(ID={self.id!r}, User-ID={self.owner_user_id!r}, Average-Price={self.avgprice!r}, Description={self.description!r}," \
               f"Rating={self.rating!r}, Business_Name={self.business_name!r}, Product={self.product!r}, Location={self.location!r})"


def create_business(sqlite_engine, user_id, owner, avg_price, description, rating, businessname, products, location):
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        session = Session(sqlite_engine)
        name, image, weight, location, price, seller = [], [], [], [], [], []
        stmt = insert(BusinessModel).values(BusinessModel.owner_user_id == user_id,
                                            BusinessModel.avg_price == avg_price,
                                            BusinessModel.description == description,
                                            BusinessModel.rating == rating,
                                            BusinessModel.business_name == businessname,
                                            BusinessModel.products == products,
                                            BusinessModel.location == location)
        session.add(stmt)
        session.commit()
        scope_session.remove()
        return ActionResult.SUCCESS
    except Exception as e:
        return_data = [{"Status": ActionResult.FAILURE, "Message": str(e)}]
    return ActionResult.FAILURE


def get_business_by_id(sqlite_engine, user_id):
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        session = Session(sqlite_engine)
        name, image, weight, location, price, seller = [], [], [], [], [], []
        stmt = select(BusinessModel).where(BusinessModel.owner_user_id == user_id)
        for business in session.scalars(stmt):
            name.append(business.name)
            image.append(business.image if business.image is not None else "Not Available")
            weight.append(business.weight if business.weight is not None else "Not Available")
            location.append(business.location)
            price.append(business.price)
            seller.append(business.optional_seller if business.optional_seller is not None else "Not Available")
        business_list = [{"Name": n, "Image": i, "Weight": w, "Location": l, "Price": p, "Seller": s}
                     for n, i, w, l, p, s in zip(name, image, weight, location, price, seller)]
        scope_session.remove()
        return ActionResult.SUCCESS
    except Exception as e:
        return_data = [{"Status": "ERROR", "Message": str(e)}]
    return ActionResult.FAILURE


def update_business_product(sqlite_engine, _user_id, product):
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        session = Session(sqlite_engine)
        stmt = update(BusinessModel).where(BusinessModel.owner_user_id == _user_id).values(product=product)
        result = session.execute(stmt)
        session.commit()
        scope_session.remove()
        return ActionResult.SUCCESS
    except Exception as e:
        return ActionResult.FAILURE


def update_business_rating(sqlite_engine, _user_id, rating):
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        session = Session(sqlite_engine)
        stmt = update(BusinessModel).where(BusinessModel.owner_user_id == _user_id).values(rating=rating)
        result = session.execute(stmt)
        session.commit()
        scope_session.remove()
        return ActionResult.SUCCESS
    except Exception as e:
        return ActionResult.FAILURE


def delete_business():
    pass