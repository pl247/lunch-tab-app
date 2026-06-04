FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Create data directory and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data
VOLUME /app/data
EXPOSE 8723
ENV PORT=8723
ENV DB_PATH=/app/data/app.db
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8723"]
