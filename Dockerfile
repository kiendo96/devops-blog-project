FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# ENV FLASK_APP=run.py
ENV FLASK_ENV=production

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot
RUN mkdir -p /app/uploads/images && chown -R nonroot:nonroot /app/uploads

COPY . .
RUN chown -R nonroot:nonroot /app

USER nonroot
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
