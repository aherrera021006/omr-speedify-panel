from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    # Crear admin por defecto si no existe
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin1234')  # Cambia esta contraseña
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('client_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Bienvenido, ' + user.username)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Acceso denegado')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/client')
@login_required
def client_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return render_template('client_dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
