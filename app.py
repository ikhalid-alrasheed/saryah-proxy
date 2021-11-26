from flask import Flask, request, jsonify;from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__);app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saryah.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;db=SQLAlchemy(app);from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required; login_manager = LoginManager(app)
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    apple_id = db.Column(db.Integer)
    full_name = db.Column(db.String(40))
    sex = db.Column(db.String(1))
    nationality = db.Column(db.String(40))
    birthday = db.Column(db.DateTime)
    email = db.Column(db.String)
    government_id = db.Column(db.String(12), unique=True)
    national_address = db.Column(db.String)
    phone_NO = db.Column(db.String(13), unique=True)
    password = db.Column(db.String, default=None)
    def set_password(self, pwd): self.password = generate_password_hash(pwd)
    def check_password(self, pwd): return check_password_hash(self.password, pwd)
    def how_old_in_years(self): return (datetime.utcnow() - self.birthday).days // 365
    def to_dict(self):
        keys = ['id', 'apple_id', 'full_name', 'sex', 'nationality', 'birthday', 'email', 'government_id', 'national_address',
                'phone_NO', "password"];relation_keys =  ["cars", "owned_cars"]
        return {key : getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
class Cars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User",foreign_keys=[user_id], backref="cars", lazy=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner = db.relationship("User", foreign_keys=[owner_id], backref="owned_cars", lazy=True)
    model = db.Column(db.String(40))
    model_year = db.Column(db.String(4))
    model_manufacturer = db.Column(db.String(20))
    chassis_NO = db.Column(db.String(25), unique=True)
    customs_id = db.Column(db.String(25), unique=True)
    plate_NO = db.Column(db.String(25)) # "ABC1234 ابت١٢٣٤"
    color = db.Column(db.String)
    body_type = db.Column(db.String)
    def to_dict(self):
        keys = ['id', 'model', 'model_year', 'model_manufacturer', 'chassis_NO', 'customs_id', 'plate_NO', 'color', 'body_type']
        relation_keys = ["transactions"]
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer) #matches epow id
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    car = db.relationship('Cars', backref='transactions', lazy=True)
    transaction_at = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal_SAR = db.Column(db.Float)
    vat_SAR = db.ColumnProperty(0.15 * subtotal_SAR)
    total_SAR = db.ColumnProperty(subtotal_SAR + vat_SAR)
    def to_dict(self):
        keys = ['id', 'request_id', 'transaction_at', 'subtotal_SAR', 'vat_SAR', 'total_sar']
        relation_keys =  ["policy"]
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
class Policies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), nullable=False)
    transaction = db.relationship('Transactions', backref='policy', lazy=True)
    provider = db.Column(db.String(15))
    issue_at = db.Column(db.DateTime)
    effective_at = db.Column(db.DateTime)
    number = db.Column(db.String(25))
    type = db.Column(db.String(10))
    def to_dict(self):
        keys = ['id', 'provider', 'issue_at', 'effective_at', 'number', 'type']
        relation_keys =  []
        return {key: getattr(self, key, None) if key in keys else [item.to_dict() for item in getattr(self, key, None)]
                for key in keys + relation_keys}
# routs
@app.route('/')
def init():
    return exec(open('database_builder.py').read())
@login_manager.user_loader
def get_user(user_id):
    return User.query.get(user_id)
@app.route('/sign_up', methods=['POST'])
def sign_up():
    """id_type : ['apple_id', 'phone_NO']"""
    signup_type =  request.form["id_type"]
    user = User.query.filter_by(apple_id=request.form[signup_type]).first() if type == "apple_id" \
        else User.query.filter_by(phone_NO=request.form[signup_type]).first()
    if user : return f"user already exist"
    del user;user = User()
    setattr(user, signup_type, request.form[signup_type])
    if signup_type != "apple_id":user.set_password(request.form["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict())
@app.route('/login', methods=['POST'])
def login():
    login_type = request.form["id_type"]
    user = User.query.filter_by(apple_id=request.form[login_type]).first() if login_type == "apple_id" \
        else User.query.filter_by(phone_NO=request.form[login_type]).first()
    if not user : return "this user does not exist"
    if login_type == "apple_id": login_user(user); return "user logged in"
    if user.check_password(request.form["password"]):
        login_user(user);return "user logged in"
    return "password does not match"
app.secret_key = b'192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
if __name__ == "__main__":
    app.run(debug=False)
