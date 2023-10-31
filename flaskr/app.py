from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
# Gibberish that sqlalchemy needs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY'] = 'aed59bcbfb7a03c29b6364d4cce086dc'




# Initialize the database 
db = SQLAlchemy(app)
db.init_app(app)



# This is our hardcoded password
HARDCODED_USERNAME = "your_username"
HARDCODED_PASSWORD = "your_password"

 

class LoginForm(FlaskForm):
  username = StringField('Username')
  password = PasswordField('Password')
  submit = SubmitField('Login')


# create database model for events
class Event(db.Model):
   
   # id is used to identify the article. It is assigned by the program
   id = db.Column(db.Integer, primary_key=True)
   
   # This is for the title of the article
   name = db.Column(db.String(255))
   
   date = db.Column(db.String(255))
   

   def __init__(self, name, date):
      self.name = name
      self.date = date
        
# Create database model for presentations
class Presentation(db.Model):
   
   id = db.Column(db.Integer, primary_key = True)
   
   name = db.Column(db.String(255))
   
   url = db.Column(db.String(255))
   
   date_added = db.Column(db.DateTime, default=datetime.utcnow)
   
   def __init__(self, name, url):
      self.name = name
      self.url = url
        
db.create_all()  # Create the database tables



 # This displays our login manager and lets the user know if they made it in
@app.route('/login', methods=['GET', 'POST'])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      if form.username.data == HARDCODED_USERNAME and form.password.data == HARDCODED_PASSWORD:
         session['logged_in'] = True
         flash('Login successful!')
         return redirect('/dashboard')
      else:
         flash('Invalid credentials.')
   return render_template('login.html', form=form)

# If we are home return the render template for the home page
@app.route("/")
def home():
   return render_template('index.html')

# If we want to see the events and presentations, we return here
@app.route("/resources")
def links():
   # Get the current date
   current_date = datetime.now().date()

   # Query events happening on the current day or in the future
   future_events = Event.query.filter(Event.date >= current_date).all()

   # Sort events by date in ascending order
   future_events_sorted = sorted(future_events, key=lambda event: event.date)

   
   # Query the latest presentations, ordered by date_added in descending order
   latest_presentations = Presentation.query.order_by(desc(Presentation.date_added)).all()
   
   return render_template('resources.html', events=future_events_sorted,
                          presentations=latest_presentations)


# Function to display the events and presentations
@app.route('/dashboard')
def dashboard():
   if 'logged_in' not in session:
      return redirect(url_for('login'))
   
   events = Event.query.all()
    
   # Query all events in the future
   future_events = Event.query.filter(Event.date >= datetime.now()).all()

   # Sort events by date in ascending order
   future_events_sorted = sorted(future_events, key=lambda event: event.date)

   
   # Query the latest presentations, ordered by date_added in descending order
   latest_presentations = Presentation.query.order_by(desc(Presentation.date_added)).all()
   
   return render_template('dashboard.html', events = events, presentations = latest_presentations)
   

# Function to create an event
@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
   
   if 'logged_in' not in session:
      return redirect(url_for('login'))
   
   if request.method == 'POST':
      event_name = request.form.get('event_name')
      event_date = request.form.get('event_date')
      # Add your code to create the event in the database here
      new_event = Event(name=event_name, date=event_date)

      # Add the new event to the database session
      db.session.add(new_event)
      db.session.commit()  # Commit the changes to the database

      # After creating the event, you can redirect the user back to the dashboard
      return redirect('/dashboard')
   
   # If it's a GET request (initial load of the page), just render the form
   return render_template('create_event.html')


# Function to delete an event
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
   
   if 'logged_in' not in session:
      return redirect(url_for('login'))
   
   event = Event.query.get(event_id)
   if event:
      db.session.delete(event)
      db.session.commit()
   return redirect('/dashboard')

# FUnction to create a presentation
@app.route('/create_presentation', methods=['GET', 'POST'])
def create_presentation():
   
   if 'logged_in' not in session:
      return redirect(url_for('login'))
   
   if request.method == 'POST':
      presentation_name = request.form.get('presentation_name')
      presentation_url = request.form.get('presentation_url')

      # Create a new Presentation object
      new_presentation = Presentation(name=presentation_name, url=presentation_url)

      # Add the new presentation to the database session
      db.session.add(new_presentation)
      db.session.commit()  # Commit the changes to the database

      # After creating the presentation, you can redirect the user back to the dashboard
      return redirect('/dashboard')

   # If it's a GET request (initial load of the page), just render the form
   return render_template('create_presentation.html')


@app.route('/delete_presentation/<int:presentation_id>', methods=['POST'])
def delete_presentation(presentation_id):
   
   if 'logged_in' not in session:
      return redirect(url_for('login'))
   
   presentation = Presentation.query.get(presentation_id)
   if presentation:
      db.session.delete(presentation)
      db.session.commit()
   return redirect('/dashboard')
   
   
# Logout route
@app.route('/logout')
def logout():
   # Remove the 'logged_in' session variable to log the user out
   session.pop('logged_in', None)
   flash('Logged out successfully!')
   return redirect(url_for('login'))  # Redirect the user to the login page

if __name__ == '__main__':
   app.run()