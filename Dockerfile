FROM python:3.9-slim

WORKDIR /app

RUN apt -y update && apt -y upgrade
# RUN apt -y install libopencv-dev
RUN pip install --upgrade pip
RUN pip install h5py --only-binary h5py

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
