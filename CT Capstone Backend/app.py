from flask import Flask, make_response, request, g
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


class Config():
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS= os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email, password):
    u = User.query.filter_by(email=email).first()
    if not u:
        return False
    g.current_user = u
    return u.check_hashed_password(password)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String, index=True, unique=True)
    password = db.Column(db.String)
    reverb = db.Column(db.Integer)
    dist = db.Column(db.Integer)
    vibe = db.Column(db.Integer)
    octave = db.Column(db.Integer)
    

    def __repr__(self):
        return f'<{self.user_id}|{self.email}>'

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self,data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = self.hash_password(data['password'])

    def from_keydict(self,data):
        self.reverb = data['reverb']
        self.dist = data['dist']
        self.vibe = data['vibe']
        self.octave = data['octave']

    def to_dict(self):
        return {'user_id': self.id, 'email':self.email, 'user':self.first_name}



class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)


@app.get('/login')
@basic_auth.login_required()
def login():
    return make_response(f'{g.current_user.first_name}', 200)

@app.get('/user')
def get_users():
    return make_response({'users':[user.to_dict() for user in User.query.all()]}, 200)

@app.get('/user/<int:id>')
def get_user(id):
    return make_response(User.query.get(id).to_dict(), 200)

@app.post('/user')
def create_user():
    data = request.get_json()
    new_user = User()
    new_user.from_dict(data)
    new_user.save()
    return make_response("success",200)

@app.put('/user/<int:id>')
def put_keys(id):
    data = request.get_json()
    User.query.get(id).from_keydict(data)
    return make_response("success",200)

@app.delete('/user/<int:id>')
def delete_user(id):
    User.query.get(id).delete()
    return make_response("success",200)