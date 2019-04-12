FROM python:3.7
RUN apt-get update
RUN apt-get install -y curl
RUN mkdir /data
WORKDIR /data
COPY requirements.txt /data
RUN pip install -r requirements.txt
COPY setup.py /data/
COPY certbot_dns_godaddy /data/certbot_dns_godaddy
RUN pip install -e .

run curl -LO https://storage.googleapis.com/kubernetes-release/release/\
$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
run chmod +x ./kubectl

ARG GODADDY_KEY
ARG GODADDY_SECRET
ARG EMAIL
ARG DOMAIN
ARG SECRETNAME

ADD entrypoint.sh .
CMD ["./entrypoint.sh"]
