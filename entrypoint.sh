#!/bin/bash

# Start SSH service for Hadoop
service ssh start

# Format HDFS if not already formatted
if [ ! -d "/data/hdfs/namenode" ]; then
    hdfs namenode -format
fi

# Start Hadoop HDFS services
start-dfs.sh
start-yarn.sh

# Create a directory in HDFS
hdfs dfs -mkdir -p /user/hadoop

# Initialize Hive Metastore schema using MySQL
if ! mysql -u"$HIVE_METASTORE_USER" -p"$HIVE_METASTORE_PASSWORD" -D hive_db -e "SELECT 1;" &> /dev/null; then
    echo "Initializing Hive Metastore schema in MySQL..."
    $HIVE_HOME/bin/schematool -initSchema -dbType mysql -url jdbc:mysql://mysql:3306/hive_db -user $HIVE_METASTORE_USER -pass $HIVE_METASTORE_PASSWORD
fi

# Start Hive Metastore and HiveServer2
hive --service metastore &
hive --service hiveserver2 &

# Watch for changes in mounted directory and import new files into HDFS
inotifywait -m /mnt/import -e create -e moved_to --format '%w%f' |
    while read file; do
        echo "Uploading $file to HDFS"
        hdfs dfs -put "$file" /user/hadoop/
    done

# Keep container running
tail -f /dev/null