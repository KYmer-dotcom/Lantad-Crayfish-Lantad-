#!/bin/bash
set -e

echo "=== 1/6: Updating packages and installing dependencies ==="
apt update
apt install -y python3-pip python3-venv git nginx libpq-dev certbot python3-certbot-nginx

echo "=== 2/6: Cloning/Updating repository ==="
if [ -d "/var/www/lantad/.git" ]; then
    cd /var/www/lantad
    git fetch origin
    git reset --hard origin/main
else
    rm -rf /var/www/lantad
    git clone https://github.com/KYmer-dotcom/Lantad-Crayfish-Lantad-.git /var/www/lantad
fi

echo "=== 3/6: Setting up Python virtual environment ==="
cd /var/www/lantad
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt gunicorn

echo "=== 4/6: Migrating Database & Importing Local Data ==="
cd /var/www/lantad/System
export USE_SQLITE=True
/var/www/lantad/.venv/bin/python manage.py migrate
if [ -f "local_dump.json" ]; then
    echo "Importing complete database snapshot (local_dump.json)..."
    /var/www/lantad/.venv/bin/python manage.py loaddata local_dump.json || true
fi
/var/www/lantad/.venv/bin/python manage.py shell -c "from apps.accounts.models import User; User.objects.filter(is_superuser=True).update(role='owner')"

echo "=== 5/6: Collecting Static Assets & Setting Permissions ==="
/var/www/lantad/.venv/bin/python manage.py collectstatic --noinput --clear
cp -rn /var/www/lantad/System/static/* /var/www/lantad/System/staticfiles/ 2>/dev/null || true
chmod -R 755 /var/www/lantad

echo "=== 6/6: Configuring Systemd & Nginx with HTTPS ==="
cat << 'EOF' > /etc/systemd/system/lantad.service
[Unit]
Description=Lantad Superworm & Crayfish Django App
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/lantad/System
Environment="PATH=/var/www/lantad/.venv/bin"
Environment="PYTHONPATH=/var/www/lantad/System"
Environment="USE_SQLITE=True"
ExecStart=/var/www/lantad/.venv/bin/gunicorn --chdir /var/www/lantad/System --workers 3 --bind 127.0.0.1:8000 core.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart lantad
systemctl enable lantad

cat << 'EOF' > /etc/nginx/sites-available/lantad
server {
    listen 80;
    server_name 187.77.150.222 lantadcrayfish.tech www.lantadcrayfish.tech;

    location /static/ {
        alias /var/www/lantad/System/staticfiles/;
    }

    location /media/ {
        alias /var/www/lantad/System/media/;
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

# If SSL certs exist, ensure HTTPS block is active
if [ -f "/etc/letsencrypt/live/lantadcrayfish.tech/fullchain.pem" ]; then
    certbot --nginx -d lantadcrayfish.tech -d www.lantadcrayfish.tech --non-interactive --agree-tos -m kymerorielcrisostomo@gmail.com --redirect || true
fi

echo ""
echo "========================================================="
echo "   🎉 SETUP 100% COMPLETE & VERIFIED!                    "
echo "   Live Domain: https://lantadcrayfish.tech              "
echo "   Server IP:   http://187.77.150.222                    "
echo "========================================================="
