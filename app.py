import re, json,os,smtplib,requests
from datetime import datetime as dt
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html_template import html_template_2
from Hinducalendar import HinduCalendar
from jinja2 import Template
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_EXTERNAL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_EXTERNAL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

app.config['SECRET_KEY'] = 'your-very-secret-key'

class EmailSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Add Name Column
    email = db.Column(db.String(100), unique=True, nullable=False)
    calendar_type = db.Column(db.String(100), nullable=False)
    email_notification = db.Column(db.String(3), nullable=False, default='yes')

def send_email(TO_EMAIL,html_body):
    EMAIL_ADDRESS = os.getenv("GMAIL_APP_USERNAME")
    APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    current_date = datetime.now().strftime("%B %d, %Y")
    msg = MIMEMultipart()
    
    msg["Subject"] = f"Calendar - notification ({current_date})"  # Add the current date to the subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

def generate(event):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-flash"
    
    json_format = {
        "quote": {
            "tamil": "Error in event",
            "english": "Error in event"
        },
        "morning_wish": "Error in event"
    }
    response = client.models.generate_content(
            model=model,
            contents=f"Provide a beautiful one quote in Tamil and english for '{event}' in one line with morning wish in json format if any error in event just generate only morning wish json format will be '{json_format}'"
        )
    try:
        cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
        return cleaned_response
    except json.JSONDecodeError:
        print("Response is not valid JSON.")
        print("Raw response:")
        print(response.text)

with app.app_context():
    db.create_all()
    
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"message": "Flask app with PostgreSQL is running!"})

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/cron', methods=['GET'])
def cron():
    return jsonify({"message": "Flask app with PostgreSQL is running!"})

@app.route('/calendar', methods=['POST'])
def get_panchang():
    user_date = request.form.get('userInput')
    try:
        formatted_date = datetime.strptime(user_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return "<h3>Invalid date format. Please use YYYY-MM-DD.</h3>"

    calendar_type = request.form.get('calendarType')
    cal = HinduCalendar(method=calendar_type, city='auto', regional_language=False)
    a,b=cal.get_date(date=formatted_date, regional=False)
    try:
        b = json.loads(b)
        data = {
            "English Date": b.get("ce_datestring", "N/A"),
            "Regional Date": b.get("regional_date", "N/A"),
            "Event": b.get("event", "N/A"),
            "Regional Date String": b.get("regional_datestring", "N/A"),
            "Panchang": b.get("panchang", "N/A"),
            "calendar_type": calendar_type
        }
        
        return render_template('calendar.html', data=data,Regional=calendar_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-new', methods=['GET', 'POST'])
def addnew():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        calendar_type = request.form.get('calendarType')
        email_notification = request.form.get('email_notification')
        existing_subscription = EmailSubscription.query.filter_by(email=email).first()
        if existing_subscription:
            existing_subscription.name = name
            existing_subscription.calendar_type = calendar_type
            existing_subscription.email_notification = email_notification
        else:
            new_subscription = EmailSubscription(
                name=name,
                email=email,
                calendar_type=calendar_type,
                email_notification=email_notification
            )
            db.session.add(new_subscription)
        db.session.commit()
        flash("Subscription updated successfully!" if existing_subscription else "Subscription successful!", "success")
        return redirect(url_for('index'))
    return render_template("notify_input.html")

@app.route('/trigger', methods=['GET'])
def trigger():
    users = EmailSubscription.query.filter_by(email_notification="yes").all()
    print("list of users",users)
    for user in users:
        calendar_type = user.calendar_type
        try:
            cal = HinduCalendar(method=calendar_type, city='auto', regional_language=False)
            today_date = datetime.today().strftime('%d/%m/%Y')
            a, b = cal.get_date(date=today_date, regional=False)
            b = json.loads(b)
            data = {
                "English Date": b.get("ce_datestring", "N/A"),
                "Regional Date": b.get("regional_date", "N/A"),
                "Event": b.get("event", "N/A"),
                "Regional Date String": b.get("regional_datestring", "N/A"),
                "Panchang": b.get("panchang", "N/A"),
                "calendar_type": calendar_type
            }
            if data.get('Event') not in [None, "N/A", ""]:
                event=data['Event']
                gen_ai = generate(event)
                json_data = json.loads(gen_ai)
                template = Template(html_template_2)
                html_body = template.render(data=json_data, calendar_data=data, event=event)
                send_email(user.email, html_body)
            else:
                print("No event found for",today_date)
        except Exception as e:
            print(f"❌ Error sending email to {user.email}: {e}")
    return 'done',200

@app.route("/success")
def success():
    flash('Thank you for subscribing! 🎉', 'success')
    return redirect(url_for('index'))

@app.route("/about")
def about():
    flash('A Python Flask Website 🎉! Made With Love ❤️', 'success')
    return redirect(url_for('index'))

@app.route('/manage', methods=['GET', 'POST'])
def manage_subscription():
    if request.method == 'POST':
        email = request.form['email']
        subscription = EmailSubscription.query.filter_by(email=email).first()
        if subscription:
            return redirect(url_for('edit_subscription', subscription_id=subscription.id))
        else:
            return 'Email not found. Please try again.'
    return render_template('manage.html')

@app.route('/edit/<int:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
    subscription = EmailSubscription.query.get_or_404(subscription_id)
    if request.method == 'POST':
        subscription.calendar_type = request.form['calendarType']
        subscription.email_notification = request.form['email_notification']
        db.session.commit()
        flash('Subscription updated successfully!', 'success')
        return redirect(url_for('index')) 
    return render_template('edit_subscription.html', subscription=subscription)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)