#!/bin/bash
set -e

echo "=== 1/5: Updating packages and installing dependencies ==="
apt update
apt install -y python3-pip python3-venv git nginx libpq-dev

echo "=== 2/5: Cloning repository ==="
rm -rf /var/www/lantad
git clone https://github.com/KYmer-dotcom/Lantad-Crayfish-Lantad-.git /var/www/lantad

echo "=== 3/5: Setting up Python virtual environment ==="
cd /var/www/lantad
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt gunicorn

echo "=== 4/5: Running migrations and static files ==="
export USE_SQLITE=True
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput

echo "=== 5/5: Configuring Systemd & Nginx ==="
cat << 'EOF' > /etc/systemd/system/lantad.service
[Unit]
Description=Lantad Superworm & Crayfish Django App
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/lantad
Environment="PATH=/var/www/lantad/.venv/bin"
Environment="USE_SQLITE=True"
ExecStart=/var/www/lantad/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 core.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start lantad
systemctl enable lantad

cat << 'EOF' > /etc/nginx/sites-available/lantad
server {
    listen 80;
    server_name 187.77.150.222 lantadcrayfish.tech www.lantadcrayfish.tech;

    location /static/ {
        alias /var/www/lantad/staticfiles/;
    }

    location /media/ {
        alias /var/www/lantad/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/lantad /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

echo ""
echo "========================================================="
echo "   DEPLOYMENT SUCCESSFUL!                                "
echo "   Open your browser at: http://187.77.150.222           "
echo "========================================================="
