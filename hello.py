from flask import Flask, render_template

# Create a Flask instance
app = Flask(__name__)

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