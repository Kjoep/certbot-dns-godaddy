#!/bin/bash

echo certbot_dns_godaddy:dns_godaddy_key=$GODADDY_KEY > godaddy.ini
echo certbot_dns_godaddy:dns_godaddy_secret=$GODADDY_SECRET >> godaddy.ini

certbot certonly $EXTRA -n -m $EMAIL --agree-tos -d *.$DOMAIN -a certbot-dns-godaddy:dns-godaddy \
        --certbot-dns-godaddy:dns-godaddy-credentials godaddy.ini

echo "Exposing certs as secrets..."

./kubectl create --dry-run=true -o yaml secret tls $SECRETNAME \
    --cert /etc/letsencrypt/live/$DOMAIN/fullchain.pem\
    --key /etc/letsencrypt/live/$DOMAIN/privkey.pem\
    > secret.yaml

./kubectl apply -f secret.yaml
for i in $(echo $TARGET_NAMESPACES | sed "s/,/ /g")
do
    echo "Exposing as secret in namespace ${i}"
    ./kubectl -n $i apply -f secret.yaml
done
