import json, os, smtplib
import urllib.request
import urllib.error
import subprocess, re, time, sys
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from html_template import html_template_2
from Hinducalendar import HinduCalendar
from jinja2 import Template
from dotenv import load_dotenv
import pytz
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()
IST = pytz.timezone("Asia/Kolkata")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Flask-Calendar-App'

database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    print("⚠️ DATABASE_URL is not set. Subscription features will be disabled.")

db = SQLAlchemy(app)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    calendar_type = db.Column(db.String(50))
    email_notification = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

if database_url:
    with app.app_context():
        try:
            db.create_all()
            print("✅ PostgreSQL Database configured and tables created.")
        except Exception as e:
            print(f"❌ Error configuring PostgreSQL: {e}")

def get_ist_now():
    return datetime.now(pytz.utc).astimezone(IST)

def send_email(TO_EMAIL,html_body, attachment_tuple=None):
    EMAIL_ADDRESS = os.getenv("GMAIL_APP_USERNAME")
    APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    #current_date = datetime.now().strftime("%B %d, %Y")
    current_date = get_ist_now().strftime("%B %d, %Y")
    msg = MIMEMultipart()
    msg["Subject"] = f"Calendar - notification ({current_date})"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))
    
    if attachment_tuple:
        img_data, img_name = attachment_tuple
        image = MIMEImage(img_data, name=img_name)
        msg.attach(image)
        
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/classic', methods=['GET'])
def classic():
    return render_template('classic.html')

@app.route('/api/classic_calendar', methods=['GET'])
def proxy_classic_calendar():
    cal_type = request.args.get('type') # 'daily' or 'monthly'
    year = request.args.get('year')
    month = request.args.get('month') # 01-12
    day = request.args.get('day') # 1-31 (unpadded)

    if not year or not month:
        return jsonify({"error": "Missing year or month"}), 400

    month_names = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }

    if cal_type == 'daily':
        if not day:
            return jsonify({"error": "Missing day"}), 400
        # Daily format: 2026/19012026.jpg (day is not padded, month is padded)
        url = f"https://www.tamildailycalendar.com/{year}/{int(day)}{month}{year}.jpg"
    elif cal_type == 'monthly':
        # Monthly format: 2026_Monthly/04_Tamil_Monthly_Calendar_April_2026.jpg
        m_name = month_names.get(month)
        if not m_name:
            return jsonify({"error": "Invalid month"}), 400
        url = f"https://www.tamildailycalendar.com/{year}_Monthly/{month}_Tamil_Monthly_Calendar_{m_name}_{year}.jpg"
    else:
        return jsonify({"error": "Invalid type"}), 400

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.tamildailycalendar.com/'})
        response = urllib.request.urlopen(req)
        return Response(response.read(), content_type=response.headers.get('Content-Type', 'image/jpeg'))
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"Image not found on the server (HTTP {e.code}). It might not be available for the selected date."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/calendar', methods=['POST'])
def get_panchang():
    user_date = request.form.get('userInput')
    try:
        formatted_date = datetime.strptime(user_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
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
        if request.headers.get('Accept') == 'application/json':
            return jsonify(data)
        return render_template('calendar.html', data=data,Regional=calendar_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-new', methods=['GET', 'POST'])
def addnew():
    if not os.getenv("DATABASE_URL"):
        flash("Email subscriptions are currently disabled (Database not configured).", "warning")
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        calendar_type = request.form.get('calendarType')
        email_notification = request.form.get('email_notification')

        existing = Subscription.query.filter_by(email=email).first()
        if existing:
            existing.name = name
            existing.calendar_type = calendar_type
            existing.email_notification = email_notification
            db.session.commit()
            flash("Subscription updated successfully!", "success")
        else:
            new_sub = Subscription(
                name=name,
                email=email,
                calendar_type=calendar_type,
                email_notification=email_notification
            )
            db.session.add(new_sub)
            db.session.commit()
            flash("Subscription successful!", "success")

        return redirect(url_for('index'))
    
    return render_template("notify_input.html")

def background_task(users):
    for user in users:
        calendar_type = user.calendar_type
        try:
            cal = HinduCalendar(method=calendar_type, city='auto', regional_language=False)
            now = get_ist_now()
            today_date = now.strftime('%d/%m/%Y')
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
                template = Template(html_template_2)
                html_body = template.render(calendar_data=data, event=event)
                
                attachment = None
                if calendar_type == "Tamil":
                    try:
                        year = now.strftime('%Y')
                        month = now.strftime('%m')
                        day = str(now.day)
                        url = f"https://www.tamildailycalendar.com/{year}/{day}{month}{year}.jpg"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.tamildailycalendar.com/'})
                        response = urllib.request.urlopen(req)
                        attachment = (response.read(), f"Tamil_Calendar_{day}_{month}_{year}.jpg")
                    except Exception as e:
                        print(f"Failed to fetch classic calendar for email attachment: {e}")
                        
                send_email(user.email, html_body, attachment)
            else:
                print("No event found for", today_date)
        except Exception as e:
            print(f"❌ Error sending email to {user.email}: {e}")

            
@app.route('/trigger', methods=['GET'])
def trigger():
    if not os.getenv("DATABASE_URL"):
        return 'Subscriptions are currently disabled (Database not configured).', 503
    try:
        users = Subscription.query.filter_by(email_notification="yes").all()
        if not users:
            return 'No users with notifications enabled.', 200
        thread = threading.Thread(target=background_task, args=(users,))
        thread.start()
        return 'Processing started', 200
    except Exception as e:
        return f"Error occurred: {str(e)}", 500


@app.route("/about")
def about():
    flash('A Python Flask Website 🎉! Made With Love ❤️', 'success')
    return redirect(url_for('index'))

@app.route('/manage', methods=['GET', 'POST'])
def manage_subscription():
    if not os.getenv("DATABASE_URL"):
        flash("Subscription management is currently disabled (Database not configured).", "warning")
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        sub = Subscription.query.filter_by(email=email).first()
        if sub:
            return redirect(url_for('edit_subscription', subscription_id=str(sub.id)))
        else:
            return 'Email not found. Please try again.'
    return render_template('manage.html')


@app.route('/edit/<string:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
    if not os.getenv("DATABASE_URL"):
        flash("Subscription editing is currently disabled (Database not configured).", "warning")
        return redirect(url_for('index'))
    
    try:
        sub = Subscription.query.get(int(subscription_id))
    except ValueError:
        return "Invalid subscription ID", 400
        
    if not sub:
        return "Subscription not found", 404

    if request.method == 'POST':
        sub.calendar_type = request.form['calendarType']
        sub.email_notification = request.form['email_notification']
        db.session.commit()
        flash('Subscription updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_subscription.html', subscription=sub)

# global variables for cloudflared
cloudflared_process = None
last_cloudflared_restart = 0.0

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

def stop_cloudflared():
    global cloudflared_process
    if cloudflared_process:
        try:
            cloudflared_process.terminate()
            cloudflared_process.wait(timeout=5)
        except Exception:
            pass
    try:
        subprocess.run(['pkill', 'cloudflared'], stderr=subprocess.DEVNULL)
    except:
        pass

def start_cloudflared():
    global cloudflared_process
    stop_cloudflared()
    try:
        cloudflared_process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://localhost:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Starting cloudflared tunnel...")
        if cloudflared_process and cloudflared_process.stderr:
            for line in cloudflared_process.stderr:
                print(line, end='')
                match = re.search(r'(https://[-a-z0-9]+\.trycloudflare\.com)', line)
                if match:
                    url = match.group(1)
                    print(f"[*] Found Cloudflare URL: {url}")
                    try:
                        redirector_url = 'https://tamilcalendar.pythonanywhere.com/update'
                        data = urllib.parse.urlencode({'url': url}).encode('utf-8')
                        req = urllib.request.Request(redirector_url, data=data)
                        with urllib.request.urlopen(req) as response:
                            print(f"[*] Updated proxy successfully: {response.status}")
                    except Exception as e:
                        print(f"[!] Failed to update proxy: {e}")
    except Exception as e:
        print(f"Cloudflared error: {e}")

def monitor_cloudflared():
    global last_cloudflared_restart
    # Wait initially to allow tunnel execution buffer
    time.sleep(15) 
    first_run = True
    while True:
        try:
            health_ok = False
            redirector_url_current = 'https://tamilcalendar.pythonanywhere.com/current'
            req = urllib.request.Request(redirector_url_current)
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    current_url = response.read().decode('utf-8').strip()
                    # if it's JSON, parse it
                    if current_url.startswith('{'):
                        current_url = json.loads(current_url).get('url', '')
                
                if current_url:
                    health_url = current_url.rstrip('/') + '/health'
                    req_health = urllib.request.Request(health_url)
                    with urllib.request.urlopen(req_health, timeout=10) as health_response:
                        if health_response.status == 200:
                            health_ok = True
                            print("[*] Cloudflare tunnel is healthy.")
            except urllib.error.HTTPError as he:
                print(f"[!] Health check HTTP error ({he.code}): {he.reason}")
            except Exception as health_e:
                print(f"[!] Health check failed: {health_e}")
            
            if not health_ok:
                current_time = time.time()
                
                if first_run or (current_time - last_cloudflared_restart > 3600):
                    print("[!] Restarting cloudflared due to health check failure.")
                    last_cloudflared_restart = current_time
                    threading.Thread(target=start_cloudflared, daemon=True).start()
                else:
                    print("[*] Health check failed, but waiting for 1hr cooldown to restart cloudflared.")
            
        except Exception as e:
            print(f"Cloudflare monitor error: {e}")
        
        first_run = False
        time.sleep(600) # Check every 10 mins

def scheduled_job():
    print("⏰ Running scheduled email trigger job...")
    if not os.getenv("DATABASE_URL"):
        print("Database not configured. Cannot run scheduled job.")
        return
    with app.app_context():
        try:
            users = Subscription.query.filter_by(email_notification="yes").all()
            if not users:
                print('No users with notifications enabled.')
                return
            background_task(users)
        except Exception as e:
            print(f"Error in scheduled job: {e}")

# Start the scheduler
scheduler = BackgroundScheduler(timezone=IST)
scheduler.add_job(scheduled_job, CronTrigger(hour=5, minute=30, timezone=IST))
scheduler.start()

if __name__ == "__main__":
    if '--cloudflared' in sys.argv or '--cloudfared' in sys.argv:
        t = threading.Thread(target=start_cloudflared, daemon=True)
        t.start()
        
        cf_monitor_t = threading.Thread(target=monitor_cloudflared, daemon=True)
        cf_monitor_t.start()
        
    app.run(host="0.0.0.0", port=5000,debug=True)