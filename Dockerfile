FROM python:3.6-slim

RUN apt-get update && apt-get install -y unixodbc-dev gcc g++ --no-install-recommends

WORKDIR /c2dh-nerd

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

RUN apt-get purge -y --auto-remove unixodbc-dev gcc g++
RUN rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8002

ENV PYTHONPATH=/c2dh-nerd

CMD ["python", "-m", "c2dh_nerd"]
