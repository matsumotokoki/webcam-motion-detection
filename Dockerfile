FROM python:3.9-slim

ENV TF_CPP_MIN_LOG_LEVEL=2
WORKDIR /app

# 必要なパッケージをインストール
RUN apt -y update && apt -y upgrade && apt install -y \
    libgl1-mesa-glx libopencv-dev\
    && rm -rf /var/lib/apt/lists/*

# アプリケーションの依存関係をコピーしインストール
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install h5py --only-binary h5py
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# アプリケーションの起動
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app","--timeout", "900"]
