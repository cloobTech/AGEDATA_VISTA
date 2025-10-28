# from pyspark.sql import SparkSession


# def get_spark_session():
#     """Get a spark session"""
#     spark = SparkSession.builder \
#         .appName("AgeDataProcessing") \
#         .getOrCreate()
#         # .config("spark.jars", "/Downloads/spark-excel_2.12-0.13.5.jar") \
#     return spark


from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import requests
import tempfile
import os
from urllib.parse import urlparse
from typing import Optional, Dict, Any


class SparkDataLoader:
    def __init__(self):
        self.spark = self.get_spark_session()

    def get_spark_session(self):
        """Get a spark session with optimized configurations for large data"""
        spark = SparkSession.builder \
            .appName("ClientDataProcessing") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.parquet.compression.codec", "snappy") \
            .getOrCreate()

        # Optional: Add Excel support if needed
        # .config("spark.jars", "/path/to/spark-excel_2.12-0.13.5.jar")

        return spark

    # OPTION 1: Load from URL (CSV, JSON, Parquet)
    def load_from_url(self, url: str, file_type: str = "auto", **kwargs) -> Any:
        """
        Load data from a URL

        Args:
            url: Direct download URL
            file_type: 'csv', 'json', 'parquet', or 'auto' (detect from extension)
            **kwargs: Additional options for Spark reader

        Returns:
            DataFrame: Cached DataFrame. Caller is responsible for unpersisting.

        Note:
            The returned DataFrame is cached and must be unpersisted by the caller.
        """
        safe_kwargs = kwargs or {}
        tmp_path = None

        try:
            print(
                f"⬇️ Downloading data from URL: {url}, options: {safe_kwargs}")

            # Detect file type from URL if auto
            if file_type == "auto":
                parsed_url = urlparse(url)
                file_ext = parsed_url.path.split('.')[-1].lower()
                file_type = file_ext if file_ext in [
                    'csv', 'json', 'parquet'] else 'csv'

            # Download file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp_file:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                tmp_path = tmp_file.name

            # Load based on file type
            df = self._load_from_file(tmp_path, file_type, **safe_kwargs)

            # Cache the DataFrame and force an action to materialize it
            df.cache()
            df.count()  # This forces the DataFrame to be cached and the file to be read

            return df

        except Exception as e:
            raise Exception(f"Failed to load data from URL: {str(e)}")
        finally:
            # Clean up temp file in any case
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    print(f"🧹 Cleaned up temporary file: {tmp_path}")
                except Exception as e:
                    print(
                        f"⚠️ Failed to clean up temp file {tmp_path}: {str(e)}")
        
    # OPTION 2: Load from Local File (CSV, Excel, JSON, Parquet)
    def load_from_file(self, file_path: str, file_type: str = "auto", **kwargs) -> Any:
        """
        Load data from local file system

        Args:
            file_path: Path to the file
            file_type: 'csv', 'excel', 'json', 'parquet', or 'auto'
            **kwargs: Additional options for Spark reader
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect file type if auto
        if file_type == "auto":
            file_ext = file_path.split('.')[-1].lower()
            if file_ext in ['xlsx', 'xls']:
                file_type = 'excel'
            else:
                file_type = file_ext

        return self._load_from_file(file_path, file_type, **kwargs)

    def _load_from_file(self, file_path: str, file_type: str, **kwargs) -> Any:
        """Internal method to load from file path"""
        try:
            if file_type == 'csv':
                df = self.spark.read \
                    .option("header", kwargs.get('header', 'true')) \
                    .option("inferSchema", kwargs.get('inferSchema', 'true')) \
                    .csv(file_path)

            elif file_type == 'excel':
                # Requires spark-excel package
                df = self.spark.read \
                    .format("com.crealytics.spark.excel") \
                    .option("header", kwargs.get('header', 'true')) \
                    .option("inferSchema", kwargs.get('inferSchema', 'true')) \
                    .load(file_path)

            elif file_type == 'json':
                df = self.spark.read \
                    .option("multiline", kwargs.get('multiline', 'true')) \
                    .json(file_path)

            elif file_type == 'parquet':
                df = self.spark.read.parquet(file_path)

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            return df

        except Exception as e:
            raise Exception(f"Failed to load {file_type} file: {str(e)}")

    # OPTION 3: Load from Database
    def load_from_database(self,
                           jdbc_url: str,
                           table: str,
                           username: str,
                           password: str,
                           properties: Optional[Dict] = None) -> Any:
        """
        Load data from JDBC database

        Args:
            jdbc_url: JDBC connection URL
            table: Table name or query
            username: Database username
            password: Database password
            properties: Additional connection properties
        """
        try:
            connection_properties = {
                "user": username,
                "password": password,
                "driver": "org.postgresql.Driver"  # Adjust driver as needed
            }

            if properties:
                connection_properties.update(properties)

            df = self.spark.read \
                .jdbc(url=jdbc_url, table=table, properties=connection_properties)

            print(
                f"✅ Successfully loaded {df.count()} rows from database table: {table}")
            return df

        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    # OPTION 4: Load from Cloud Storage
    def load_from_cloud_storage(self,
                                cloud_path: str,
                                file_type: str = "parquet",
                                cloud_provider: str = "s3") -> Any:
        """
        Load data from cloud storage (S3, GCS, Azure Blob)

        Args:
            cloud_path: Full path to cloud storage location
            file_type: File format
            cloud_provider: 's3', 'gcs', or 'azure'
        """
        try:
            # Configure cloud-specific settings
            if cloud_provider == "s3":
                # AWS S3 configuration (set AWS credentials in environment or Spark config)
                cloud_path = f"s3a://{cloud_path.lstrip('s3://')}"

            elif cloud_provider == "gcs":
                # Google Cloud Storage
                cloud_path = f"gs://{cloud_path.lstrip('gs://')}"
                self.spark.conf.set(
                    "spark.hadoop.google.cloud.auth.service.account.enable", "true")

            elif cloud_provider == "azure":
                # Azure Blob Storage
                cloud_path = f"wasbs://{cloud_path.lstrip('wasbs://')}"

            # Load data based on file type
            if file_type == 'parquet':
                df = self.spark.read.parquet(cloud_path)
            elif file_type == 'csv':
                df = self.spark.read.csv(
                    cloud_path, header=True, inferSchema=True)
            elif file_type == 'json':
                df = self.spark.read.json(cloud_path)
            else:
                raise ValueError(
                    f"Unsupported file type for cloud storage: {file_type}")

            print(
                f"✅ Successfully loaded {df.count()} rows from cloud storage: {cloud_path}")
            return df

        except Exception as e:
            raise Exception(f"Cloud storage load failed: {str(e)}")

    # BONUS OPTION: Load from HDFS
    def load_from_hdfs(self, hdfs_path: str, file_type: str = "parquet") -> Any:
        """
        Load data from HDFS

        Args:
            hdfs_path: HDFS path (hdfs://namenode:port/path)
            file_type: File format
        """
        try:
            full_path = f"hdfs://{hdfs_path}" if not hdfs_path.startswith(
                'hdfs://') else hdfs_path

            if file_type == 'parquet':
                df = self.spark.read.parquet(full_path)
            elif file_type == 'csv':
                df = self.spark.read.csv(
                    full_path, header=True, inferSchema=True)
            elif file_type == 'json':
                df = self.spark.read.json(full_path)
            else:
                raise ValueError(
                    f"Unsupported file type for HDFS: {file_type}")

            print(
                f"✅ Successfully loaded {df.count()} rows from HDFS: {full_path}")
            return df

        except Exception as e:
            raise Exception(f"HDFS load failed: {str(e)}")

    def show_sample(self, df, num_rows: int = 5):
        """Display sample data and schema"""
        print("\n📊 Sample Data:")
        df.show(num_rows)
        print("\n🏗️ Schema:")
        df.printSchema()
        print(f"\n📈 Total Rows: {df.count():,}")
        print(f"📊 Total Columns: {len(df.columns)}")

    def stop_spark(self):
        """Stop Spark session"""
        self.spark.stop()
