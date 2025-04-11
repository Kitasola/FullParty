FROM python:3.11

RUN apt-get update && apt-get install -y git unzip curl && \
    pip install --upgrade pip

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash"]