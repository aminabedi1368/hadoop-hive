
# Hadoop & Hive Setup Verification Guide

This document guides you through the process of verifying that Hadoop and Hive have been installed and configured correctly in a Dockerized environment. Additionally, it includes steps to test file uploads to HDFS and run a simple MapReduce job using a Java program.

## Prerequisites

- Ensure that your Docker containers are running by using:

  ```bash
  docker-compose up -d
  ```

## 1. Checking Hadoop Installation

### Accessing the Hadoop Container

To run commands inside the Hadoop-Hive container, you need to use `docker exec`. Below are the steps to verify Hadoop.

### Check Hadoop Version

Run the following command to check that Hadoop is installed and the version is correct:

```bash
docker exec -it hadoop-hive hadoop version
```

### Check HDFS Status

You can verify the status of HDFS by running:

```bash
docker exec -it hadoop-hive hdfs dfsadmin -report
```

### List Directories in HDFS

To list directories in HDFS, use the following command:

```bash
docker exec -it hadoop-hive hdfs dfs -ls /
```

## 2. Checking Hive Installation

### Check Hive Version

Run the following command to check that Hive is installed and the version is correct:

```bash
docker exec -it hadoop-hive hive --version
```

### Access Hive Shell

To access the Hive shell, run:

```bash
docker exec -it hadoop-hive hive
```

### Create a Test Table in Hive

Once inside the Hive shell, create a test table using:

```sql
CREATE TABLE test_table (id INT, name STRING);
SHOW TABLES;
```

## 3. Testing File Upload in HDFS

To test file uploads in HDFS, you can create a test file on your local machine and copy it into the `mnt/import` directory mounted in the Docker container.

### Create a Test File

Create a simple text file:

```bash
echo "This is a test file for Hadoop" > ./mnt/import/test_file.txt
```

The file will automatically be uploaded to HDFS through the inotify service configured in the container.

### Verify File Upload in HDFS

To verify that the file has been uploaded to HDFS:

```bash
docker exec -it hadoop-hive hdfs dfs -ls /user/hadoop
```

### Check the Contents of the Uploaded File

You can also check the contents of the file by running:

```bash
docker exec -it hadoop-hive hdfs dfs -cat /user/hadoop/test_file.txt
```

## 4. Running a Java MapReduce Job on Hadoop

You can write, compile, and execute a simple Java program to test Hadoop’s MapReduce functionality.

### Java Program: WordCount

First, create a Java file `WordCount.java` in the `mnt/java` directory on your host machine:

```java
import java.io.IOException;
import java.util.StringTokenizer;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCount {

  public static class TokenizerMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();

    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
      StringTokenizer itr = new StringTokenizer(value.toString());
      while (itr.hasMoreTokens()) {
        word.set(itr.nextToken());
        context.write(word, one);
      }
    }
  }

  public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private IntWritable result = new IntWritable();

    public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable val : values) {
        sum += val.get();
      }
      result.set(sum);
      context.write(key, result);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "word count");
    job.setJarByClass(WordCount.class);
    job.setMapperClass(TokenizerMapper.class);
    job.setCombinerClass(IntSumReducer.class);
    job.setReducerClass(IntSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
```

### Compile the Java Program

Compile the Java program inside the container by running:

```bash
docker exec -it hadoop-hive javac -cp $(hadoop classpath) -d . /mnt/java/WordCount.java
docker exec -it hadoop-hive jar cf wc.jar WordCount*.class
```

### Upload an Input File to HDFS

To upload an input file to HDFS, you can use:

```bash
docker exec -it hadoop-hive hdfs dfs -put /mnt/import/test_file.txt /user/hadoop/input
```

### Run the MapReduce Job

Now, run the MapReduce job on Hadoop using the compiled Java program:

```bash
docker exec -it hadoop-hive hadoop jar wc.jar WordCount /user/hadoop/input /user/hadoop/output
```

### Check the Output of the MapReduce Job

To see the results of the job:

```bash
docker exec -it hadoop-hive hdfs dfs -cat /user/hadoop/output/part-r-00000
```

This should display the word count from the input file.

