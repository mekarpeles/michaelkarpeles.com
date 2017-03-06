# michaelkarpeles.com

michaelkarpeles.com is currently registered (along with many of my other domains, unfortunately) on godaddy.com; despite moral qualms about their service, I have made an executive decision that I cannot be bothered to change it (judge me accordingly). The website is currently hosted on a linode. Login credentials, in the event of an emergency, can likely be sourced from my father, Dr. Richard Karpeles.

    ssh mek@michaelkarpeles.com

## Installation

In the event something happens to me and the website/service needs to be reinstalled, michaelkarpeles.com runs flask as a uwsgi service under nginx.

### Dependencies

    sudo apt-get install nginx uwsgi python-pip
    sudo pip install flask

### uwsgi.ini

A file /var/www/michaelkarpeles.com/uwsgi.ini must be created with contents:


      [uwsgi]
      #application's base folder
      base = /var/www/michaelkarpeles.com

      #python module to import
      app = app
      module = %(app)

      #home = %(base)/venv
      pythonpath = /usr/local/lib/python3.4/site-packages

      #socket file's location
      socket = /var/www/michaelkarpeles.com/%n.sock

      #permissions for the socket file
      chmod-socket = 666

      #the variable that holds a flask application inside the module imported at line #6
      callable = app

      #location of log files
      logto = /var/log/uwsgi/%n.logmek@production:/var/www/michaelkarpeles.com


### nginx

The nginx config looks something like this. You may want to create a new SSL cert (free using StartSSL) and put it in the certificate directory listed below:

  server {
      listen 443 ssl;
      server_name michaelkarpeles.com www.michaelkarpeles.com;

      ssl_certificate      /var/www/ssl/michaelkarpeles.com/ssl-unified.crt;
      ssl_certificate_key  /var/www/ssl/michaelkarpeles.com/ssl.key;

      client_max_body_size 75M;
      root /var/www/michaelkarpeles.com/;
      access_log /var/log/nginx/localhost.access.log;


      location /robots.txt {
          alias /var/www/michaelkarpeles.com/static/robots.txt;
      }

      location ~ ^/(favicon\.ico).*$ {
          root /var/www/michaelkarpeles.com/static/;
          return 204;
          access_log     off;
          log_not_found  off;
      }

      location /static/ {
          root /var/www/michaelkarpeles.com;
          if (-f $request_filename) {
              rewrite ^/static/(.*)$  /static/$1 break;
          }
      }

      location ~* \.(js|css|jpg|jpeg|gif|png|ico|svg)$ {
          if (-f $request_filename) {
              expires max;
              break;
          }
      }

      location / { try_files $uri @yourapplication; }
      location @yourapplication {
          set $cors "true";
          include uwsgi_params;
          uwsgi_pass unix:/var/www/michaelkarpeles.com/uwsgi.sock;
      }
  }

## Restarting

There is a script in my home directory oh mek@michaelkarpeles.com, /home/mek/restart.sh which can be run as `sudo bash ./restart.sh` within a tmux session. Otherwise, you can run `cd /var/www/michaelkarpeles.com;sudo uwsgi --ini uwsgi.ini &` (assuming this repo lives in /var/www/michaelkarpeles.com).
