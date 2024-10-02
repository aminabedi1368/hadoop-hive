# Use a base image with Java installed
FROM ubuntu:23.10

# Set environment variables for Hadoop and Hive
ENV HADOOP_VERSION=3.3.1
ENV HIVE_VERSION=3.1.2
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
ENV HADOOP_HOME=/opt/hadoop
ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$HIVE_HOME/bin:$JAVA_HOME/bin

# Install dependencies: wget, SSH for Hadoop, and other utilities
RUN apt-get update && apt-get install -y \
    wget \
    ssh \
    rsync \
    python3 \
    openjdk-8-jdk \
    vim \
    default-mysql-client

# Download and install Hadoop
RUN wget http://archive.apache.org/dist/hadoop/core/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz \
    && tar -xzvf hadoop-$HADOOP_VERSION.tar.gz -C /opt/ \
    && mv /opt/hadoop-$HADOOP_VERSION /opt/hadoop \
    && rm hadoop-$HADOOP_VERSION.tar.gz

# Download and install Hive
RUN wget https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz \
    && tar -xzvf apache-hive-$HIVE_VERSION-bin.tar.gz -C /opt/ \
    && mv /opt/apache-hive-$HIVE_VERSION-bin /opt/hive \
    && rm apache-hive-$HIVE_VERSION-bin.tar.gz

# Install MySQL JDBC Driver for Hive
RUN wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.30.tar.gz \
    && tar -xzf mysql-connector-java-8.0.30.tar.gz -C /opt/ \
    && cp /opt/mysql-connector-java-8.0.30/mysql-connector-java-8.0.30.jar $HIVE_HOME/lib/ \
    && rm -rf /opt/mysql-connector-java-8.0.30 /opt/mysql-connector-java-8.0.30.tar.gz

# Configure Hadoop (core-site.xml, hdfs-site.xml)
COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml

# Configure Hive (hive-site.xml)
COPY hive-site.xml $HIVE_HOME/conf/hive-site.xml

RUN echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# SSH setup for Hadoop
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# Create necessary HDFS directories at startup
RUN mkdir -p /data/hdfs

# Startup script to initialize HDFS, start Hadoop, and Hive services
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ports for NameNode, DataNode, ResourceManager, NodeManager
EXPOSE 9870 9864 8088 8042

# Entry point for the container
ENTRYPOINT ["/entrypoint.sh"]
