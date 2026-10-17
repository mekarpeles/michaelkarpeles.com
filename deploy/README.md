# Deploying the FastAPI port on NEW (test via mekarpeles.com)

This branch (`fastapi-port`) replaces the Python 2 Flask app (`mekarpeles/app.py`) with a
Python 3 FastAPI app (`mekarpeles/asgi.py`) that renders the same templates/static and keeps
the same routes. `/posts`, `/rss`, `/edit` still call the external `https://graph.global` API.

## 1. Code + venv (on NEW, as your user)
```bash
sudo git clone -b fastapi-port git@github.com:mekarpeles/michaelkarpeles.com.git /srv/michaelkarpeles.com
sudo chown -R www-data:www-data /srv/michaelkarpeles.com
cd /srv/michaelkarpeles.com
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install -r requirements.txt
```

## 2. Service (uvicorn on 127.0.0.1:8090)
```bash
sudo cp deploy/michaelkarpeles.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now michaelkarpeles
systemctl status michaelkarpeles --no-pager
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8090/      # expect 200
```

## 3. nginx vhost for mekarpeles.com + cert
```bash
sudo cp deploy/nginx-mekarpeles.com.conf /etc/nginx/sites-available/mekarpeles.com
sudo ln -sfn ../sites-available/mekarpeles.com /etc/nginx/sites-enabled/mekarpeles.com
# cert via meksrv's DNS-01 helper (token already configured on NEW):
sudo certbot certonly --manual --preferred-challenges dns \
  --manual-auth-hook "$HOME/meksrv/bin/gd-dns-hook.sh add" \
  --manual-cleanup-hook "$HOME/meksrv/bin/gd-dns-hook.sh del" \
  --cert-name mekarpeles.com -d mekarpeles.com -d www.mekarpeles.com \
  --non-interactive --agree-tos -m mek@archive.org --keep-until-expiring
sudo nginx -t && sudo systemctl reload nginx
```

## 4. Point mekarpeles.com DNS -> NEW
(Claude does this via GoDaddy API once the above is verified on NEW with `--resolve`.)
mek.fyi stays on OLD throughout, so nothing production is touched while testing on mekarpeles.com.

## Notes
- The app is cwd-independent (templates/static resolved relative to the package).
- Logs: `journalctl -u michaelkarpeles -f`
- To update: `git pull` in /srv/michaelkarpeles.com && `sudo systemctl restart michaelkarpeles`.
