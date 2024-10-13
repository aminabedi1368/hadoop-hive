# Hadoop-Hive Docker Environment

This project provides a ready-to-use environment for running **Hadoop** and **Hive** in Docker containers, along with a **MySQL** container for Hive metastore. The Hadoop-Hive setup is based on a custom Docker image that includes pre-configured Hadoop and Hive services.

## Features

- **Hadoop 3.3.1**: HDFS, YARN, and MapReduce services.
- **Hive 3.1.2**: Data warehouse software that facilitates reading, writing, and managing large datasets residing in distributed storage using SQL.
- **MySQL 8.0**: Database for Hive metastore.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. **Pull the Docker image** from Docker Hub:

   ```bash
   docker pull myusername/hadoop-hive:v1
   ```

2. **Set up the environment** using Docker Compose:

   Clone this repository and navigate to the directory containing the `docker-compose.yml` file.

   ```bash
   git clone https://github.com/yourusername/hadoop-hive-setup.git
   cd hadoop-hive-setup
   ```

3. **Run the Docker Compose environment**:

   To start the services, run the following command:

   ```bash
   docker-compose up
   ```

   This will start two containers:
   - `hadoop-hive`: Container for Hadoop and Hive services.
   - `mysql`: Container for the MySQL database that serves as Hive's metastore.

4. **Accessing Hadoop and Hive**:

   - **Hadoop Web UI**:
     - NameNode: `http://localhost:9870`
     - DataNode: `http://localhost:9864`
     - ResourceManager: `http://localhost:8088`
     - NodeManager: `http://localhost:8042`
   
   - **Hive**:
     - HiveServer2 is available at port `10000`.
     - The Hive Metastore is available at port `10002`.

5. **Stopping the environment**:

   To stop the running containers, use:

   ```bash
   docker-compose down
   ```

## Running a Hive Query

Once the containers are up, you can connect to Hive and run queries:

1. **Connect to the Hive container**:

   ```bash
   docker exec -it hadoop-hive /bin/bash
   ```

2. **Start the Hive CLI**:

   Inside the container, run the following command to start Hive:

   ```bash
   hive
   ```

3. **Run a simple Hive query**:

   Inside the Hive CLI, run:

   ```sql
   CREATE TABLE test_table (id INT, name STRING);
   SHOW TABLES;
   ```

## Notes

- Ensure that you have a working internet connection while pulling the images.
- You can modify the `docker-compose.yml` file to change ports or other configuration settings as needed.
  
## Volumes

- `./data/hdfs:/data/hdfs`: HDFS data is stored on your host system in the `data/hdfs` directory.
- `./mnt/import:/mnt/import`: Use this directory to import files into HDFS.
- `./mnt/java:/mnt/java`: Java files for Hadoop jobs can be placed here.
