import ctypes.wintypes

from flask import Flask, request, jsonify;from flask_sqlalchemy import SQLAlchemy
import enum;import requests;from datetime import datetime as dt
app=Flask(__name__);app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saryah.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;db=SQLAlchemy(app)
AD=db.session.add;CM=db.session.commit;FK=db.ForeignKey;RL=db.relationship
C=db.Column;T=db.DateTime;I=db.Integer;S=db.String
class User(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, server_default=db.func.now())
    apple_id=C(I, nullable=False, unique=True)
    email=C(S)
    full_name=C(S)
    def to_dict(self):
        return {key: getattr(self, key, None) for key in ["id","timestamp","apple_id","email","full_name"]}
class Sex(enum.Enum):F="female";M="male";O="other"
class DriverIdType(enum.Enum):ID="id";IQAMA="igama"
class Driver(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=db.func.now())
    first_name=C(S)
    last_name=C(S)
    sex=C(db.Enum(Sex), nullable=False, default=Sex.O)
    nationality=C(S)
    birthday=C(T)
    email=C(S)
    government_id=C(S, unique=True, nullable=False)
    government_id_type=C(db.Enum(DriverIdType), nullable=False)
    national_address=C(S)
    phone_NO=C(S, unique=True)
class CarIdType(enum.Enum):CHASSIS="chassis";CUSTOMS="customs"
class Car(db.Model):
    id=C(I, primary_key=True);timestamp=C(T, default=db.func.now())
    model=C(S)
    model_year=C(S)
    model_manufacturer=C(S)
    global_id=C(S, unique=True, nullable=False)
    global_id_type=C(db.Enum(CarIdType), nullable=False)
    plate_NO=C(S)
    color=C(S)
    body_type=C(S)
class Application(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=db.func.now())
    user_id=C(I, FK("user.id"), nullable=False)
    user=RL("User", foreign_keys=[user_id], backref="applications", lazy=True)
    driver_id=C(I, FK("driver.id"), nullable=False)
    driver=RL("Driver", foreign_keys=[driver_id], backref="applications", lazy=True)
    car_id=C(I, FK("car.id"), nullable=False)
    car=RL('Car', backref='applications', lazy=True)
class Transaction(db.Model):
    id = C(I, primary_key=True);timestamp = C(T, default=db.func.now())
    application_id=C(I, FK("application.id"), nullable=False)
    application=RL("Application", backref="transaction", lazy=True)
    epow_id = C(I)
    transaction_at = C(T, default=db.func.now())
    subtotal_halalah = C(I)
    vat_halalah = db.ColumnProperty(0.15 * subtotal_halalah)
    total_halalah = db.ColumnProperty(subtotal_halalah + vat_halalah)
class Policy(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=db.func.now())
    transaction_id = C(I, FK("transaction.id"), nullable=False)
    transaction = RL('Transaction', backref='policy', lazy=True)
    provider = C(S)
    issue_at = C(T)
    effective_at = C(T)
    number = C(S)
    type = C(S)
def entity_from_json(model:db.Model, json):
    columns:[db.Column]=model.__dict__["__table__"].columns;entity=model()
    for column in columns:
        c_name = column.name
        if c_name in json:
            if type(column.type)==db.Enum:
                column_enum = {l.value:l.name for l in column.type.__dict__["_valid_lookup"]
                               if type(type(l)) == enum.EnumMeta}
                entity.__setattr__(c_name, column_enum[json[c_name]])
            elif type(column.type)==db.DateTime: entity.__setattr__(c_name, dt.fromisoformat(json[c_name]))
            else: entity.__setattr__(c_name, json[c_name])
    return entity
# routs
@app.route('/login', methods=['POST'])
def login():
    r=request.get_json(force=True)
    u=User.query.filter_by(apple_id=r["apple_id"]).first()
    if not u:
        return jsonify({})
    return  jsonify(u.to_dict())
@app.route('/sign_up', methods=['POST'])
def sign_up():
    request_data=request.get_json(force=True)
    u=User.query.filter_by(apple_id=request_data["apple_id"]).first()
    if not u:
        del u;u=entity_from_json(User, request_data)
        AD(u);CM()
    return  jsonify(u.to_dict())
@app.route("/application", methods=["POST"])
def application():
    request_data=request.get_json(force=True)
    req = requests.post("http://127.0.0.1:4999/person",
                        data= '{"government_id": %s ,"car_id": %s }' % (request_data["government_id"],request_data["car_id"]))
    if req.status_code != 200: return "kyc failed"
    kyc = req.json();del req
    user=User.query.filter_by(apple_id = request_data["apple_id"]).first()
    car=entity_from_json(Car, dict(kyc["car"], **request_data))
    driver = entity_from_json(Driver, dict(kyc["driver"], **request_data))
    new_application=Application(user=user,car=car,driver=driver)
    AD(new_application);CM()
    return f"{new_application}"

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run(debug=True)
