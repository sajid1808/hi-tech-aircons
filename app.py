import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, make_response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

app = Flask(__name__)

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'bookings.db')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'site_config.json')
ADMIN_TOKEN = "hi-tech-admin-token-2026"

DEFAULT_CONFIG = {
    "tagline": "Smart Cooling for smart people",
    "phone1": "+91 80721 57403",
    "phone2": "+91 98423 83756",
    "email": "hitechaircons01@gmail.com",
    "address": "No: 68A, VVLP Complex, Near Retta Pillaiyaar Temple, Palakarai Main Road, Palakarai, Trichy – 620008, Tamil Nadu, India.",
    "gstin": "33ABJPI7098G1ZF",
    "whatsapp_num": "918072157403",
    "copyright_year": "2026",
    "owner_name": "ILYAS K",
    "owner_title": "Founder & Managing Director",
    "owner_quote": "At HI-TECH AIRCONS, our mission is to build trust through technical excellence. We combine premium engineering with absolute transparency so that every client experiences smart, stress-free comfort.",
    "email_alerts_enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "",
    "smtp_password": "",
    "alert_recipient_email": ""
}

# Dynamic Database Connection Resolver (Local SQLite vs Cloud Postgres)
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        import psycopg2
        return psycopg2.connect(database_url), True
    else:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn, False

# Database Initialization and Seeding from local files
def init_db():
    conn, is_pg = get_db_connection()
    cursor = conn.cursor()
    
    if is_pg:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                service VARCHAR(100) NOT NULL,
                notes TEXT,
                created_at VARCHAR(100) NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_config (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brand_products (
                brand_id VARCHAR(255) PRIMARY KEY,
                data TEXT NOT NULL
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brand_products (
                brand_id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        ''')
    conn.commit()
    
    # Seed configuration keys if empty
    cursor.execute("SELECT COUNT(*) FROM site_config")
    if cursor.fetchone()[0] == 0:
        config_data = DEFAULT_CONFIG.copy()
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data.update(json.load(f))
            except Exception as e:
                print("Could not read site_config.json for seeding:", e)
        
        placeholder = "%s" if is_pg else "?"
        for k, v in config_data.items():
            val_str = str(v) if not isinstance(v, bool) else ("true" if v else "false")
            cursor.execute(
                f"INSERT INTO site_config (key, value) VALUES ({placeholder}, {placeholder})",
                (k, val_str)
            )
        conn.commit()
        
    # Seed brand catalog if empty
    cursor.execute("SELECT COUNT(*) FROM brand_products")
    if cursor.fetchone()[0] == 0:
        products_file = os.path.join(os.path.dirname(__file__), 'brand_products.json')
        if os.path.exists(products_file):
            try:
                with open(products_file, 'r', encoding='utf-8') as f:
                    products_data = json.load(f)
                placeholder = "%s" if is_pg else "?"
                for brand, data in products_data.items():
                    cursor.execute(
                        f"INSERT INTO brand_products (brand_id, data) VALUES ({placeholder}, {placeholder})",
                        (brand, json.dumps(data))
                      )
                conn.commit()
            except Exception as e:
                print("Could not seed brand_products database:", e)
                
    conn.close()

# Initialize DB on Startup
try:
    init_db()
except Exception as e:
    print("Database connection/init failed. Will retry on demand:", e)

# Load configuration values from DB
def load_config():
    try:
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM site_config")
        rows = cursor.fetchall()
        conn.close()
        
        config = {}
        for r in rows:
            k, v = r[0], r[1]
            if v == "true":
                config[k] = True
            elif v == "false":
                config[k] = False
            elif k == "smtp_port":
                try:
                    config[k] = int(v)
                except:
                    config[k] = 587
            else:
                config[k] = v
                
        for k, v in DEFAULT_CONFIG.items():
            if k not in config:
                config[k] = v
        return config
    except Exception as e:
        print("Error loading config from database:", e)
        return DEFAULT_CONFIG

# SMTP EMAIL ALERT DISPATCHER (Dependency-free standard library SMTP call)
def send_email_alert(name, phone, service, notes):
    config = load_config()
    if not config.get('email_alerts_enabled'):
        return
        
    smtp_server = config.get('smtp_server', 'smtp.gmail.com')
    smtp_port = int(config.get('smtp_port', 587))
    sender_email = config.get('smtp_email')
    sender_password = config.get('smtp_password')
    if sender_password:
        sender_password = sender_password.replace(" ", "")
    recipient_email = config.get('alert_recipient_email')
    
    if not (sender_email and sender_password and recipient_email):
        print("Email alerts enabled but SMTP credentials or recipient settings are missing in configuration.")
        return
        
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "HI-TECH AIRCONS: New Booking Alert!"
    
    body = f"""HI-TECH AIRCONS - NEW BOOKING LEAD RECEIVED

Customer Name: {name}
Phone Number: {phone}
Requested Service: {service.upper()}
Additional Notes: {notes or '-'}
Received At: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email booking alert sent successfully!")
    except Exception as e:
        print("Failed to send email booking alert:", str(e))

def trigger_email_async(name, phone, service, notes):
    thread = threading.Thread(target=send_email_alert, args=(name, phone, service, notes))
    thread.daemon = True
    thread.start()

# 1. API: SUBMIT A BOOKING
@app.route('/api/book', methods=['POST'])
def save_booking():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        name = data.get('name')
        phone = data.get('phone')
        service = data.get('service')
        notes = data.get('notes', '')
        
        if not name or not phone or not service:
            return jsonify({"success": False, "error": "Missing required fields (name, phone, service)"}), 400
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        placeholder = "%s" if is_pg else "?"
        cursor.execute(
            f"INSERT INTO bookings (name, phone, service, notes, created_at) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})",
            (name, phone, service, notes, created_at)
        )
        conn.commit()
        conn.close()
        
        # Trigger Email alert notification asynchronously
        trigger_email_async(name, phone, service, notes)
        
        return jsonify({"success": True, "message": "Booking request saved successfully!"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 2. API: GET ALL BOOKINGS (Admin Only)
@app.route('/api/admin/bookings', methods=['GET'])
def get_bookings():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized Access"}), 401
        
    try:
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, service, notes, created_at FROM bookings ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        bookings = []
        for r in rows:
            bookings.append({
                "id": r[0],
                "name": r[1],
                "phone": r[2],
                "service": r[3],
                "notes": r[4],
                "created_at": r[5]
            })
            
        return jsonify({"success": True, "bookings": bookings}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3. API: DELETE A BOOKING (Admin Only)
@app.route('/api/admin/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized Access"}), 401
        
    try:
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        placeholder = "%s" if is_pg else "?"
        cursor.execute(f"DELETE FROM bookings WHERE id = {placeholder}", (booking_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Booking deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3b. API: UPDATE A BOOKING (Admin Only)
@app.route('/api/admin/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized Access"}), 401
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        name = data.get('name')
        phone = data.get('phone')
        service = data.get('service')
        notes = data.get('notes', '')
        
        if not name or not phone or not service:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
            
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        placeholder = "%s" if is_pg else "?"
        cursor.execute(
            f"UPDATE bookings SET name = {placeholder}, phone = {placeholder}, service = {placeholder}, notes = {placeholder} WHERE id = {placeholder}",
            (name, phone, service, notes, booking_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Booking updated successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3c. API: UPLOAD FILE (Admin Only)
@app.route('/api/admin/upload', methods=['POST'])
def upload_file():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized Access"}), 401
        
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files['file']
    target = request.form.get('target')
    
    if not file or not target:
        return jsonify({"success": False, "error": "Missing file or upload target"}), 400
        
    filename_map = {
        'logo': 'logo.jpg',
        'owner': 'owner.jpg',
        'hero-bg': 'hero-bg.png',
        'gallery-showroom': 'gallery-showroom.png',
        'gallery-split': 'gallery-split.png',
        'gallery-commercial-vrv': 'gallery-commercial-vrv.png',
        'gallery-repair-gas': 'gallery-repair-gas.png',
        'gallery-office-cassette': 'gallery-office-cassette.png',
        'gallery-repair-pcb': 'gallery-repair-pcb.png'
    }
    
    if target not in filename_map:
        return jsonify({"success": False, "error": "Invalid upload target"}), 400
        
    filename = filename_map[target]
    filepath = os.path.join(os.path.dirname(__file__), 'assets', filename)
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return jsonify({"success": True, "message": f"{target} updated successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Upload writing failed: {str(e)}"}), 500

# API: GET CONFIG
@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(load_config()), 200

# API: UPDATE CONFIG (Admin Only)
@app.route('/api/config', methods=['POST'])
def update_config():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized Access"}), 401
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        placeholder = "%s" if is_pg else "?"
        
        for k, v in data.items():
            val_str = str(v) if not isinstance(v, bool) else ("true" if v else "false")
            if is_pg:
                cursor.execute(
                    "INSERT INTO site_config (key, value) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                    (k, val_str)
                )
            else:
                cursor.execute("UPDATE site_config SET value = ? WHERE key = ?", (val_str, k))
                if cursor.rowcount == 0:
                    cursor.execute("INSERT INTO site_config (key, value) VALUES (?, ?)", (k, val_str))
                    
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Website configuration updated successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API: GET PRODUCTS
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT brand_id, data FROM brand_products")
        rows = cursor.fetchall()
        conn.close()
        
        products = {}
        for r in rows:
            products[r[0]] = json.loads(r[1])
            
        if not products:
            raise ValueError("No products found in DB")
        return jsonify(products), 200
    except Exception as e:
        # Fallback to local brand_products.json if DB is empty or fails
        products_file = os.path.join(os.path.dirname(__file__), 'brand_products.json')
        if os.path.exists(products_file):
            try:
                with open(products_file, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f)), 200
            except:
                pass
        return jsonify({"success": False, "error": str(e)}), 500

# API: UPDATE PRODUCTS (Admin Only)
@app.route('/api/products', methods=['POST'])
def update_products():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"success": False, "error": "Unauthorized Access"}), 401
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        conn, is_pg = get_db_connection()
        cursor = conn.cursor()
        
        for brand, brand_data in data.items():
            data_str = json.dumps(brand_data)
            if is_pg:
                cursor.execute(
                    "INSERT INTO brand_products (brand_id, data) ON CONFLICT (brand_id) DO UPDATE SET data = EXCLUDED.data",
                    (brand, data_str)
                )
            else:
                cursor.execute("UPDATE brand_products SET data = ? WHERE brand_id = ?", (data_str, brand))
                if cursor.rowcount == 0:
                    cursor.execute("INSERT INTO brand_products (brand_id, data) VALUES (?, ?)", (brand, data_str))
                    
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Brand products updated successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 4. ROUTE: ADMIN DASHBOARD HTML
@app.route('/admin')
def serve_admin_dashboard():
    return send_from_directory(os.path.dirname(__file__), 'admin.html')

# 5. ROUTE: STATIC WEBPAGE AND ASSETS
@app.route('/')
def serve_index():
    return send_from_directory(os.path.dirname(__file__), 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.dirname(__file__), path)

if __name__ == '__main__':
    print("Initializing Flask server on Port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=True)
