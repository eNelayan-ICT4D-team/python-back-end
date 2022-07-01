import traceback
from flask_login import UserMixin
from sqlalchemy import Column, String, select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from actionresult import ActionResult
from sqlite_orm import Base, sqlite_engine


class AppUserModel(Base):
    __tablename__ = 'app_user'
    id = Column(String(), primary_key=True)
    name = Column(String())
    email = Column(String())
    profile_pic = Column(String())
    role = Column(String())

    def __repr__(self):
        return f"User_Inventory(id={self.id!r}, name={self.name!r}, email={self.email!r}, profile_pic={self.profile_pic!r}, role={self.role!r})"


class AppUser(UserMixin):
    def __init__(self, id_, name, email, profile_pic, role):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.role = role

    def __repr__(self):
        return f"User_Inventory(id={self.id!r}, name={self.name!r}, email={self.email!r}, profile_pic={self.profile_pic!r}, role={self.role!r})"

    @staticmethod
    def create_user(_user_id, _name, _email, _profile_pic, _role):
        try:
            session_factory = sessionmaker(bind=sqlite_engine)
            scope_session = scoped_session(session_factory)
            session = Session(sqlite_engine)
            user = AppUserModel(id=_user_id, name=_name, email=_email, profile_pic=_profile_pic, role=_role)
            session.add(user)
            session.commit()
            scope_session.remove()
            print("In create user section.")
            return ActionResult.SUCCESS
        except Exception as e:
            traceback.print_exc()
            return ActionResult.FAILURE

    @staticmethod
    def get_user(_user_id):
        try:
            session_factory = sessionmaker(bind=sqlite_engine)
            scope_session = scoped_session(session_factory)
            session = Session(sqlite_engine)
            stmt = select(AppUserModel).where(AppUserModel.id == _user_id)
            result = session.execute(stmt)
            user_id = ''
            name = ''
            email = ''
            profile_pic = ''
            role = ''
            # print("In get user section.")
            for user in result.scalars():
                user_id = user.id
                name = user.name
                email = user.email
                profile_pic = user.profile_pic
                role = user.role
                # print(user)
            # print("Found values in get user section -> "+user_id + ' '+ role)
            user_object = AppUser(id_=user_id, name=name, email=email, profile_pic=profile_pic, role=role)
            scope_session.remove()
        except Exception as e:
            # print(e)
            traceback.print_exc()
            user_object = None
        return user_object

    @staticmethod
    def update_role_user(_user_id, _role):
        try:
            session_factory = sessionmaker(bind=sqlite_engine)
            scope_session = scoped_session(session_factory)
            session = Session(sqlite_engine)
            stmt = update(AppUserModel).where(AppUserModel.id == _user_id).values(role=_role)
            session.execute(stmt)
            session.commit()
            scope_session.remove()
            return ActionResult.SUCCESS
        except Exception as e:
            return ActionResult.FAILURE

    @staticmethod
    def delete_role_user(_user_id):
        try:
            session_factory = sessionmaker(bind=sqlite_engine)
            scope_session = scoped_session(session_factory)
            session = Session(sqlite_engine)
            stmt = delete(AppUserModel).where(AppUserModel.id == _user_id)
            session.execute(stmt)
            session.commit()
            scope_session.remove()
            return ActionResult.SUCCESS
        except Exception as e:
            return ActionResult.FAILURE
