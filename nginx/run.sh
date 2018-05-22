#!/bin/bash

# Now actually start nginx
service nginx start

# Create new Certificates if not in place
if [ ! -d "/etc/letsencrypt/live/#NGINX_HOST/fullchain.pem" ]; then
    if [ ! -d "/etc/letsencrypt/live/#NGINX_HOST/privkey.pem" ]; then
        if [ -n $TEST_CERTIFICATES ]; then
            if [ $TEST_CERTIFICATES == "true" ]
              then
                ./certbot-auto --nginx -n --agree-tos -m "admin@#NGINX_HOST" -d #NGINX_HOST --test-cert
              elif [ $TEST_CERTIFICATES == "false" ]
              then
                ./certbot-auto --nginx -n --agree-tos -m "admin@#NGINX_HOST" -d #NGINX_HOST
              fi
        else
            ./certbot-auto --nginx -n --agree-tos -m "admin@#NGINX_HOST" -d #NGINX_HOST
        fi
    else
        echo "Private Key missing!"
        return 0
    fi
fi

# Start cron for the automatic renewal of certificates
while true; do
    ./certbot-auto renew --quiet --no-self-upgrade
    sleep 300
done