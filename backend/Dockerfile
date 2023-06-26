FROM python:3.11.4-slim

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get clean &&\
    apt-get autoremove -y &&\
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
    pip install --no-cache-dir -r requirements.txt

# Download wait-for-it.sh and make it executable
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

COPY . /app
RUN chmod +x start_script.sh

CMD ["/app/start_script.sh"]