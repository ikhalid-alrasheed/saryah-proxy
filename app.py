from flask import Flask, request, jsonify;from flask_sqlalchemy import SQLAlchemy
import enum;import requests;from datetime import datetime as dt
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saryah.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
AD=db.session.add;CM=db.session.commit;FK=db.ForeignKey;RL=db.relationship
C=db.Column;T=db.DateTime;I=db.Integer;S=db.String
class User(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=dt.utcnow)
    apple_id=C(I, nullable=False, unique=True)
    email=C(S)
    full_name=C(S)
    def to_dict(self):
        return {key: getattr(self, key, None) for key in ["id","timestamp","apple_id","email","full_name"]}
class Sex(enum.Enum):
    F = "female";M = "male";O="other"
class DriverIdType(enum.Enum):
    ID="id"; IQAMA="igama"
class Driver(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=dt.utcnow)
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
class CarIdType(enum.Enum):
    CHASSIS = "chassis"; CUSTOMS = "customs"
class Car(db.Model):
    id=C(I, primary_key=True);timestamp=C(T, default=dt.utcnow)
    model=C(S)
    model_year=C(S)
    model_manufacturer=C(S)
    global_id=C(S, unique=True, nullable=False)
    global_id_type=C(db.Enum(CarIdType), nullable=False)
    plate_NO=C(S)
    color=C(S)
    body_type=C(S)
class Application(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=dt.utcnow)
    user_id=C(I, FK("user.id"), nullable=False)
    user=RL("User", foreign_keys=[user_id], backref="applications", lazy=True)
    driver_id=C(I, FK("driver.id"), nullable=False)
    driver=RL("Driver", foreign_keys=[driver_id], backref="applications", lazy=True)
    car_id=C(I, FK("car.id"), nullable=False)
    car=RL('Car', backref='applications', lazy=True)
class Transaction(db.Model):
    id = C(I, primary_key=True);timestamp = C(T, default=dt.utcnow)
    application_id=C(I, FK("application.id"), nullable=False)
    application=RL("Application", backref="transaction", lazy=True)
    epow_id = C(I)
    transaction_at = C(T, default=dt.utcnow)
    subtotal_SAR = C(db.DECIMAL)
    vat_SAR = db.ColumnProperty(0.15 * subtotal_SAR)
    total_SAR = db.ColumnProperty(subtotal_SAR + vat_SAR)
    def to_dict(self):
        keys = ['id', 'request_id', 'transaction_at', 'subtotal_SAR', 'vat_SAR', 'total_sar']
        relation_keys =  ["policy"]
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
class Policy(db.Model):
    id=C(I,primary_key=True);timestamp=C(T, default=dt.utcnow)
    transaction_id = C(I, FK("transaction.id"), nullable=False)
    transaction = RL('Transaction', backref='policy', lazy=True)
    provider = C(S)
    issue_at = C(T)
    effective_at = C(T)
    number = C(S)
    type = C(S)
    def to_dict(self):
        keys = ['id', 'provider', 'issue_at', 'effective_at', 'number', 'type']
        relation_keys =  []
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
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
    r=request.get_json(force=True)
    u=User.query.filter_by(apple_id=r["apple_id"]).first()
    if not u:
        del u;u=User(apple_id=r['apple_id'], email=r["email"], full_name=r["full_name"])
        AD(u);CM()
    return  jsonify(u.to_dict())
@app.route("/application", methods=["POST"])
def application():
    request_data=request.get_json(force=True)
    if ("owner_id" not in request_data) or ("car_id" not in request_data) : return jsonify({})
    req = requests.post("http://127.0.0.1:4999/person",
                        data= '{"person_id": %s ,"car_id": %s }' % (request_data["owner_id"],request_data["car_id"]))
    if req.status_code != 200: return "kyc failed"
    kyc = req.json(); del req
    user = User.query.get(request_data["user_id"])
    car = Car(model=kyc["car"]["model"], model_year=kyc["car"]["model_year"],
              model_manufacturer=kyc["car"]["model_manufacturer"], global_id=request_data["car_id"],global_id_type=CarIdType.CHASSIS,
              plate_NO=kyc["car"]["plate_NO"], color=kyc["car"]["color"], body_type=kyc["car"]["body_type"])
    driver = Driver(first_name=kyc["owner"]["first_name"], last_name=kyc["owner"]["last_name"], sex=kyc["owner"]["sex"],
                    nationality=kyc["owner"]["nationality"], birthday=dt.fromisoformat(kyc["owner"]["birthday"]),
                    email=kyc["owner"]["email"], government_id=request_data["owner_id"],government_id_type=DriverIdType.ID,
                    national_address=kyc["owner"]["national_address"], phone_NO=str(kyc["owner"]["phone_NO"]))
    AD(car);AD(driver)
    new_application = Application(user=user,car=car,driver=driver)
    AD(new_application);CM()
    return f"{new_application}"




if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run(debug=True)
