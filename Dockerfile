FROM python:3.9-slim

WORKDIR /app

RUN apt -y update && apt -y upgrade && apt install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install h5py --only-binary h5py

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]