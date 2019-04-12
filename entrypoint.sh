#!/bin/bash

echo certbot_dns_godaddy:dns_godaddy_key=$GODADDY_KEY > godaddy.ini
echo certbot_dns_godaddy:dns_godaddy_secret=$GODADDY_SECRET >> godaddy.ini

certbot certonly -n -m $EMAIL --agree-tos -d *.$DOMAIN -a certbot-dns-godaddy:dns-godaddy \
        --certbot-dns-godaddy:dns-godaddy-credentials godaddy.ini

echo "Exposing certs as secrets..."

./kubectl create --dry-run=true -o yaml secret generic $SECRETNAME \
    --from-file=/etc/letsencrypt/live/$DOMAIN/cert.pem\
    --from-file=/etc/letsencrypt/live/$DOMAIN/fullchain.pem\
    --from-file=/etc/letsencrypt/live/$DOMAIN/chain.pem\
    --from-file=/etc/letsencrypt/live/$DOMAIN/privkey.pem\
    > secret.yaml

./kubectl apply -f secret.yaml
