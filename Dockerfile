FROM python:3.7.4-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .
ENTRYPOINT ./myrun.sh

# 10.74.68.2 port 1735
# docker run -it -p 8888:8888 -p 1735:1735 firebolts sh