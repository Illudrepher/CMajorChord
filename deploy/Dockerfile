FROM python:3.10-slim
RUN apt-get update && apt-get install -y \
    ffmpeg \
    openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN mkdir -p output
RUN mkdir -p files
COPY mir/requirements.txt /app/mir/requirements.txt
RUN pip install --no-cache-dir -r /app/mir/requirements.txt
COPY mir/ /app/mir
RUN chmod +x /app/mir/analyze.sh
COPY backend/target/app.jar /app/app.jar
EXPOSE 8848
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
1
