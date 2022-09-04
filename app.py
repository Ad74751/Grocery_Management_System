import os
from flask import Flask,  render_template, request, make_response, jsonify
from werkzeug.utils import redirect, secure_filename
from database import DB
import uuid
from crypto import Crypto
from serializer import Serializer

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


crypto = Crypto()

app = Flask(__name__)

# Initializing Database
dbInstance = DB(app)
db = dbInstance.GetDB()

# defining database schema


class User(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(80), nullable=False)
    pincode = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False, default=False)
    cart = db.Column(db.String(500))
    uid = db.Column(db.String(80), unique=True,
                    nullable=False, default=str(uuid.uuid4()))

    def __init__(self, name, email, password, phone, state, pincode, address, isAdmin):
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.state = state
        self.pincode = pincode
        self.address = address
        self.isAdmin = isAdmin


class Product(db.Model, Serializer):
    key = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    img = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.String(80),
                    nullable=False, default=str(uuid.uuid1()))

    def __init__(self, name, category, img, price, uid):
        self.name = name
        self.category = category
        self.img = img
        self.price = price
        self.uid = uid

    def serialize(self):
        d = Serializer.serialize(self)
        return d


# Creating database if it does not exist
dbInstance.CreateDB()

# Authentication Functions


def isAdmin(cookie):
    if cookie:
        try:
            ssid = crypto.decrypt(crypto.b64dec(cookie))
            print(ssid)
            email = ssid.split('%')[0]
            password = ssid.split('%')[1]
            print(email)
            print(password)
            user = User.query.filter(User.email == email).filter(
                User.password == password).first()
            if user and user.isAdmin == 1:
                return True
            else:
                return False
        except:
            return False
    else:
        return False


def isAuthenticated(cookie):
    if cookie:
        try:
            print(crypto.b64dec(cookie))
            ssid = crypto.decrypt(crypto.b64dec(cookie))
            print(ssid)
            email = ssid.split('%')[0]
            password = ssid.split('%')[1]
            print(email)
            print(password)
            user = User.query.filter(User.email == email).filter(
                User.password == password).first()
            if user:
                return True
            else:
                return False
        except:
            return False

    else:
        return False

#### General Functions ####


def getUserID(cookie):
    return crypto.decrypt(crypto.b64dec(cookie)).split('%')[2]


def manual_replace(s, char, index):
    return s[:index] + char + s[index + 1:]
#### End General Functions ####


###### Defining App Routes #####

@app.route('/')
def index():
    if isAuthenticated(request.cookies.get('ssid')):
        return render_template("index.html", user=getUserID(request.cookies.get('ssid')))
    else:
        return render_template("index.html", user=None)

@app.route('/checkout/<uid>')
def buy(uid):
    if isAuthenticated(request.cookies.get('ssid')) and getUserID(request.cookies.get('ssid')) == uid:
        user = User.query.filter(User.uid == uid).first()
        if user:
            return render_template("buy.html", user=user)
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/shop')
def shop():
    if isAuthenticated(request.cookies.get('ssid')):
        return render_template("shop.html", user=getUserID(request.cookies.get('ssid')))
    else:
        return render_template("shop.html", user=None)


@app.route('/profile/<uid>')
def profile(uid):
    if isAuthenticated(request.cookies.get('ssid')) and getUserID(request.cookies.get('ssid')) == uid:
        user = User.query.filter(User.uid == uid).first()
        if user:
            return render_template("profile.html", user=user)
        else:
            return "<h2>User Profile Not Found</h2>"
    else:
        return redirect('/login')


@app.route('/test')
def test():
    return render_template("test.html")


@app.route('/logout')
def logout():
    if request.cookies.get("ssid"):
        resp = make_response(redirect('/login'))
        resp.delete_cookie('ssid')
        return resp


@app.route('/products/<uid>')
def products(uid):
    if uid and uid == "all":
        products = Product.query.all()
        return jsonify(Product.serialize_list(products))
    elif uid:
        product = Product.query.filter(Product.uid == uid).first()
        if product:
            return render_template("detail.html", prod=product, user=getUserID(request.cookies.get('ssid')) if request.cookies.get('ssid') else None)
        else:
            return "<h1>Product Not Found</h1>"
    else:
        return redirect('/login')


# @app.route('/add-admin')
# def admin():
#     admin = User("Admin", "admin@mail.com", "admin@1234$",
#                  "None", "None", "None", "None", True)
#     db.session.add(admin)
#     db.session.commit()
#     return "Admin Added"

# ### Admin Routes #####


@app.route('/addproduct', methods=['POST'])
def addProduct():
    if request.method == "POST" and isAdmin(request.cookies.get('ssid')):
        formData = request.form
        file = request.files['image']
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                product = Product(formData.get('name'), formData.get(
                    'category'), manual_replace(f'{UPLOAD_FOLDER}/{filename}', ".", 0), int(formData.get('price')), str(uuid.uuid4()))
                db.session.add(product)
                db.session.commit()
                return redirect('/dashboard')
            except Exception as e:
                print(e)
                return redirect('/login')
    else:
        return redirect('/login')


@app.route('/delete-product/<uid>', methods=['GET'])
def deleteProduct(uid):
    if request.method == "GET" and isAdmin(request.cookies.get('ssid')):
        if uid:
            product = Product.query.filter(Product.uid == uid).first()
            if product:
                db.session.delete(product)
                db.session.commit()
                return redirect('/dashboard')
            else:
                return redirect('/dashboard')
        else:
            return redirect('/dashboard')
    else:
        return redirect('/login')


@app.route('/dashboard')
def dashboard():
    print(isAdmin(request.cookies.get('ssid')))
    if isAdmin(request.cookies.get('ssid')):
        prods = Product.query.all()
        return render_template("dashboard.html", user=getUserID(request.cookies.get('ssid')), products=prods)
    else:
        return redirect('/login')
#### End Admin Routes #####


##### User Routes #####
@app.route('/delete-account/<uid>')
def delete_account(uid):
    if isAuthenticated(request.cookies.get('ssid')) and uid and getUserID(request.cookies.get('ssid')) == uid:
        user = User.query.filter(User.uid == uid).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return redirect('/register')
        else:
            return "The specified user does not exist !!!"
    else:
        return redirect('/login')


@app.route('/edit-profile', methods=['POST'])
def edit_profile():
    if request.method == "POST" and isAuthenticated(request.cookies.get('ssid')):
        formData = request.form
        uid = formData.get('uid')
        name = formData.get('name')
        email = formData.get('email')
        phone = formData.get('phone')
        address = formData.get('address')
        if getUserID(request.cookies.get('ssid')) == uid:
            user = User.query.filter(User.uid == uid).first()
            if user:
                user.name = name
                user.email = email
                user.phone = phone
                user.address = address
                db.session.commit()
                return redirect(f'/profile/{uid}')
            else:
                return "User not found !!!"
        else:
            return redirect('/login')


# @app.route('/cart/<operation>', methods=['GET', 'POST'])
# def cart(operation):
#     if operation == "add" and request.method == "POST" and isAuthenticated(request.cookies.get('ssid')):
#         formData = request.json
#         if formData:
#             user = User.query.filter(User.uid == getUserID(
#                 request.cookies.get('ssid'))).first()
#             if user:
#                 cartItem = {
#                     "id": formData["id"],
#                     "qty": formData["qty"],
#                 }

#                 if user.cart:
#                     cart = json.loads(user.cart)
#                     cartData = json.dumps(car)
#                 else:
#                     user.cart = json.dumps([])

##### End User Routes #####

##### Authentication Routes ######


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if isAuthenticated(request.cookies.get("ssid")):
            return redirect('/shop')
        else:
            return render_template("login.html")
    elif request.method == "POST":
        formData = request.form
        try:
            user = User.query.filter(User.email == formData.get('email')).filter(
                User.password == formData.get('password')).first()
            if user:
                cookie_content = crypto.b64enc(crypto.encrypt(
                    f'{formData.get("email")}%{formData.get("password")}%{user.uid}'))
                resp = make_response(
                    redirect('/dashboard' if user.isAdmin == 1 else '/shop'))
                resp.set_cookie("ssid", cookie_content)
                return resp
            else:
                return redirect('/login')
        except:
            return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        formData = request.form
        user = User(formData.get('fname'), formData.get('email'), formData.get('password'), formData.get(
            'phone'), formData.get('state'), formData.get('pincode'), formData.get('address'), False)
        try:
            db.session.add(user)
            db.session.commit()
            cookie_content = crypto.b64enc(crypto.encrypt(
                f'{formData.get("email")}%{formData.get("password")}%{user.uid}'))
            resp = make_response(render_template("index.html"))
            resp.set_cookie("ssid", cookie_content)
            return resp
        except Exception as e:
            print(e)
            return "Error"
##### End Authentication Routes ######


if __name__ == "__main__":
    app.run(debug=True)
