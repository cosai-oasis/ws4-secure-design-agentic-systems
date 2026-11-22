FROM docker.io/library/maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -q
COPY src/ src/
RUN mvn package -q -DskipTests

FROM quay.io/keycloak/keycloak:26.5.2
COPY --from=builder /build/target/keycloak-agentic-spi-1.0.0-SNAPSHOT.jar /opt/keycloak/providers/
ENV KC_FEATURES=client-auth-federated,kubernetes-service-accounts,token-exchange,token-exchange-standard
RUN /opt/keycloak/bin/kc.sh build
