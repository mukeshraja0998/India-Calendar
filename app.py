import re, json,os,smtplib,requests
from datetime import datetime as dt
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template, Response, flash, redirect, url_for
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
import pytz
import threading
#from flask_pymongo import PyMongo
from bson.objectid import ObjectId


load_dotenv()
IST = pytz.timezone("Asia/Kolkata")

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI")
print(f"Loaded MONGO_URI: {mongo_uri}")
#app.config["MONGO_URI"] = mongo_uri
#mongo = PyMongo()
#mongo.init_app(app)

app.config['SECRET_KEY'] = 'Flask-Calendar-App'

#mongo = PyMongo(app)
#db = mongo.cx.get_database("mydatabase")

def get_ist_now():
    return datetime.now(pytz.utc).astimezone(IST)

def send_email(TO_EMAIL,html_body):
    EMAIL_ADDRESS = os.getenv("GMAIL_APP_USERNAME")
    APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    #current_date = datetime.now().strftime("%B %d, %Y")
    current_date = get_ist_now().strftime("%B %d, %Y")
    msg = MIMEMultipart()
    msg["Subject"] = f"Calendar - notification ({current_date})"
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

def generate(event,calendar_type="Tamil"):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-flash"
    #print("calendar_type",calendar_type)
    json_format = {
        f"quote": {
            calendar_type: "Error in event",
            "english": "Error in event"
        },
        "morning_wish": "Error in event"
    }
    response = client.models.generate_content(
            model=model,
            contents=f"Provide a beautiful one quote in {calendar_type} and english for '{event}' in one line with morning wish in json format if any error in event just generate only morning wish json format will be '{json_format}'"
        )
    try:
        cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
        return cleaned_response
    except json.JSONDecodeError:
        print("Response is not valid JSON.")
        print("Raw response:")
        print(response.text)

    
@app.route('/health', methods=['GET'])
def health():
    print("MONGO_URI:", os.getenv("MONGO_URI"))
    return jsonify({"message": "Flask app with PostgreSQL is running!"})

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/calendar', methods=['POST'])
def get_panchang():
    user_date = request.form.get('userInput')
    try:
        formatted_date = datetime.strptime(user_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return "<h3>Invalid date format. Please use YYYY-MM-DD.</h3>"
    calendar_type = request.form.get('calendarType')
    cal = HinduCalendar(method=calendar_type, city='Chennai', regional_language=False)
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

        existing = mongo.db.subscriptions.find_one({'email': email})
        if existing:
            mongo.db.subscriptions.update_one(
                {'email': email},
                {'$set': {
                    'name': name,
                    'calendar_type': calendar_type,
                    'email_notification': email_notification
                }}
            )
            flash("Subscription updated successfully!", "success")
        else:
            mongo.db.subscriptions.insert_one({
                'name': name,
                'email': email,
                'calendar_type': calendar_type,
                'email_notification': email_notification,
                'created_at': datetime.utcnow()
            })
            flash("Subscription successful!", "success")

        return redirect(url_for('index'))
    
    return render_template("notify_input.html")

def background_task(users):
    for user in users:
        calendar_type = user['calendar_type']
        try:
            cal = HinduCalendar(method=calendar_type, city='auto', regional_language=False)
            today_date = get_ist_now().strftime('%d/%m/%Y')
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
                event = data['Event']
                gen_ai = generate(event, calendar_type)
                json_data = json.loads(gen_ai)
                template = Template(html_template_2)
                html_body = template.render(data=json_data, calendar_data=data, event=event)
                send_email(user['email'], html_body)
            else:
                print("No event found for", today_date)
        except Exception as e:
            print(f"❌ Error sending email to {user['email']}: {e}")

            
@app.route('/trigger', methods=['GET'])
def trigger():
    try:
        users = list(mongo.db.subscriptions.find({"email_notification": "yes"}))
        if not users:
            return 'No users with notifications enabled.', 200
        thread = threading.Thread(target=background_task, args=(users,))
        thread.start()
        return 'Processing started', 200
    except Exception as e:
        return f"Error occurred: {str(e)}", 500



@app.route('/check', methods=['GET'])
def check():
    
    cal = HinduCalendar(method="tamil", city='auto', regional_language=False)
    #today_date = datetime.today().strftime('%d/%m/%Y')
    today_date = get_ist_now().strftime('%d/%m/%Y')
    a, b = cal.get_date(date=today_date, regional=False)
    b = json.loads(b)
    data = {
        "English Date": b.get("ce_datestring", "N/A"),
        "Regional Date": b.get("regional_date", "N/A"),
        "Event": b.get("event", "N/A"),
        "Regional Date String": b.get("regional_datestring", "N/A"),
        "Panchang": b.get("panchang", "N/A"),
        "calendar_type": "tamil"
    }
    event = data['Event']
    gen_ai = generate(event, "tamil")
    json_data = json.loads(gen_ai)
    #print(data)
    return render_template('trigger.html', data=json_data, calendar_data=data, event=event)

@app.route("/about")
def about():
    flash('A Python Flask Website 🎉! Made With Love ❤️', 'success')
    return redirect(url_for('index'))

@app.route('/manage', methods=['GET', 'POST'])
def manage_subscription():
    if request.method == 'POST':
        email = request.form['email']
        sub = mongo.db.subscriptions.find_one({'email': email})
        if sub:
            return redirect(url_for('edit_subscription', subscription_id=str(sub['_id'])))
        else:
            return 'Email not found. Please try again.'
    return render_template('manage.html')


@app.route('/edit/<string:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
    sub = mongo.db.subscriptions.find_one({'_id': ObjectId(subscription_id)})
    if not sub:
        return "Subscription not found", 404

    if request.method == 'POST':
        mongo.db.subscriptions.update_one(
            {'_id': ObjectId(subscription_id)},
            {'$set': {
                'calendar_type': request.form['calendarType'],
                'email_notification': request.form['email_notification']
            }}
        )
        flash('Subscription updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_subscription.html', subscription=sub)

@app.route('/check_mongo')
def check_mongo():
    try:
        db.test.insert_one({"msg": "Hello from Flask & MongoDB!"})
        return "MongoDB is connected!"
    except Exception as e:
        return f"MongoDB connection failed: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)