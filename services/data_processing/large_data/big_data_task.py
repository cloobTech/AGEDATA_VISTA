from celery_app import celery_app
from services.data_processing.helper.spark_session import SparkDataLoader
from services.data_processing.large_data.data_analyser import PySparkDataAnalyzer
from storage.redis_sync_client import set_task_progress_sync, set_task_failed_sync
import json
from datetime import datetime


@celery_app.task(bind=True, name="big_data_analysis")
def perform_big_data_analysis_task(self, analysis_config: dict):
    """
    Celery task for performing big data analysis with PySpark
    """
    task_id = self.request.id
    spark_loader = None

    try:
        # Initialize progress
        set_task_progress_sync(task_id, 10, "RUNNING",
                               "Initializing Spark session...")

        # Initialize Spark
        spark_loader = SparkDataLoader()
        analyzer = PySparkDataAnalyzer(spark_loader)

        set_task_progress_sync(task_id, 20, "RUNNING",
                               "Loading data from source...")

        # Load data
        df = analyzer.load_data(analysis_config['source_config'])

        set_task_progress_sync(
            task_id, 40, "RUNNING", f"Data loaded: {df.count()} rows. Starting analysis...")

        # Perform comprehensive profiling
        set_task_progress_sync(task_id, 50, "RUNNING",
                               "Performing data profiling...")
        profile_result = analyzer.comprehensive_data_profile(df)

        # Prepare results
        result = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'data_profile': profile_result,
            'analysis_config': analysis_config,
            'summary': {
                'total_rows': profile_result['total_rows'],
                'total_columns': profile_result['total_columns'],
                'data_quality_summary': {
                    col: stats['completeness_rate']
                    for col, stats in profile_result['data_quality'].items()
                }
            }
        }

        # Convert to serializable format
        serializable_result = json.loads(json.dumps(result, default=str))

        set_task_progress_sync(task_id, 100, "COMPLETED",
                               "Analysis completed successfully")

        return serializable_result

    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        set_task_failed_sync(task_id, error_msg)

        # Ensure Spark session is stopped even on failure
        if spark_loader:
            try:
                spark_loader.stop_spark()
            except:
                pass

        raise Exception(error_msg)

    finally:
        # Always stop Spark session to free resources
        if spark_loader:
            try:
                spark_loader.stop_spark()
            except:
                pass
