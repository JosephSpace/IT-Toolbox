import sqlite3
import pyotp
import qrcode
from io import BytesIO
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from user_agents import parse

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'

# Profil resimleri için yükleme klasörü
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask-Login yapılandırması
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# SQLite Veritabanı Bağlantısı
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # users tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            bio TEXT,
            profile_image TEXT,
            role TEXT DEFAULT 'user',
            joined_date TEXT,
            notifications_blog INTEGER DEFAULT 1,
            notifications_news INTEGER DEFAULT 1,
            notifications_offers INTEGER DEFAULT 1,
            activity_logs INTEGER DEFAULT 0,
            two_factor_auth INTEGER DEFAULT 0,
            pin_code_enabled INTEGER DEFAULT 0,
            two_factor_secret TEXT
        )
    ''')

    # Yeni sütunları ekle (eğer yoksa)
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN activity_logs INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN two_factor_auth INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN pin_code_enabled INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN two_factor_secret TEXT')
    except sqlite3.OperationalError:
        pass

    # user_activities tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            device TEXT,
            ip_address TEXT,
            location TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()

    # Admin hesabı oluştur
    cursor.execute('SELECT 1 FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_email = 'hi@admin.com'
        admin_password = generate_password_hash('123')
        admin_joined_date = datetime.now().strftime('%d %b %Y')
        cursor.execute('''
            INSERT INTO users (username, email, password, first_name, last_name, joined_date, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', admin_email, admin_password, 'Admin', 'User', admin_joined_date, 'admin'))
        conn.commit()
        print("Admin hesabı oluşturuldu: Kullanıcı adı: admin, Şifre: 123")

    conn.close()

# Veritabanını başlat
init_db()

# User model
class User(UserMixin):
    def __init__(self, id, username, email, password, first_name="John", last_name="Smith", bio="", profile_image=None, role="user", joined_date=None, notifications=None, activity_logs=0, two_factor_auth=0, pin_code_enabled=0, two_factor_secret=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio
        self.profile_image = profile_image
        self.role = role
        self.joined_date = joined_date
        self.notifications = notifications or {
            "blog": True,
            "newsletter": True,
            "offers": True
        }
        self.activity_logs = activity_logs
        self.two_factor_auth = two_factor_auth
        self.pin_code_enabled = pin_code_enabled
        self.two_factor_secret = two_factor_secret

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        activity_logs = user[13] if len(user) > 13 else 0
        two_factor_auth = user[14] if len(user) > 14 else 0
        pin_code_enabled = user[15] if len(user) > 15 else 0
        two_factor_secret = user[16] if len(user) > 16 else None

        return User(
            id=user[0],
            username=user[1],
            email=user[2],
            password=user[3],
            first_name=user[4],
            last_name=user[5],
            bio=user[6],
            profile_image=user[7],
            role=user[8],
            joined_date=user[9],
            notifications={
                "blog": bool(user[10]),
                "newsletter": bool(user[11]),
                "offers": bool(user[12])
            },
            activity_logs=bool(activity_logs),
            two_factor_auth=bool(two_factor_auth),
            pin_code_enabled=bool(pin_code_enabled),
            two_factor_secret=two_factor_secret
        )
    return None

# Dosya yükleme için yardımcı fonksiyon
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Program verilerini yükle
with open('static/data/programs.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)

# Admin erişim kontrolü için dekoratör
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html', 
                         categories=categories, 
                         all_categories=categories, 
                         active_category=None, 
                         search_query=None)

@app.route('/category/<category_name>')
def show_category(category_name):
    formatted_category = category_name.replace('-', ' ').title()
    selected_category = next((c for c in categories if c['name'] == formatted_category), None)
    
    if selected_category:
        return render_template('index.html', 
                            categories=[selected_category], 
                            all_categories=categories,
                            active_category=formatted_category,
                            search_query=None)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return redirect(url_for('index'))
    
    search_results = []
    for category in categories:
        matching_programs = [p for p in category['programs'] 
                           if query in p['name'].lower() or query in p['description'].lower()]
        if matching_programs:
            search_results.append({'name': category['name'], 'programs': matching_programs})
    
    return render_template('index.html', 
                        categories=search_results, 
                        all_categories=categories,
                        active_category=None,
                        search_query=query)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('logCheck') else False
            
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[3], password):
                activity_logs = user[13] if len(user) > 13 else 0
                two_factor_auth = user[14] if len(user) > 14 else 0
                pin_code_enabled = user[15] if len(user) > 15 else 0
                two_factor_secret = user[16] if len(user) > 16 else None

                user_obj = User(
                    id=user[0],
                    username=user[1],
                    email=user[2],
                    password=user[3],
                    first_name=user[4],
                    last_name=user[5],
                    bio=user[6],
                    profile_image=user[7],
                    role=user[8],
                    joined_date=user[9],
                    notifications={
                        "blog": bool(user[10]),
                        "newsletter": bool(user[11]),
                        "offers": bool(user[12])
                    },
                    activity_logs=bool(activity_logs),
                    two_factor_auth=bool(two_factor_auth),
                    pin_code_enabled=bool(pin_code_enabled),
                    two_factor_secret=two_factor_secret
                )

                # 2FA kontrolü
                if user_obj.two_factor_auth:
                    # 2FA kodu doğrulama sayfasına yönlendir
                    session['user_id_to_verify'] = user_obj.id
                    session['remember'] = remember
                    return redirect(url_for('auth', form='verify_2fa'))
                else:
                    # 2FA yoksa direkt giriş yap
                    login_user(user_obj, remember=remember)

                    # Kullanıcı aktivitesini kaydet
                    if user_obj.activity_logs:
                        user_agent = parse(request.headers.get('User-Agent'))
                        device = f"{user_agent.browser.family} - {user_agent.os.family}"
                        ip_address = request.remote_addr
                        location = ip_address
                        timestamp = datetime.now().strftime('%d %b %Y, %H:%M:%S')

                        conn = sqlite3.connect('users.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO user_activities (user_id, device, ip_address, location, timestamp)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (user_obj.id, device, ip_address, location, timestamp))
                        conn.commit()
                        conn.close()

                    return redirect(url_for('index'))
            flash('Geçersiz e-posta veya şifre.', 'error')
            return redirect(url_for('auth', form='login'))

        elif form_type == 'register':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            terms_accepted = request.form.get('termCon')
            joined_date = datetime.now().strftime('%d %b %Y')

            if not all([username, email, password, confirm_password]):
                flash('Tüm alanlar doldurulmalıdır.', 'error')
            elif password != confirm_password:
                flash('Şifreler eşleşmiyor.', 'error')
            elif not terms_accepted:
                flash('Şartları ve koşulları kabul etmelisiniz.', 'error')
            else:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                try:
                    cursor.execute('SELECT 1 FROM users WHERE email = ?', (email,))
                    if cursor.fetchone():
                        flash('Bu e-posta zaten kayıtlı.', 'error')
                    else:
                        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
                        if cursor.fetchone():
                            flash('Bu kullanıcı adı zaten alınmış.', 'error')
                        else:
                            hashed_password = generate_password_hash(password)
                            cursor.execute('''
                                INSERT INTO users (username, email, password, first_name, last_name, joined_date, role)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (username, email, hashed_password, username, "", joined_date, 'user'))
                            conn.commit()
                            flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
                            return redirect(url_for('auth', form='login'))
                except sqlite3.Error as e:
                    flash('Kayıt sırasında bir hata oluştu: ' + str(e), 'error')
                finally:
                    conn.close()
            return redirect(url_for('auth', form='register'))

        elif form_type == 'verify_2fa':
            code = request.form.get('code')
            user_id = session.get('user_id_to_verify')
            remember = session.get('remember', False)

            if not user_id:
                flash('Geçersiz oturum. Lütfen tekrar giriş yapın.', 'error')
                return redirect(url_for('auth', form='login'))

            user = load_user(user_id)
            if not user:
                flash('Kullanıcı bulunamadı.', 'error')
                return redirect(url_for('auth', form='login'))

            totp = pyotp.TOTP(user.two_factor_secret)
            if totp.verify(code):
                login_user(user, remember=remember)

                # Kullanıcı aktivitesini kaydet
                if user.activity_logs:
                    user_agent = parse(request.headers.get('User-Agent'))
                    device = f"{user_agent.browser.family} - {user_agent.os.family}"
                    ip_address = request.remote_addr
                    location = ip_address
                    timestamp = datetime.now().strftime('%d %b %Y, %H:%M:%S')

                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO user_activities (user_id, device, ip_address, location, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user.id, device, ip_address, location, timestamp))
                    conn.commit()
                    conn.close()

                session.pop('user_id_to_verify', None)
                session.pop('remember', None)
                return redirect(url_for('index'))
            else:
                flash('Geçersiz doğrulama kodu.', 'error')
                return redirect(url_for('auth', form='verify_2fa'))

    form = request.args.get('form', 'login')
    return render_template('auth.html', active_form=form)

@app.route('/forgot_password')
def forgot_password():
    flash('Şifre sıfırlama özelliği henüz uygulanmadı.', 'info')
    return redirect(url_for('auth', form='login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profiles')
@login_required
def profiles():
    return render_template('profiles.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email')
    bio = request.form.get('bio')
    notifications_blog = 'notifications-blog' in request.form
    notifications_news = 'notifications-news' in request.form
    notifications_offers = 'notifications-offers' in request.form

    if not all([first_name, last_name, username, email]):
        flash('Tüm alanlar doldurulmalıdır.', 'error')
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT 1 FROM users WHERE email = ? AND id != ?', (email, current_user.id))
            if cursor.fetchone():
                flash('Bu e-posta başka bir kullanıcı tarafından kullanılıyor.', 'error')
            else:
                cursor.execute('SELECT 1 FROM users WHERE username = ? AND id != ?', (username, current_user.id))
                if cursor.fetchone():
                    flash('Bu kullanıcı adı zaten alınmış.', 'error')
                else:
                    cursor.execute('''
                        UPDATE users
                        SET first_name = ?, last_name = ?, username = ?, email = ?, bio = ?,
                            notifications_blog = ?, notifications_news = ?, notifications_offers = ?
                        WHERE id = ?
                    ''', (first_name, last_name, username, email, bio,
                          int(notifications_blog), int(notifications_news), int(notifications_offers),
                          current_user.id))
                    conn.commit()
                    flash('Profil başarıyla güncellendi.', 'success')
        except sqlite3.Error as e:
            flash('Profil güncellenirken bir hata oluştu: ' + str(e), 'error')
        finally:
            conn.close()
    return redirect(url_for('profiles'))

@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('Tüm şifre alanları doldurulmalıdır.', 'error')
    elif not check_password_hash(current_user.password, current_password):
        flash('Mevcut şifre yanlış.', 'error')
    elif new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor.', 'error')
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            hashed_password = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, current_user.id))
            conn.commit()
            flash('Şifre başarıyla güncellendi.', 'success')
        except sqlite3.Error as e:
            flash('Şifre güncellenirken bir hata oluştu: ' + str(e), 'error')
        finally:
            conn.close()
    return redirect(url_for('profiles'))

@app.route('/update_photo', methods=['POST'])
@login_required
def update_photo():
    if 'profile_image' not in request.files:
        flash('Dosya seçilmedi.', 'error')
        return redirect(url_for('profiles'))
    
    file = request.files['profile_image']
    if file.filename == '':
        flash('Dosya seçilmedi.', 'error')
        return redirect(url_for('profiles'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{current_user.id}.{file.filename.rsplit('.', 1)[1].lower()}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET profile_image = ? WHERE id = ?', (filename, current_user.id))
            conn.commit()
            flash('Profil resmi başarıyla güncellendi.', 'success')
        except sqlite3.Error as e:
            flash('Profil resmi güncellenirken bir hata oluştu: ' + str(e), 'error')
        finally:
            conn.close()
    else:
        flash('İzin verilen dosya türleri: png, jpg, jpeg, gif', 'error')
    
    return redirect(url_for('profiles'))

@app.route('/manage_users')
@login_required
@admin_required
def manage_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()

    user_list = []
    for user in users:
        activity_logs = user[13] if len(user) > 13 else 0
        two_factor_auth = user[14] if len(user) > 14 else 0
        pin_code_enabled = user[15] if len(user) > 15 else 0
        two_factor_secret = user[16] if len(user) > 16 else None

        user_obj = User(
            id=user[0],
            username=user[1],
            email=user[2],
            password=user[3],
            first_name=user[4],
            last_name=user[5],
            bio=user[6],
            profile_image=user[7],
            role=user[8],
            joined_date=user[9],
            notifications={
                "blog": bool(user[10]),
                "newsletter": bool(user[11]),
                "offers": bool(user[12])
            },
            activity_logs=bool(activity_logs),
            two_factor_auth=bool(two_factor_auth),
            pin_code_enabled=bool(pin_code_enabled),
            two_factor_secret=two_factor_secret
        )
        user_list.append(user_obj)

    return render_template('manage_users.html', users=user_list)

@app.route('/add_new_user', methods=['POST'])
@login_required
@admin_required
def add_new_user():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    bio = request.form.get('bio', '')
    joined_date = datetime.now().strftime('%d %b %Y')

    if not all([first_name, last_name, username, email, password]):
        flash('Tüm alanlar doldurulmalıdır.', 'error')
    else:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT 1 FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                flash('Bu e-posta zaten kayıtlı.', 'error')
            else:
                cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    flash('Bu kullanıcı adı zaten alınmış.', 'error')
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute('''
                        INSERT INTO users (username, email, password, first_name, last_name, bio, joined_date, role)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (username, email, hashed_password, first_name, last_name, bio, joined_date, role))
                    conn.commit()
                    flash('Yeni kullanıcı başarıyla eklendi.', 'success')
        except sqlite3.Error as e:
            flash('Kullanıcı eklenirken bir hata oluştu: ' + str(e), 'error')
        finally:
            conn.close()
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Kendi hesabınızı silemezsiniz.', 'error')
        return redirect(url_for('manage_users'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash('Kullanıcı başarıyla silindi.', 'success')
    except sqlite3.Error as e:
        flash('Kullanıcı silinirken bir hata oluştu: ' + str(e), 'error')
    finally:
        conn.close()
    return redirect(url_for('manage_users'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('manage_users'))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')

        if not all([first_name, last_name, email, username]):
            flash('Tüm alanlar doldurulmalıdır.', 'error')
        else:
            try:
                cursor.execute('UPDATE users SET first_name = ?, last_name = ?, email = ?, username = ? WHERE id = ?',
                               (first_name, last_name, email, username, user_id))
                conn.commit()
                flash('Kullanıcı bilgileri güncellendi.', 'success')
                return redirect(url_for('manage_users'))
            except sqlite3.Error as e:
                flash('Kullanıcı güncellenirken bir hata oluştu: ' + str(e), 'error')
            finally:
                conn.close()

    activity_logs = user[13] if len(user) > 13 else 0
    two_factor_auth = user[14] if len(user) > 14 else 0
    pin_code_enabled = user[15] if len(user) > 15 else 0
    two_factor_secret = user[16] if len(user) > 16 else None

    user_obj = User(
        id=user[0],
        username=user[1],
        email=user[2],
        password=user[3],
        first_name=user[4],
        last_name=user[5],
        bio=user[6],
        profile_image=user[7],
        role=user[8],
        joined_date=user[9],
        notifications={
            "blog": bool(user[10]),
            "newsletter": bool(user[11]),
            "offers": bool(user[12])
        },
        activity_logs=bool(activity_logs),
        two_factor_auth=bool(two_factor_auth),
        pin_code_enabled=bool(pin_code_enabled),
        two_factor_secret=two_factor_secret
    )
    conn.close()
    return render_template('edit_user.html', user=user_obj)

@app.route('/security', methods=['GET'])
@login_required
def security():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT device, ip_address, location, timestamp FROM user_activities WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5', (current_user.id,))
    recent_activities = [
        {"device": row[0], "ip": row[1], "location": row[2], "time": row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()

    return render_template('security.html', recent_activities=recent_activities)

@app.route('/toggle_activity_logs', methods=['POST'])
@login_required
def toggle_activity_logs():
    activity_logs = 'activity_logs' in request.form
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET activity_logs = ? WHERE id = ?', (int(activity_logs), current_user.id))
        conn.commit()
        flash('Aktivite logları güncellendi.', 'success')
    except sqlite3.Error as e:
        flash('Ayar güncellenirken bir hata oluştu: ' + str(e), 'error')
    finally:
        conn.close()
    return redirect(url_for('security'))

@app.route('/toggle_two_factor_auth', methods=['POST'])
@login_required
def toggle_two_factor_auth():
    new_state = not current_user.two_factor_auth
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        if new_state and not current_user.two_factor_secret:
            secret = pyotp.random_base32()
            cursor.execute('UPDATE users SET two_factor_secret = ?, two_factor_auth = ? WHERE id = ?',
                           (secret, int(new_state), current_user.id))
            conn.commit()
            flash('İki faktörlü doğrulama etkinleştirildi. Lütfen QR kodunu tarayın.', 'success')
            return redirect(url_for('setup_2fa'))
        else:
            cursor.execute('UPDATE users SET two_factor_auth = ? WHERE id = ?',
                           (int(new_state), current_user.id))
            conn.commit()
            flash('İki faktörlü doğrulama güncellendi.', 'success')
    except sqlite3.Error as e:
        flash('Ayar güncellenirken bir hata oluştu: ' + str(e), 'error')
    finally:
        conn.close()
    return redirect(url_for('security'))

@app.route('/setup_2fa', methods=['GET'])
@login_required
def setup_2fa():
    if not current_user.two_factor_secret:
        flash('2FA sırrı bulunamadı.', 'error')
        return redirect(url_for('security'))

    totp_uri = pyotp.totp.TOTP(current_user.two_factor_secret).provisioning_uri(
        name=current_user.email,
        issuer_name='IT Toolbox'
    )

    qr = qrcode.QRCode()
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return render_template('setup_2fa.html', qr_code=qr_code_base64, secret=current_user.two_factor_secret)

@app.route('/toggle_pin_code', methods=['POST'])
@login_required
def toggle_pin_code():
    pin_code_enabled = 'pin_code' in request.form
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET pin_code_enabled = ? WHERE id = ?', (int(pin_code_enabled), current_user.id))
        conn.commit()
        flash('PIN kodu ayarı güncellendi.', 'success')
    except sqlite3.Error as e:
        flash('Ayar güncellenirken bir hata oluştu: ' + str(e), 'error')
    finally:
        conn.close()
    return redirect(url_for('security'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)