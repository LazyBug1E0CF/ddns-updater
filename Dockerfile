FROM python:slim
ENV TZ Asia/Shanghai
ENV IP_SERVER=
ENV DDNS_PROVIDER ali
ENV ACCESS_KEY=
ENV ACCESS_SECRET=
ENV INTERVAL 5
WORKDIR /ddns
COPY main.py /ddns/ddns.py
COPY requirements.txt /ddns/requirements.txt
COPY start.sh /ddns/start.sh
RUN pip install -r requirements.txt
ENTRYPOINT ["sh", "./start.sh"]
