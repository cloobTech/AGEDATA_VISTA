import json
# import asyncio
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from celery_app import celery_app
from services.data_processing.report.large_data_report import create_large_data_report
from services.data_processing.helper.spark_session import SparkDataLoader
from services.data_processing.large_data.data_analyser import PySparkDataAnalyzer
from services.data_processing.visualization.plot_generator import PlotGenerator
from storage.redis_sync_client import set_task_progress_sync, set_task_failed_sync
from celery.utils.log import get_task_logger

# Initialize module-level logger
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)


def deep_clean_json(obj):
    """Comprehensive JSON cleaning that handles keys and values recursively"""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        # Handle NaN and infinity in primitive values
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        return obj
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        cleaned_dict = {}
        for key, value in obj.items():
            # Clean the key first - convert to string if it's a Timestamp or other non-serializable
            if isinstance(key, (datetime, pd.Timestamp)):
                clean_key = key.isoformat()
            elif pd.isna(key) or (isinstance(key, float) and np.isnan(key)):
                clean_key = "NaN"
            elif not isinstance(key, (str, int, float, bool, type(None))):
                clean_key = str(key)
            else:
                clean_key = key

            # Clean the value
            cleaned_dict[clean_key] = deep_clean_json(value)
        return cleaned_dict
    elif isinstance(obj, (list, tuple)):
        return [deep_clean_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        result = float(obj)
        return None if np.isnan(result) or np.isinf(result) else result
    elif isinstance(obj, np.ndarray):
        return [deep_clean_json(item) for item in obj.tolist()]
    elif pd.isna(obj):
        return None
    elif hasattr(obj, '__dict__'):
        return deep_clean_json(obj.__dict__)
    else:
        try:
            return str(obj)
        except Exception as exc:
            logger.warning("deep_clean_json: could not convert %r to str: %s", type(obj).__name__, exc)
            return None


def validate_json_serializable(obj):
    """Validate and ensure object is JSON serializable"""
    try:
        json.dumps(obj, allow_nan=False)
        return obj
    except (TypeError, ValueError) as e:
        logger.warning(
            f"JSON serialization error: {e}, performing deep cleanup")
        # Use our comprehensive deep cleaner
        cleaned_obj = deep_clean_json(obj)
        # Final validation
        json.dumps(cleaned_obj, allow_nan=False)
        return cleaned_obj


def make_serializable(obj):
    """Recursively convert non-serializable objects to serializable formats"""
    return deep_clean_json(obj)  # Use the comprehensive cleaner


@celery_app.task(bind=True, name="big_data_analysis", time_limit=3600, soft_time_limit=3300)
def perform_big_data_analysis_task(self, analysis_config: dict, user_id: str):
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

        # Perform comprehensive analysis (this should include visualizations)
        set_task_progress_sync(task_id, 50, "RUNNING",
                               "Performing data analysis...")

        # Make sure generate_visualizations is passed to the comprehensive report
        analysis_config_with_viz = {
            **analysis_config,
            'generate_visualizations': analysis_config.get('generate_visualizations', True)
        }

        analysis_results = analyzer.generate_comprehensive_report(
            df, analysis_config_with_viz)

        logger.info(f"[{task_id}] Data analysis completed successfully")

        # Generate dashboard from the analysis results (which should now include visualizations)
        dashboard = {}
        if analysis_config.get('generate_visualizations', True):
            set_task_progress_sync(
                task_id, 80, "RUNNING", "Generating dashboard...")
            logger.info(
                f"[{task_id}] Generating dashboard from analysis results...")

            try:
                logger.info(
                    f"[{task_id}] Available visualization keys: {list(analysis_results.get('visualizations', {}).keys())}")

                dashboard = PlotGenerator.generate_dashboard(analysis_results)
                logger.info(
                    f"[{task_id}] Dashboard generated successfully with {len(dashboard)} plots")
            except Exception as viz_error:
                logger.error(
                    f"[{task_id}] Dashboard generation failed: {str(viz_error)}")
                dashboard = {
                    'error': f"Dashboard generation failed: {str(viz_error)}"}

        # Prepare final result
        result = {
            'task_id': task_id,
            **analysis_results,
            'dashboard': dashboard,
            'summary': {
                'total_rows': analysis_results['analyses']['data_profile']['total_rows'],
                'total_columns': analysis_results['analyses']['data_profile']['total_columns'],
                'visualization_count': len(dashboard),
                'analysis_types': list(analysis_results.keys())
            }
        }

        # Use comprehensive cleaning from the start
        logger.info(f"[{task_id}] Starting JSON serialization cleanup...")
        serializable_result = deep_clean_json(result)

        # Validate the result
        try:
            serializable_result = validate_json_serializable(
                serializable_result)
            logger.info(f"[{task_id}] JSON validation passed")
        except Exception as json_error:
            logger.error(f"[{task_id}] JSON validation failed: {json_error}")
            # Last resort: try to serialize with very aggressive cleanup
            try:
                serializable_result = json.loads(json.dumps(result,
                                                            default=lambda x: None if pd.isna(x) else str(x) if not isinstance(
                                                                x, (str, int, float, bool, type(None))) else x,
                                                            allow_nan=False))
            except Exception as final_error:
                logger.error(
                    f"[{task_id}] Final cleanup failed: {final_error}")
                # Create a minimal safe result
                serializable_result = {
                    'task_id': task_id,
                    'error': 'Data serialization failed',
                    'summary': {
                        'total_rows': analysis_results['analyses']['data_profile']['total_rows'],
                        'total_columns': analysis_results['analyses']['data_profile']['total_columns'],
                        'visualization_count': len(dashboard),
                        'analysis_types': ['serialization_error']
                    }
                }

        # Create clean analysis results without summary and dashboard
        analysis_results_clean = {k: v for k, v in serializable_result.items()
                                  if k not in ['summary', 'dashboard']}

        # Validate each individual component before saving
        try:
            # Validate analysis_results_clean
            analysis_results_clean = validate_json_serializable(
                analysis_results_clean)

            # Validate summary
            summary_data = validate_json_serializable(
                serializable_result['summary'])

            # Validate dashboard
            dashboard_data = serializable_result.get('dashboard', {})
            if dashboard_data and 'error' not in dashboard_data:
                dashboard_data = validate_json_serializable(dashboard_data)
            else:
                dashboard_data = {}

            # Save data in Db
            data = {
                'id': task_id,
                'analysis_results': analysis_results_clean,
                'title': analysis_config.get('title', f'Big Data Analysis Report_{datetime.now().isoformat()}'),
                'user_id': user_id,
                'data_summary': summary_data,
                'data_visualizations': dashboard_data,
                'ai_insights': ''
            }

            # Final validation
            data = validate_json_serializable(data)

            set_task_progress_sync(task_id, 90, "SAVING_TO_DATABASE",
                                   "Saving analysis report to database...")
            # async_to_sync(create_large_data_report)(data)
            if data:
                create_large_data_report(data)

            set_task_progress_sync(task_id, 100, "COMPLETED",
                                   "Analysis completed successfully")
            logger.info(
                f"[{task_id}] Analysis completed and saved successfully")
            return serializable_result

        except Exception as db_error:
            error_msg = f"[{task_id}] Database save failed: {str(db_error)}"
            logger.exception(error_msg)
            set_task_failed_sync(task_id, error_msg)
            raise

    except Exception as e:
        error_msg = f"[{task_id}] Analysis failed: {str(e)}"
        logger.exception(error_msg)
        set_task_failed_sync(task_id, error_msg)

        if spark_loader:
            try:
                spark_loader.stop_spark()
                logger.info(
                    f"[{task_id}] Spark session stopped after failure.")
            except Exception as stop_err:
                logger.warning(
                    f"[{task_id}] Failed to stop Spark session after error: {stop_err}")
        raise

    finally:
        if spark_loader:
            try:
                spark_loader.stop_spark()
                logger.info(
                    f"[{task_id}] Spark session stopped successfully (cleanup).")
            except Exception as final_err:
                logger.warning(
                    f"[{task_id}] Error stopping Spark session in finally block: {final_err}")
