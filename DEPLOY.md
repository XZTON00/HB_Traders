# H.B. Trader's — VPS par Production Deployment Guide

Target: **https://hbtraders.com** (Ubuntu 22.04/24.04 VPS, Nginx + Gunicorn + PostgreSQL + systemd + Let's Encrypt SSL)

Yeh guide step-by-step hai — upar se neeche follow karo. Har jagah `hbtraders.com` aur `YOUR_VPS_IP` ko apne actual values se replace karna.

---

## 0. Pehle se chahiye

- Ek VPS (Ubuntu 22.04 ya 24.04), root/sudo access ke saath
- Domain **hbtraders.com** (aapke registrar — GoDaddy, Namecheap, etc. — mein registered)
- Local machine par yeh project ka zip

---

## 1. DNS — domain ko VPS se point karo

Apne domain registrar / DNS provider ke panel mein jaake yeh **A records** add karo:

| Type | Name/Host | Value           | TTL  |
|------|-----------|-----------------|------|
| A    | @         | `YOUR_VPS_IP`   | Auto |
| A    | www       | `YOUR_VPS_IP`   | Auto |

- `@` = `hbtraders.com`, `www` = `www.hbtraders.com` — dono same VPS IP par point honi chahiye.
- DNS propagate hone mein 10 min se 24 hours tak lag sakte hain. Check karne ke liye:
  ```bash
  dig +short hbtraders.com
  dig +short www.hbtraders.com
  ```
  Dono commands aapka VPS IP return karein, tabhi aage (SSL step) badhna.

---

## 2. VPS setup — packages install

VPS par SSH karke:

```bash
ssh root@YOUR_VPS_IP

apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip \
  postgresql postgresql-contrib \
  nginx \
  certbot python3-certbot-nginx \
  git ufw
```

Firewall (agar `ufw` on karna hai):

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

Ek dedicated non-root user banao jo app run karega:

```bash
adduser hbtrader
usermod -aG www-data hbtrader
```

Baaki sab commands **hbtrader user** se chalao (`su - hbtrader`), root se nahi — sirf systemd/nginx install wale commands root/sudo se hote hain.

---

## 3. PostgreSQL configuration

```bash
sudo -u postgres psql
```

Psql shell ke andar:

```sql
CREATE DATABASE hbtrader;
CREATE USER hbtrader WITH PASSWORD 'apna-strong-password-yahan-daalo';
ALTER ROLE hbtrader SET client_encoding TO 'utf8';
ALTER ROLE hbtrader SET default_transaction_isolation TO 'read committed';
ALTER ROLE hbtrader SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE hbtrader TO hbtrader;
\q
```

Yeh `hbtrader` DB/user hi `.env` file mein `DB_NAME` / `DB_USER` / `DB_PASSWORD` banenge (step 5 mein).

---

## 4. Project code VPS par le jaao

`hbtrader` user ban ke, uske home directory mein project daalo — chahe `git clone` se, chahe zip upload karke:

```bash
su - hbtrader
cd ~

# Option A: agar GitHub par hai
git clone https://github.com/your-username/hbtrader.git
cd hbtrader

# Option B: agar zip upload kiya (scp se local se upload karo)
#   local machine se:  scp hbtrader_django_project.zip hbtrader@YOUR_VPS_IP:~
#   phir VPS par:
unzip hbtrader_django_project.zip
cd hbtrader
```

Virtual environment banao aur production dependencies install karo:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt
```

---

## 5. `.env` file banao (production config)

```bash
cp .env.example .env
nano .env
```

Yeh values fill karo:

```ini
SECRET_KEY=<neeche wali command se generate karo>
DEBUG=False
ALLOWED_HOSTS=hbtraders.com,www.hbtraders.com
CSRF_TRUSTED_ORIGINS=https://hbtraders.com,https://www.hbtraders.com
TIME_ZONE=Asia/Kolkata

DB_ENGINE=postgres
DB_NAME=hbtrader
DB_USER=hbtrader
DB_PASSWORD=<step 3 wala password>
DB_HOST=localhost
DB_PORT=5432

SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

Strong `SECRET_KEY` generate karne ke liye:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

`.env` file kabhi git mein commit mat karna (`.gitignore` mein already `.env` add hai).

---

## 6. Database migration

```bash
source venv/bin/activate     # agar already active nahi hai
python manage.py migrate
```

Yeh saare tables (Product, ProductSpec, BusinessDetail, auth users, sessions, etc.) production Postgres DB mein bana dega.

---

## 7. Admin account banao

```bash
python manage.py createsuperuser
```

Username, email, password poochega — apne actual admin credentials daalo (yeh dev wale `admin/admin12345` se **alag** hone chahiye).

---

## 8. Initial catalog seed

Original 20 placeholder items + business details (address, phone, email) load karne ke liye:

```bash
python manage.py seed_catalog
```

Baad mein `/admin/` se real product names, prices, images, descriptions daal sakte ho — yeh command sirf ek starting point deta hai.

---

## 9. Static/media files collect karo

```bash
python manage.py collectstatic --noinput
```

Yeh sab CSS/admin static files `staticfiles/` folder mein jama kar dega — Nginx yahin se directly serve karega (step 11), Django/Gunicorn ko har request pe touch nahi karna padega.

`media/` folder (product images) already `MEDIA_ROOT` se point hota hai — koi extra command nahi chahiye, bas folder exist karna chahiye:

```bash
mkdir -p media
```

---

## 10. Gunicorn + systemd (automatic restart)

Socket aur log directories banao (root se):

```bash
exit   # hbtrader user se root pe wapas
mkdir -p /run/hbtrader /var/log/hbtrader
chown hbtrader:www-data /run/hbtrader /var/log/hbtrader
```

`/run` reboot pe clear ho jata hai, isliye ek tmpfiles rule bhi bana do taaki restart ke baad socket dir wapas ban jaye:

```bash
cat > /etc/tmpfiles.d/hbtrader.conf << 'EOF'
d /run/hbtrader 0775 hbtrader www-data -
EOF
```

Systemd service install karo:

```bash
cp /home/hbtrader/hbtrader/deploy/hbtrader.service /etc/systemd/system/hbtrader.service
systemctl daemon-reload
systemctl enable --now hbtrader
systemctl status hbtrader
```

`enable` hi automatic-restart-on-boot deta hai; service file ke andar `Restart=on-failure` crash hone par bhi wapas start kar deta hai. Logs dekhne ke liye:

```bash
journalctl -u hbtrader -f
tail -f /var/log/hbtrader/gunicorn-error.log
```

---

## 11. Nginx configuration

```bash
cp /home/hbtrader/hbtrader/deploy/nginx_hbtraders.com.conf /etc/nginx/sites-available/hbtraders.com
ln -s /etc/nginx/sites-available/hbtraders.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default   # default page hata do

nginx -t          # config test karo
systemctl reload nginx
```

Is point pe `http://hbtraders.com` already Gunicorn tak proxy ho raha hoga (SSL abhi baaki hai).

---

## 12. SSL / HTTPS (Let's Encrypt)

DNS (step 1) propagate ho chuka ho, tabhi yeh chalao:

```bash
certbot --nginx -d hbtraders.com -d www.hbtraders.com
```

Certbot automatically:
- SSL certificate issue karega
- `nginx_hbtraders.com.conf` ko edit karke `ssl_certificate` / `ssl_certificate_key` lines add karega
- HTTP → HTTPS redirect confirm karega

Auto-renewal already systemd timer se built-in hota hai; verify karo:

```bash
systemctl status certbot.timer
certbot renew --dry-run
```

---

## 13. Final check

Browser mein khol ke dekho:

- **https://hbtraders.com** — catalog page, SSL padlock ke saath
- **https://hbtraders.com/login/** aur **/register/** — customer login
- **https://hbtraders.com/admin/** — admin panel (step 7 wale credentials se login)

Command line se bhi quick check:

```bash
curl -I https://hbtraders.com
curl -I http://hbtraders.com     # 301 redirect to https dikhna chahiye
```

---

## Future updates deploy karne ka tareeka

Jab bhi code/design mein change karo:

```bash
su - hbtrader
cd ~/hbtrader
source venv/bin/activate

git pull                              # ya naya zip upload karke replace karo
pip install -r requirements-prod.txt  # agar dependencies badli hon
python manage.py migrate              # agar models badle hon
python manage.py collectstatic --noinput

exit  # root pe
systemctl restart hbtrader
```

`systemctl restart hbtrader` naye code ko load karega (kyunki `preload_app = True` hai Gunicorn config mein, isliye reload nahi — pura restart chahiye).

---

## Troubleshooting

| Problem | Check |
|---|---|
| 502 Bad Gateway | `systemctl status hbtrader`, `journalctl -u hbtrader -f` — Gunicorn crash hua ya nahi |
| Static/CSS missing | `python manage.py collectstatic --noinput` chalaya? `STATIC_ROOT` folder Nginx `alias` se match karta hai? |
| Database connection error | `.env` mein `DB_PASSWORD` sahi hai? `systemctl status postgresql` |
| SSL fail | DNS propagate ho chuka? `dig +short hbtraders.com` VPS IP dikha raha ho tabhi certbot chalao |
| 400 Bad Request | `.env` mein `ALLOWED_HOSTS` mein domain missing to nahi |
| CSRF errors on forms | `.env` mein `CSRF_TRUSTED_ORIGINS` mein `https://` prefix ke saath domain hai ya nahi |
