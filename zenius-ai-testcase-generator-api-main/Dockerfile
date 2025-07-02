FROM openjdk:17-jdk-slim

WORKDIR /app

COPY build/libs/zenius-ai-testcase-generator-api-0.0.1-SNAPSHOT.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
