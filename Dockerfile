FROM python:3.9-slim

WORKDIR /app

# 必要なパッケージをインストール
RUN apt -y update && apt -y upgrade && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
RUN apt -y install libopencv-dev

# アプリケーションの依存関係をコピーしインストール
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install h5py --only-binary h5py
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# アプリケーションの起動
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
