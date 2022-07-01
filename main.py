from flask import Flask, jsonify, request, redirect, url_for
from flask_restful import Api
import flask, traceback, os, requests, json
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, Float, String, Date, select, update, event, text
from sqlalchemy.sql import func
from sqlite_orm import Base, sqlite_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, relationship
# set up a scoped_session -> https://stackoverflow.com/a/18265238/3482140
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
from appusermodel import AppUser
from businessmodel import BusinessModel
from offermodel import OfferModel
from plot_analysis import PlotAnalysis
from actionresult import ActionResult
import telnyx_sms


app = Flask(__name__)
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "eNelayan"
db = SQLAlchemy(app)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
login_manager = LoginManager()
login_manager.init_app(app)
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@app.before_first_request
def create_tables():
    Base.metadata.create_all(sqlite_engine)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return AppUser.get_user(user_id)


class FishModel(Base):
    __tablename__ = 'fish_inventory'
    id = Column(Integer, primary_key=True)
    name = Column(String())
    image = Column(String(), nullable=True)
    weight = Column(String(), nullable=True)
    quantity = Column(String(), nullable=True)
    date_of_posting = Column(Date(), server_default=func.now())
    location = Column(String())
    price = Column(Float)
    optional_seller = Column(String(), nullable=True)

    def __repr__(self):
        return f"Fish_Inventory(id={self.id!r}, name={self.name!r}, image={self.image!r}, weight={self.weight!r}, " \
               f"quantity={self.quantity!r}, location={self.location!r}, price={self.price!r}, seller={self.optional_seller!r}) "


try:
    sqlite_engine.connect()
    Base.metadata.create_all(sqlite_engine)
    print("Connection created successfully!!!")
except OperationalError:
    print("Connection didn't succeed!!!")


def return_response(return_data, status):
    response = flask.make_response(jsonify(return_data))
    response.headers['Access-Control-Allow-Headers'] = '*'
    # response.headers['Access-Control-Allow-Origin'] = '*'
    response.status_code = status
    return response


@app.route("/", methods=['GET'])
@cross_origin()
def homepage():
    if current_user.is_authenticated:
        return_data = [{"Status": "SUCCESS",
                        "Message": "Login using Google's Gmail platform was successful!"}]
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            "<div><p>Your role: {}</p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic, current_user.role
            )
        )
    else:
        return_data = [{"Status": "FAILURE",
                        "Message": "Please login using Google's Gmail credentials!"}]
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/favicon.ico/")
def favicon():
    return "", 200


@app.route("/api/")
def home():
    return "Hurrah! The eNelayan project's API service is accessible!", 200


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
@cross_origin()
def login():
    # Reference from https://realpython.com/flask-google-login/
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]  # + ' ' + userinfo_response.json()["family_name"]
        # Create a user in your db with the information provided
        # by Google
        role = "CUSTOMER"
        user = AppUser(
            id_=unique_id, name=users_name, email=users_email, profile_pic=picture, role=role
        )
        print("Waiting for user-creation in table...")
        # Doesn't exist? Add it to the database.
        if not AppUser.get_user(unique_id):
            result = AppUser.create_user(unique_id, users_name, users_email, picture, "CUSTOMER")
            if result == ActionResult.SUCCESS:
                print("User got created successfully!")
            else:
                print("User was not created! Please try again using a valid Google-verified email address.")
                return redirect(url_for('homepage'))
        # Begin user session by logging the user in
        login_user(user)

        # Send user back to homepage
        return redirect(url_for('homepage'))

    else:
        return_data = "User email not available or not verified by Google."
        return return_response(return_data, 400)


@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('homepage'))


@app.route("/otp/<string:mobile>", methods=['GET'])
@cross_origin()
def get_otp(mobile):
    otp = telnyx_sms.send_sms(mobile)
    if otp != '':
        return_data = "The OTP generated by the application is "+otp
    else:
        return_data = "There is some problem generating the OTP currently. Please try after some time."
    return return_response(return_data, 200)


@app.route('/business', methods=['POST'])
@cross_origin()
def insert_business_data():
    id = request.form.get("id") if "id" in request.form else None
    owner = request.form.get("owner") if "owner" in request.form else None
    avg_price = request.form.get("avgprice") if "avgprice" in request.form else None
    description = request.form.get("description") if "description" in request.form else None
    rating = request.form.get("rating") if "rating" in request.form else None
    business_name = request.form.get("businessname") if "businessname" in request.form else None
    products = request.form.get("products") if "products" in request.form else None
    location = request.form.get("location") if "location" in request.form else None
    try:
        return_data = BusinessModel().create_business(id, owner, avg_price, description, rating, business_name, products, location)
    except Exception as e:
        return_data = [{"Status": "ERROR", "Message": str(e)}]
    return return_response(return_data, 200)


@app.route('/fish', methods=['POST'])
@cross_origin()
def fish_data():
    name = request.form.get("Name")
    image = request.form.get("Image")
    location = request.form.get("Location")
    weight = request.form.get("Weight")
    price = request.form.get("Price")
    seller = request.form.get("Seller")
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        with Session(sqlite_engine) as session:
            fish = FishModel(name=name, image=image, weight=weight, location=location, price=float(price),
                             optional_seller=seller)
            session.add_all([fish])
            session.commit()
        scope_session.remove()
        return_data = [{"Status": "SUCCESS",
                        "Message": "Fish data inserted successfully!"}]
    except Exception as e:
        return_data = [{"Status": "ERROR", "Message": str(e)}]
    return return_response(return_data, 200)


@app.route("/price-analysis/fish/", methods=['GET'])
@cross_origin()
def get_price_data_by_fish_name():
    try:
        query = 'select name, price from fish_inventory'
        b64_string = ''
        b64_string = PlotAnalysis().generate_plots(sqlite_engine, text(query))
        return_data = str(b64_string)
        if str(b64_string) == str(ActionResult.FAILURE):
            raise Exception("Sorry, but the action couldn't be performed")
    except Exception as e:
        print(e)
        return_data = [{"Status": "ERROR", "Message": str(e)}]
    return return_response(return_data, 200)


@app.route("/list/<string:location_name>", methods=['GET'])
@cross_origin()
def get_fish_data_by_location(location_name):
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        session = Session(sqlite_engine)
        name, image, weight, location, price, seller = [], [], [], [], [], []
        stmt = select(FishModel).where(FishModel.location.in_([location_name]))
        for fish in session.scalars(stmt):
            name.append(fish.name)
            image.append(fish.image if fish.image is not None else "Not Available")
            weight.append(fish.weight if fish.weight is not None else "Not Available")
            location.append(fish.location)
            price.append(fish.price)
            seller.append(fish.optional_seller if fish.optional_seller is not None else "Not Available")
        fish_list = [{"Name": n, "Image": i, "Weight": w, "Location": l, "Price": p, "Seller": s}
                     for n, i, w, l, p, s in zip(name, image, weight, location, price, seller)]
        scope_session.remove()
        return return_response(fish_list, 200)
    except Exception as e:
        return_data = [{"Status": "ERROR", "Message": str(e)}]
    return return_response(return_data, 200)


@app.route("/fish/all", methods=['GET'])
@cross_origin()
def get_all_fish_data():
    try:
        session_factory = sessionmaker(bind=sqlite_engine)
        scope_session = scoped_session(session_factory)
        session = Session(sqlite_engine)
        name, image, weight, location, price, seller = [], [], [], [], [], []
        stmt = select(FishModel)
        for fish in session.scalars(stmt):
            name.append(fish.name)
            image.append(fish.image if fish.image is not None else "Not Available")
            weight.append(fish.weight if fish.weight is not None else "Not Available")
            location.append(fish.location)
            price.append(fish.price)
            seller.append(fish.optional_seller if fish.optional_seller is not None else "Not Available")
        fish_list = [{"Name": n, "Image": i, "Weight": w, "Location": l, "Price": p, "Seller": s}
                     for n, i, w, l, p, s in zip(name, image, weight, location, price, seller)]
        scope_session.remove()
        return return_response(fish_list, 200)
    except Exception as e:
        return_data = [{"Status": "ERROR", "Message": str(e)}]
    return return_response(return_data, 200)


@app.errorhandler(Exception)
def server_error(err):
    app.logger.exception(err)
    return str(err), 500


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5050, ssl_context="adhoc")
    # homepage()
