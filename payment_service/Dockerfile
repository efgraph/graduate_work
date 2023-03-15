FROM python:3.8

WORKDIR /opt/payment

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY . .

RUN ["chmod", "+x", "./docker-entrypoint.sh"]
RUN ["chmod", "+x", "./wait-for-it.sh"]
ENTRYPOINT [ "./docker-entrypoint.sh" ]