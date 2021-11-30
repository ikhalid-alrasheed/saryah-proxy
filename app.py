from flask import Flask, request, jsonify;from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
import requests
app=Flask(__name__);app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saryah.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;db=SQLAlchemy(app);from datetime import datetime as dt
Ad=db.session.add;Cm=db.session.commit;Fk=db.ForeignKey;Rl=db.relationship
C=db.Column;DT=db.DateTime;I=db.Integer;S=db.String
class User(db.Model):
    id=C(I,primary_key=True);timestamp=C(DT,default=dt.utcnow())
    apple_id=C(I, nullable=False, unique=True)
    email=C(S)
    full_name=C(S(40))
    def to_dict(self):
        return {key: getattr(self, key, None) for key in ["id","timestamp","apple_id","email","full_name"]}
class Driver(db.Model):
    id=C(I,primary_key=True);timestamp=C(DT,default=dt.utcnow())
    first_name=C(S(40))
    last_name=C(S(40))
    sex=C(S(1))
    nationality=C(S(40))
    birthday=C(DT)
    email=C(S)
    government_id=C(S(12), unique=True)
    government_id_type=C(S(12)) # eqamah or ahwal
    national_address=C(S)
    phone_NO=C(S(13), unique=True)
    @hybrid_property
    def age(self): return (dt.utcnow() - self.birthday).days // 365
class Car(db.Model):
    id=C(I, primary_key=True);timestamp=C(DT,default=dt.utcnow())
    model=C(S(40))
    model_year=C(S(4))
    model_manufacturer=C(S(20))
    chassis_NO=C(S(25), unique=True)
    customs_id=C(S(25), unique=True)
    plate_NO=C(S(25))
    color=C(S)
    body_type=C(S)
class Application(db.Model):
    id=C(I,primary_key=True);timestamp=C(DT,default=dt.utcnow())
    user_id=C(I, Fk("user.id"), nullable=False)
    user=Rl("User", foreign_keys=[user_id], backref="applications", lazy=True)
    driver_id=C(I, Fk("driver.id"), nullable=False)
    driver=Rl("Driver", foreign_keys=[driver_id], backref="applications", lazy=True)
    car_id=C(I, Fk("car.id"), nullable=False)
    car=Rl('Car', backref='applications', lazy=True)
class Transaction(db.Model):
    id = C(I, primary_key=True);timestamp = C(DT, default=dt.utcnow())
    application_id=C(I, Fk("application.id"), nullable=False)
    appilication=Rl("Application", backref="transaction", lazy=True)
    epow_id = C(I)
    transaction_at = C(DT, default=dt.utcnow)
    subtotal_SAR = C(db.DECIMAL)
    vat_SAR = db.ColumnProperty(0.15 * subtotal_SAR)
    total_SAR = db.ColumnProperty(subtotal_SAR + vat_SAR)
    def to_dict(self):
        keys = ['id', 'request_id', 'transaction_at', 'subtotal_SAR', 'vat_SAR', 'total_sar']
        relation_keys =  ["policy"]
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
class Policy(db.Model):
    id=C(I,primary_key=True);timestamp=C(DT,default=dt.utcnow())
    transaction_id = C(I, Fk("transaction.id"), nullable=False)
    transaction = Rl('Transaction', backref='policy', lazy=True)
    provider = C(S(15))
    issue_at = C(DT)
    effective_at = C(DT)
    number = C(S(25))
    type = C(S(10))
    def to_dict(self):
        keys = ['id', 'provider', 'issue_at', 'effective_at', 'number', 'type']
        relation_keys =  []
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
# routs
@app.route('/login', methods=['POST'])
def login():
    R=request.get_json(force=True)
    U=User.query.filter_by(apple_id=R["apple_id"]).first()
    if not U:
        return jsonify({})
    return  jsonify(U.to_dict())
@app.route('/sign_up', methods=['POST'])
def sign_up():
    R=request.get_json(force=True)
    U=User.query.filter_by(apple_id=R["apple_id"]).first()
    if not U:
        del U;U=User(apple_id=R['apple_id'], email=R["email"], full_name=R["full_name"])
        Ad(U);Cm()
    return  jsonify(U.to_dict())
@app.route("/application", methods=["POST"])
def application():
    #TODO: get owner id and car id numbers
    R=request.get_json(force=True)
    if ("owner_id" not in R) or ("car_id" not in R) : return jsonify({})
    req = requests.post("http://127.0.0.1:4999/person", data= '{"person_id": %s ,"car_id": %s }' % (R["owner_id"],
                                                                                               R["car_id"]))
    if req.status_code != 200: return "kyc failed"
    kyc = req.json(); del req
    user = User.query.get(R["user_id"])
    print(user)
    car = Car(model=kyc["car"]["model"],model_year=kyc["car"]["model_year"],
              model_manufacturer=kyc["car"]["model_manufacturer"],chassis_NO=R["car_id"],
              plate_NO=kyc["car"]["plate_NO"],color=kyc["car"]["color"],body_type=kyc["car"]["body_type"])
    print(car)
    driver = Driver(first_name=kyc["owner"]["first_name"],last_name=kyc["owner"]["last_name"],sex=kyc["owner"]["sex"],
                   nationality=kyc["owner"]["nationality"],birthday=dt.fromisoformat(kyc["owner"]["birthday"]),
                    email=kyc["owner"]["email"],government_id=R["owner_id"],
                    national_address=kyc["owner"]["national_address"],phone_NO=str(kyc["owner"]["phone_NO"]))
    print(driver)
    Ad(car);Ad(driver)
    new_application = Application(user=user,car=car,driver=driver)
    print(new_application)
    Ad(new_application);Cm()

    return f"{new_application}"




if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run(debug=True)
