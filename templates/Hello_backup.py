from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea

# Create a Flask instance
app = Flask(__name__)
#add database
# Old SQLite database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#new mySQL database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'
#secret key 
app.config['SECRET_KEY'] = "password"
#initialise the database
db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)

# Flask Login Stuff
LoginManager = LoginManager()
LoginManager.init_app(app)
LoginManager.login_view = 'login'

@LoginManager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# Create login nform
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

#Creat login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# check the hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Succesfull!!!")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password - Try again!!!")
		else:
			flash("That user Doesn't exist - Try again...")


	return render_template('login.html', form=form)

#Create Logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Been Logged Out")
	return redirect(url_for('login'))

#Creat Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.colour = request.form['colour']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update)
		except:
			flash("Error looks like there was a problem!")
			return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update)

	else:
		return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update, 
				id = id)
	return render_template('dashboard.html')


# Create a blog post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))

# Create a posts form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")

@app.route('/posts/delete<int:id>')
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)

	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		#Return a message
		flash("Blog Post was deleted!")
		# Grab all the posts from the database and open posts page
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)

	except:
		#Return an error message
		flash("There was a problem deleting the Post! Please try again...")
		# Grab all the posts from the database and open posts page
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)


@app.route('/posts')
@login_required
def posts():
	#Grab all the posts from the database
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post=post)

#edit the post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
#@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update db
		db.session.add(post)
		db.session.commit()
		flash("Post has been Updated!")
		return redirect(url_for('post', id=post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content
	return render_template('edit_post.html', form=form)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
#@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
		#Clear the form
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''
		# Add post data to database
		db.session.add(post)
		db.session.commit()
		#return a message
		flash("Blog post submitted successfully!")
	#Redirect to the webpage
	return render_template("add_post.html", form=form)

# Json Thing
@app.route('/date')
def get_current_date():
	favourite_pizza = {
		"James": "Meat Feast",
		"Stewart": "New Yorker",
		"Colette": "Hawaiian"
	}
	#return favourite_pizza
	return {"Date": date.today()}

#create model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	colour = db.Column(db.String(40))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	#Password bits
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttibuteError('password is not a readable attribute!')
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)	

	# create a String

	def __repr__(self):
		return '<Name %r>' % self.name

# Create a Form Class
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	colour = StringField("Colour")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match')])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField("Submit")


#Delete Database Recored
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()
	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User Deleted Successfully!")
		our_users = Users.query.order_by(Users.date_added)
		return render_template('add_user.html', form=form, name=name, our_users=our_users)
	except:
		flash("Error looks like there was a problem!")
		#our_users = Users.query.order_by(Users.date_added)
		return render_template('add_user.html', form=form, name=name, our_users=our_users)


#Update Database Recored
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.colour = request.form['colour']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("update.html", 
				form=form,
				name_to_update = name_to_update)
		except:
			flash("Error looks like there was a problem!")
			return render_template("update.html", 
				form=form,
				name_to_update = name_to_update)

	else:
		return render_template("update.html", 
				form=form,
				name_to_update = name_to_update, 
				id = id)

# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
	email = StringField("What's Your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

@app.route('/user/add/', methods=['POST', 'GET'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None: 
			#hash the password
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(username=form.username.data, name=form.name.data, email=form.email.data, colour=form.colour.data, password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.username.date = ''
		form.name.data = ''
		form.email.data = ''
		form.colour.data = ''
		form.password_hash = ''

		flash("User Added Successfuly!!")
	our_users = Users.query.order_by(Users.date_added)

	return render_template('add_user.html', form=form, name=name, our_users=our_users)
	#title = "My friend List"
	#if request.method == "POST":
		#friend_name = request.form['name']
		#new_friend = Friends(name=friend_name)

		# Push to db
		#try:
			#db.session.add(new_friend)
			#db.session.commit()
			#return redirect('/friends')
		#except:
			#return "There was an error adding your friend!"

	#else:
		#friends = Friends.query.order_by(Friends.date_created)
		#return render_template('friends.html', title=title, friends=friends)

@app.route('/')
def index():
	first_name = 'James'
	stuff = "This is <strong>Bold</strong> text!!"
	favourite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
	return render_template('index.html', 
		first_name=first_name, 
		stuff=stuff,
		favourite_pizza=favourite_pizza)

# Localhost:5000/user/James
@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)

# Custom Error Page
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

# Internal Server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'), 500



# Create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form. validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form submitted successfully")

	return render_template('name.html',
		name = name,
		form = form)


# Create password test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()


	# Validate Form
	if form. validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		#clear the form
		form.email.data = ''
		form.password_hash.data = ''

		#Look up user by email
		pw_to_check = Users.query.filter_by(email=email).first()
		
		#Check hashed password
		passed = check_password_hash(pw_to_check.password_hash, password)


	return render_template('test_pw.html',
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)