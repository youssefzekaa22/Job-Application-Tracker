FROM python:3.11 as builder 

WORKDIR /app

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.11-slim

RUN useradd -m -u 1000 youssef

WORKDIR /app

COPY --from=builder --chown=youssef:youssef /root/.local /home/youssef/.local

COPY --chown=youssef:youssef . .

ENV PATH=/home/youssef/.local/bin:$PATH

USER youssef

EXPOSE 5000

CMD ["python","app.py"]




