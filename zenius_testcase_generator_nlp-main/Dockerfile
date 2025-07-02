FROM python:3.11

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV OPENAI_API_KEY=""
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
