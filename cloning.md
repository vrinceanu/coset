Here's a clean strategy to clone and deploy your Django project from GitHub to a new server:

## 1. Prepare the New Server

**Install system dependencies:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx -y
```

## 2. Set Up SSH Access to GitHub

```bash
# Generate SSH key on the new server
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy the public key
cat ~/.ssh/id_ed25519.pub
```
Then add this key to **GitHub → Settings → SSH and GPG Keys**.

## 3. Clone the Repository

```bash
cd /var/www/   # or your preferred directory
git clone git@github.com:your-org/your-repo.git
cd your-repo
```

## 4. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Never copy `.env` files via Git. Instead:
```bash
cp .env.example .env
nano .env  # Fill in DB credentials, SECRET_KEY, ALLOWED_HOSTS, DEBUG=False, etc.
```
Or use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)

## 6. Database Setup

```bash
# Run migrations
python manage.py migrate

# If copying data from old server:
# On OLD server:
python manage.py dumpdata > backup.json

# On NEW server:
python manage.py loaddata backup.json
```

## 7. Static & Media Files

```bash
python manage.py collectstatic --noinput

# If media files exist, rsync from old server:
rsync -avz old-server:/var/www/your-repo/media/ /var/www/your-repo/media/
```

## 8. Set Up Gunicorn

```bash
pip install gunicorn

# Test it works:
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
```

Create a systemd service `/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=Gunicorn Django
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/your-repo
ExecStart=/var/www/your-repo/venv/bin/gunicorn your_project.wsgi:application --bind unix:/run/gunicorn.sock
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable gunicorn && sudo systemctl start gunicorn
```

## 9. Configure Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ { root /var/www/your-repo; }
    location /media/  { root /var/www/your-repo; }

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/yourapp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 10. SSL (HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Future Deployments (Pull Updates)

```bash
cd /var/www/your-repo
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

---

## Key Checklist

| Item | Notes |
|---|---|
| `SECRET_KEY` | Must be unique per environment |
| `DEBUG=False` | Always in production |
| `ALLOWED_HOSTS` | Set to your domain/IP |
| DB credentials | Use env vars, never hardcode |
| Firewall | Open ports 80, 443 only |
| Backups | Set up DB backup cron job |

Consider automating step 10 with a simple deploy script or a CI/CD pipeline (GitHub Actions → SSH deploy) for repeatability.