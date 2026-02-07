FROM apache/hive:4.0.0

USER root

# Download PostgreSQL JDBC Driver
ADD https://jdbc.postgresql.org/download/postgresql-42.7.1.jar /opt/hive/lib/postgresql-42.7.1.jar

# Download Hadoop AWS and AWS SDK for S3A support
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar /opt/hive/lib/hadoop-aws-3.3.4.jar
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.367/aws-java-sdk-bundle-1.12.367.jar /opt/hive/lib/aws-java-sdk-bundle-1.12.367.jar

# Set proper permissions
RUN chmod 644 /opt/hive/lib/*.jar && \
    chown hive:hive /opt/hive/lib/*.jar

USER hive
