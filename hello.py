from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Create a Flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "password"

# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create a route decarator
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