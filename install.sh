#!/usr/bin/env bash
set -e

echo "Actualizando sistema..."
apt update && apt upgrade -y

echo "Instalando dependencias de sistema..."
apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git

echo "Configurando PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE DATABASE omr_panel;
CREATE USER omr_user WITH PASSWORD 'omr_pass';
GRANT ALL PRIVILEGES ON DATABASE omr_panel TO omr_user;
EOF

echo "Clonando repositorio (ya tienes el código, así que este paso es opcional)..."
# git clone https://github.com/tu_usuario/omr-speedify-panel.git /opt/omr-panel

echo "Creando entorno virtual y instalando dependencias Python..."
python3 -m venv /opt/omr-panel/venv
source /opt/omr-panel/venv/bin/activate
pip install --upgrade pip
pip install -r /opt/omr-panel/requirements.txt

echo "Configurando variables de entorno..."
cat > /opt/omr-panel/.env <<EOF
SECRET_KEY=cambia_esto_por_una_clave_segura
DATABASE_URL=postgresql://omr_user:omr_pass@localhost/omr_panel
EOF

echo "Creando base de datos y usuario admin..."
source /opt/omr-panel/venv/bin/activate
export FLASK_APP=/opt/omr-panel/app.py
python3 -c "
from app import app, db, User
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin1234')
        db.session.add(admin)
        db.session.commit()
"

echo "Configurando Nginx..."
cat > /etc/nginx/sites-available/omr-panel <<EOF
server {
    listen 80;
    server_name panel.todoserviciosya.com.co;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/omr-panel /etc/nginx/sites-enabled/

systemctl restart nginx

echo "¡Instalación completa! Ejecuta la app con:"
echo "source /opt/omr-panel/venv/bin/activate && flask run --host=0.0.0.0"
