# services/data_processing/big_data_analyzer.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler
from typing import Dict, List, Any
from datetime import datetime
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, mean, count
import pandas as pd


class PySparkDataAnalyzer:
    def __init__(self, spark_loader):
        self.loader = spark_loader
        self.spark = spark_loader.spark

    def load_data(self, source_config: Dict[str, Any]) -> DataFrame:
        """Load data using the SparkDataLoader based on source configuration"""
        source_type = source_config.get('type', 'file')

        try:
            if source_type == 'file':
                return self.loader.load_from_file(
                    file_path=source_config['path'],
                    file_type=source_config.get('format', 'auto'),
                    **source_config.get('options', {})
                )

            elif source_type == 'url':

                return self.loader.load_from_url(
                    url=source_config['url'],
                    file_type=source_config.get('format', 'auto'),
                    **source_config.get('options', {})
                )

            elif source_type == 'database':
                return self.loader.load_from_database(
                    jdbc_url=source_config['url'],
                    table=source_config['table'],
                    username=source_config.get('username', ''),
                    password=source_config.get('password', ''),
                    properties=source_config.get('properties', {})
                )

            elif source_type == 'cloud':
                return self.loader.load_from_cloud_storage(
                    cloud_path=source_config['path'],
                    file_type=source_config.get('format', 'parquet'),
                    cloud_provider=source_config.get('provider', 's3')
                )

            elif source_type == 'hdfs':
                return self.loader.load_from_hdfs(
                    hdfs_path=source_config['path'],
                    file_type=source_config.get('format', 'parquet')
                )

            else:
                raise ValueError(f"Unsupported source type: {source_type}")

        except Exception as e:
            raise Exception(
                f"Failed to load data from {source_type}: {str(e)}")

    def comprehensive_data_profile(self, df: DataFrame) -> Dict[str, Any]:
        """Comprehensive data profiling with advanced metrics"""
        from pyspark.sql.functions import col, count, when, isnan, isnull, mean, stddev, min, max, approx_count_distinct

        profile = {}

        # Basic counts
        profile['total_rows'] = df.count()
        profile['total_columns'] = len(df.columns)
        profile['column_names'] = df.columns

        # Schema information
        profile['schema'] = [
            {
                'column_name': field.name,
                'data_type': str(field.dataType),
                'nullable': field.nullable
            }
            for field in df.schema.fields
        ]

        # Missing values analysis
        missing_expr = []
        for column in df.columns:
            missing_expr.append(
                count(when(isnull(col(column)), column)).alias(f"{column}_nulls"))
            if dict(df.dtypes)[column] in ['double', 'float']:
                missing_expr.append(
                    count(when(isnan(col(column)), column)).alias(f"{column}_nan"))

        missing_data = df.select(missing_expr).collect()[0].asDict()
        profile['missing_values'] = missing_data

        # Data quality metrics
        completeness = {}
        for column in df.columns:
            null_count = missing_data.get(f"{column}_nulls", 0)
            nan_count = missing_data.get(f"{column}_nan", 0)
            total_missing = null_count + nan_count
            completeness[column] = {
                'missing_count': total_missing,
                'completeness_rate': 1 - (total_missing / profile['total_rows']),
                'null_count': null_count,
                'nan_count': nan_count
            }
        profile['data_quality'] = completeness

        # Unique values and cardinality
        unique_counts = {}
        for column in df.columns:
            unique_count = df.select(approx_count_distinct(
                col(column)).alias('distinct')).collect()[0]['distinct']
            unique_counts[column] = {
                'distinct_count': unique_count,
                'cardinality_ratio': unique_count / profile['total_rows'] if profile['total_rows'] > 0 else 0
            }
        profile['unique_analysis'] = unique_counts

        # Basic statistics for numeric columns
        numeric_cols = [col_name for col_name, dtype in df.dtypes
                        if dtype in ['int', 'bigint', 'double', 'float', 'decimal', 'long']]

        if numeric_cols:
            stats_df = df.select([col(c) for c in numeric_cols]).describe()
            stats_data = stats_df.collect()

            numeric_stats = {}
            for col_name in numeric_cols:
                numeric_stats[col_name] = {
                    'count': float(stats_data[0][col_name]),
                    'mean': float(stats_data[1][col_name]),
                    'stddev': float(stats_data[2][col_name]),
                    'min': float(stats_data[3][col_name]),
                    'max': float(stats_data[4][col_name])
                }
            profile['numeric_statistics'] = numeric_stats

        return profile

    # Add other analysis methods (statistical_analysis, time_series_analysis, etc.)
    # ... [Include the other methods from your previous PySparkDataAnalyzer implementation]

    def advanced_statistical_analysis(self, df: DataFrame, numeric_columns: List[str] | None = None) -> Dict[str, Any]:
        """Advanced statistical analysis with correlations and distributions"""
        if numeric_columns is None:
            numeric_columns = [col_name for col_name, dtype in df.dtypes
                               if dtype in ['int', 'bigint', 'double', 'float', 'decimal', 'long']]

        analysis = {}

        if numeric_columns:
            # Correlation analysis
            assembler = VectorAssembler(
                inputCols=numeric_columns, outputCol="features")
            df_vector = assembler.transform(df).select("features")

            # Pearson correlation
            pearson_matrix = Correlation.corr(
                df_vector, "features").collect()[0][0].toArray()
            analysis['correlation_matrix'] = {
                'columns': numeric_columns,
                'matrix': pearson_matrix.tolist()
            }

            # Quantile analysis
            quantiles = {}
            for col_name in numeric_columns:
                quantile_values = df.approxQuantile(
                    col_name, [0.05, 0.25, 0.5, 0.75, 0.95], 0.01)
                quantiles[col_name] = {
                    'p5': quantile_values[0],
                    'p25': quantile_values[1],
                    'median': quantile_values[2],
                    'p75': quantile_values[3],
                    'p95': quantile_values[4]
                }
            analysis['quantiles'] = quantiles

            # Skewness and kurtosis approximation
            for col_name in numeric_columns:
                # Basic skewness calculation (simplified)
                mean_val = df.select(mean(col_name)).collect()[0][0]
                std_val = df.select(stddev(col_name)).collect()[0][0]
                analysis[col_name] = {
                    'skewness_approx': self._calculate_skewness(df, col_name, mean_val, std_val),
                    'coefficient_of_variation': std_val / mean_val if mean_val != 0 else float('inf')
                }

        return analysis

    def _calculate_skewness(self, df: DataFrame, column: str, mean_val: float, std_val: float) -> float:
        """Calculate approximate skewness"""
        if std_val == 0:
            return 0.0

        # Using moment-based skewness approximation
        result = df.select(
            mean(pow((col(column) - mean_val) / std_val, 3)).alias('skewness')
        ).collect()[0]['skewness']

        return result if result is not None else 0.0

    def time_series_analysis(self, df: DataFrame, time_col: str, value_col: str,
                             period: int | None = None,
                             model: str = 'additive',
                             frequency: str = 'D') -> Dict[str, Any]:
        """Generic time series decomposition for any data"""
        # from pyspark.sql.window import Window
        # from pyspark.sql.functions import row_number, mean, count
        # import pandas as pd

        result = {
            "model": model,
            "frequency": frequency,
            "period": period,
            "components": {},
            "stats": {},
            "metadata": {},
            "warnings": []
        }

        try:
            # Validate columns exist
            if time_col not in df.columns:
                raise ValueError(f"Time column '{time_col}' not found")
            if value_col not in df.columns:
                raise ValueError(f"Value column '{value_col}' not found")

            # Convert time column to timestamp (handles various formats)
            df_processed = df.withColumn(time_col, to_timestamp(col(time_col)))

            # Remove rows with null timestamps or values
            df_processed = df_processed.filter(
                col(time_col).isNotNull() & col(value_col).isNotNull()
            )

            # Aggregate by time to handle duplicates
            df_aggregated = df_processed.groupBy(time_col).agg(
                mean(value_col).alias('value'),
                count(value_col).alias('record_count')
            )

            # Sort by time
            window_spec = Window.orderBy(time_col)
            df_aggregated = df_aggregated.withColumn(
                "row_index", row_number().over(window_spec))

            # Convert to pandas
            pandas_df = df_aggregated.select(
                time_col, 'value').orderBy(time_col).toPandas()

            if pandas_df.empty:
                raise ValueError("No data available after processing")

            # Convert to datetime
            pandas_df[time_col] = pd.to_datetime(
                pandas_df[time_col], errors='coerce', utc=True)
            pandas_df = pandas_df.dropna(subset=[time_col])

            if pandas_df.empty:
                raise ValueError("No valid dates after conversion")

            pandas_df = pandas_df.set_index(time_col)

            # Handle duplicates by taking mean
            if pandas_df.index.duplicated().any():
                result['warnings'].append(
                    "Duplicate timestamps found - aggregating by mean")
                pandas_df = pandas_df.groupby(pandas_df.index).mean()

            # Set frequency
            try:
                pandas_df = pandas_df.asfreq(frequency).fillna(method='ffill')
            except Exception as e:
                result['warnings'].append(
                    f"Could not set frequency {frequency}: {str(e)}")
                # Continue without frequency setting

            # Auto-detect period if not provided
            if period is None:
                if frequency in ['D', 'B']:  # Daily or business days
                    period = 7  # Weekly seasonality
                elif frequency in ['W']:
                    period = 4  # Monthly seasonality
                elif frequency in ['M', 'BM', 'MS']:
                    period = 12  # Yearly seasonality
                else:
                    period = min(24, len(pandas_df) // 2)

            result['period'] = period
            result['metadata'] = {
                'original_rows': df.count(),
                'processed_rows': len(pandas_df),
                'date_range': {
                    'start': str(pandas_df.index.min()),
                    'end': str(pandas_df.index.max())
                },
                'frequency_set': frequency
            }

            # Check if we have enough data
            if len(pandas_df) < period * 2:
                raise ValueError(
                    f"Not enough data points ({len(pandas_df)}) for period {period}")

            # Perform decomposition
            from statsmodels.tsa.seasonal import seasonal_decompose

            decomposition = seasonal_decompose(
                pandas_df['value'].dropna(),
                model=model,
                period=period,
                extrapolate_trend=0
            )

            result['components'] = {
                "observed": decomposition.observed.to_dict(),
                "trend": decomposition.trend.to_dict(),
                "seasonal": decomposition.seasonal.to_dict(),
                "resid": decomposition.resid.to_dict(),
            }

            result['stats'] = {
                "residual_mean": float(decomposition.resid.mean()),
                "residual_std": float(decomposition.resid.std()),
                "seasonal_amplitude": float(
                    decomposition.seasonal.max() - decomposition.seasonal.min()
                ),
                "trend_strength": float(
                    1 - (decomposition.resid.var() /
                         decomposition.observed.var())
                ) if decomposition.observed.var() > 0 else 0
            }

        except ImportError:
            result['warnings'].append(
                "statsmodels not available for decomposition")
        except Exception as e:
            result['error'] = str(e)
        return result

    def anomaly_detection(self, df: DataFrame, numeric_columns: List[str],
                          method: str = 'iqr', threshold: float = 1.5) -> Dict[str, Any]:
        """Detect anomalies using various methods"""
        anomalies = {}

        for column in numeric_columns:
            if method == 'iqr':
                # IQR method
                quantiles = df.approxQuantile(column, [0.25, 0.75], 0.01)
                q1, q3 = quantiles[0], quantiles[1]
                iqr = q3 - q1
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr

                anomaly_count = df.filter(
                    (col(column) < lower_bound) | (col(column) > upper_bound)
                ).count()

                anomalies[column] = {
                    'method': 'iqr',
                    'anomaly_count': anomaly_count,
                    'anomaly_percentage': (anomaly_count / df.count()) * 100,
                    'bounds': {'lower': lower_bound, 'upper': upper_bound}
                }

            elif method == 'zscore':
                # Z-score method
                mean_val = df.select(mean(column)).collect()[0][0]
                std_val = df.select(stddev(column)).collect()[0][0]

                if std_val > 0:
                    anomaly_count = df.filter(
                        abs((col(column) - mean_val) / std_val) > threshold
                    ).count()

                    anomalies[column] = {
                        'method': 'zscore',
                        'anomaly_count': anomaly_count,
                        'anomaly_percentage': (anomaly_count / df.count()) * 100,
                        'threshold_zscore': threshold
                    }

        return anomalies

    def pattern_analysis(self, df: DataFrame, group_columns: List[str],
                         value_columns: List[str]) -> Dict[str, Any]:
        """Analyze patterns across different groups"""
        patterns = {}

        for value_col in value_columns:
            # Group-level statistics
            group_stats = df.groupBy(group_columns).agg(
                mean(value_col).alias('mean'),
                stddev(value_col).alias('stddev'),
                count(value_col).alias('count'),
                min(value_col).alias('min'),
                max(value_col).alias('max')
            )

            patterns[value_col] = {
                'group_statistics': group_stats.collect(),
                'total_groups': group_stats.count(),
                'value_distribution': df.select(
                    mean(value_col).alias('global_mean'),
                    stddev(value_col).alias('global_stddev')
                ).collect()[0].asDict()
            }

        return patterns

    def data_drift_analysis(self, df_reference: DataFrame, df_current: DataFrame,
                            numeric_columns: List[str]) -> Dict[str, Any]:
        """Analyze data drift between reference and current datasets"""
        drift_analysis = {}

        for column in numeric_columns:
            # Compare distributions using basic statistics
            ref_stats = df_reference.select(
                mean(column).alias('ref_mean'),
                stddev(column).alias('ref_stddev'),
                count(column).alias('ref_count')
            ).collect()[0]

            curr_stats = df_current.select(
                mean(column).alias('curr_mean'),
                stddev(column).alias('curr_stddev'),
                count(column).alias('curr_count')
            ).collect()[0]

            # Calculate drift metrics
            mean_drift = abs(ref_stats['ref_mean'] - curr_stats['curr_mean']) / \
                ref_stats['ref_mean'] if ref_stats['ref_mean'] != 0 else 0
            std_drift = abs(ref_stats['ref_stddev'] - curr_stats['curr_stddev']) / \
                ref_stats['ref_stddev'] if ref_stats['ref_stddev'] != 0 else 0

            drift_analysis[column] = {
                'mean_drift': mean_drift,
                'stddev_drift': std_drift,
                'reference_stats': {
                    'mean': ref_stats['ref_mean'],
                    'stddev': ref_stats['ref_stddev'],
                    'count': ref_stats['ref_count']
                },
                'current_stats': {
                    'mean': curr_stats['curr_mean'],
                    'stddev': curr_stats['curr_stddev'],
                    'count': curr_stats['curr_count']
                }
            }

        return drift_analysis

    def create_analysis_config(self, df: DataFrame, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a generic analysis configuration based on data schema"""

        # Auto-detect column types
        numeric_cols = [col for col, dtype in df.dtypes
                        if dtype in ['int', 'bigint', 'double', 'float', 'decimal', 'long']]

        string_cols = [col for col, dtype in df.dtypes
                       if dtype in ['string', 'varchar']]

        timestamp_cols = [col for col, dtype in df.dtypes
                          if any(keyword in dtype.lower() for keyword in ['timestamp', 'date', 'time'])]

        # Build auto-detected config
        auto_config = {
            'detected_schema': {
                'numeric_columns': numeric_cols,
                'string_columns': string_cols,
                'timestamp_columns': timestamp_cols,
                'total_columns': len(df.columns),
                'sample_size': df.count()
            },
            'analysis_options': {
                'data_profiling': True,
                'statistical_analysis': len(numeric_cols) > 0,
                'time_series_analysis': len(timestamp_cols) > 0,
                'anomaly_detection': len(numeric_cols) > 0,
                'visualizations': True
            }
        }

        # Merge with user config (user config takes precedence)
        config = {**auto_config, **user_config}

        # Auto-select time column if not specified
        if not config.get('time_column') and timestamp_cols:
            # Use first timestamp column
            config['time_column'] = timestamp_cols[0]

        # Auto-select value columns if not specified
        if not config.get('value_columns') and numeric_cols:
            # Use first 3 numeric columns
            config['value_columns'] = numeric_cols[:3]

        return config

    def generate_comprehensive_report(self, df: DataFrame, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis report for any data type"""

        # Create generic analysis configuration
        analysis_config = self.create_analysis_config(df, user_config)

        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_config': analysis_config,
            'data_summary': {},
            'analyses': {},
            'visualizations': {},
            'warnings': []
        }

        try:
            # Basic data profiling (always run)
            report['analyses']['data_profile'] = self.comprehensive_data_profile(df)
            report['data_summary']['basic_stats'] = {
                'total_rows': report['analyses']['data_profile']['total_rows'],
                'total_columns': report['analyses']['data_profile']['total_columns'],
                'column_types': {col: dtype for col, dtype in df.dtypes}
            }

            # Determine column types for visualizations
            numeric_columns = analysis_config['detected_schema']['numeric_columns']
            string_columns = analysis_config['detected_schema']['string_columns']
            timestamp_columns = analysis_config['detected_schema']['timestamp_columns']

            # Statistical analysis for numeric data
            if analysis_config['analysis_options']['statistical_analysis'] and numeric_columns:
                report['analyses']['statistical_analysis'] = self.advanced_statistical_analysis(df, numeric_columns)

            # Time series analysis if time column available
            if (analysis_config['analysis_options']['time_series_analysis'] and 
                analysis_config.get('time_column') and 
                analysis_config.get('value_columns')):
                
                time_col = analysis_config['time_column']
                for value_col in analysis_config['value_columns'][:2]:  # Limit to 2 for performance
                    try:
                        ts_result = self.time_series_analysis(
                            df, time_col, value_col,
                            period=analysis_config.get('period'),
                            frequency=analysis_config.get('frequency', 'D')
                        )
                        if 'time_series_analysis' not in report['analyses']:
                            report['analyses']['time_series_analysis'] = {}
                        report['analyses']['time_series_analysis'][value_col] = ts_result
                    except Exception as e:
                        report['warnings'].append(f"Time series analysis failed for {value_col}: {str(e)}")

            # Generate visualizations
            if analysis_config['analysis_options']['visualizations']:
                # Basic visualizations for numeric data
                if numeric_columns:
                    try:
                        report['visualizations']['basic'] = self.generate_basic_visualizations(df, numeric_columns)
                    except Exception as e:
                        report['warnings'].append(f"Basic visualizations failed: {str(e)}")
                        report['visualizations']['basic'] = {"error": str(e)}

                # Time series visualizations
                if (analysis_config.get('time_column') and analysis_config.get('value_columns')):
                    try:
                        report['visualizations']['time_series'] = self.generate_time_series_visualizations(
                            df, 
                            analysis_config['time_column'],
                            analysis_config['value_columns'],
                            aggregation_method=analysis_config.get('aggregation_method', 'mean')
                        )
                    except Exception as e:
                        report['warnings'].append(f"Time series visualizations failed: {str(e)}")
                        report['visualizations']['time_series'] = {"error": str(e)}

            # Anomaly detection
            if (analysis_config['analysis_options']['anomaly_detection'] and numeric_columns):
                try:
                    report['analyses']['anomaly_detection'] = self.anomaly_detection(
                        df, 
                        numeric_columns,
                        method=analysis_config.get('anomaly_method', 'iqr')
                    )
                except Exception as e:
                    report['warnings'].append(f"Anomaly detection failed: {str(e)}")
                    report['analyses']['anomaly_detection'] = {"error": str(e)}

            return report

        except Exception as e:
            report['error'] = str(e)
            return report
        

    def generate_basic_visualizations(self, df: DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Generate basic visualization data and configurations"""
        import pandas as pd
        import numpy as np

        visualizations = {}

        # Sample data for plotting (limit to avoid memory issues)
        sample_df = df.sample(False, 0.1) if df.count() > 10000 else df
        pandas_sample = sample_df.limit(1000).toPandas()

        # Histograms for numeric columns
        histograms = {}
        for col in numeric_columns:
            if col in pandas_sample.columns:
                hist_data = pandas_sample[col].dropna()
                if len(hist_data) > 0:
                    hist, bin_edges = np.histogram(hist_data, bins=20)
                    histograms[col] = {
                        'histogram': hist.tolist(),
                        'bin_edges': bin_edges.tolist(),
                        'type': 'histogram'
                    }
        visualizations['histograms'] = histograms

        # Correlation heatmap data
        if len(numeric_columns) > 1:
            numeric_sample = sample_df.select(numeric_columns).toPandas()
            correlation_matrix = numeric_sample.corr()
            visualizations['correlation_heatmap'] = {
                'matrix': correlation_matrix.values.tolist(),
                'columns': numeric_columns,
                'type': 'heatmap'
            }

        # Box plot data
        box_plots = {}
        for col in numeric_columns:
            if col in pandas_sample.columns:
                box_data = pandas_sample[col].dropna()
                if len(box_data) > 0:
                    box_plots[col] = {
                        'q1': float(np.percentile(box_data, 25)),
                        'q2': float(np.percentile(box_data, 50)),
                        'q3': float(np.percentile(box_data, 75)),
                        'whisker_low': float(np.percentile(box_data, 5)),
                        'whisker_high': float(np.percentile(box_data, 95)),
                        'outliers': box_data[(box_data < np.percentile(box_data, 5)) |
                                             (box_data > np.percentile(box_data, 95))].tolist(),
                        'type': 'boxplot'
                    }
        visualizations['box_plots'] = box_plots

        return visualizations

    def generate_advanced_visualizations(self, df: DataFrame,
                                         categorical_columns: List[str],
                                         numeric_columns: List[str]) -> Dict[str, Any]:
        """Generate advanced visualizations including categorical relationships"""
        import pandas as pd

        visualizations = {}
        sample_df = df.sample(False, 0.1) if df.count() > 10000 else df
        pandas_sample = sample_df.limit(2000).toPandas()

        # Bar charts for categorical columns
        bar_charts = {}
        for col in categorical_columns:
            if col in pandas_sample.columns:
                value_counts = pandas_sample[col].value_counts().head(
                    10)  # Top 10 categories
                bar_charts[col] = {
                    'categories': value_counts.index.tolist(),
                    'counts': value_counts.values.tolist(),
                    'type': 'barchart'
                }
        visualizations['bar_charts'] = bar_charts

        # Scatter plot matrix for numeric columns (limited to 4 columns for performance)
        if len(numeric_columns) >= 2:
            # Limit to first 4 numeric columns
            scatter_columns = numeric_columns[:4]
            scatter_data = pandas_sample[scatter_columns].dropna()

            scatter_matrix = {}
            for i, col1 in enumerate(scatter_columns):
                for j, col2 in enumerate(scatter_columns):
                    if i < j:  # Avoid duplicates and self-comparisons
                        key = f"{col1}_vs_{col2}"
                        scatter_matrix[key] = {
                            'x': scatter_data[col1].tolist(),
                            'y': scatter_data[col2].tolist(),
                            'x_label': col1,
                            'y_label': col2,
                            'type': 'scatter'
                        }
            visualizations['scatter_matrix'] = scatter_matrix

        return visualizations

    def generate_time_series_visualizations(self, df: DataFrame,
                                            time_col: str,
                                            value_cols: List[str],
                                            aggregation_method: str = 'mean') -> Dict[str, Any]:
        """Generate time series visualizations for any data type"""
        from pyspark.sql.functions import col, to_date, mean, stddev, count, sum as spark_sum, min, max
        import pandas as pd

        visualizations = {'time_series': {}, 'warnings': [], 'metadata': {}}

        try:
            # Validate inputs
            if time_col not in df.columns:
                raise ValueError(
                    f"Time column '{time_col}' not found in DataFrame")

            available_value_cols = [
                col for col in value_cols if col in df.columns]
            if not available_value_cols:
                raise ValueError(
                    f"No value columns found in DataFrame. Available columns: {df.columns}")

            # Convert to date (handles both timestamp and date strings)
            date_df = df.withColumn("analysis_date", to_date(col(time_col)))

            # Filter out null dates
            date_df = date_df.filter(col("analysis_date").isNotNull())

            # Store metadata about the data
            visualizations['metadata'] = {
                'time_column': time_col,
                'value_columns_used': available_value_cols,
                'aggregation_method': aggregation_method,
                'total_records': df.count(),
                'date_range': {
                    'min': date_df.agg(min("analysis_date")).collect()[0][0],
                    'max': date_df.agg(max("analysis_date")).collect()[0][0]
                }
            }

            time_series_data = {}
            for value_col in available_value_cols[:5]:  # Limit for performance
                try:
                    # Choose aggregation method based on data type and user preference
                    if aggregation_method == 'sum':
                        agg_expr = spark_sum(value_col).alias('value')
                    elif aggregation_method == 'count':
                        agg_expr = count(value_col).alias('value')
                    elif aggregation_method == 'min':
                        agg_expr = min(value_col).alias('value')
                    elif aggregation_method == 'max':
                        agg_expr = max(value_col).alias('value')
                    else:  # default to mean
                        agg_expr = mean(value_col).alias('value')

                    # Daily aggregates
                    daily_agg = date_df.groupBy("analysis_date").agg(
                        agg_expr,
                        count(value_col).alias('record_count')
                    ).orderBy("analysis_date")

                    # Convert to pandas (limit for performance)
                    sample_size = min(1000, daily_agg.count())
                    daily_pandas = daily_agg.limit(sample_size).toPandas()

                    if daily_pandas.empty:
                        visualizations['warnings'].append(
                            f"No data for {value_col} after aggregation")
                        continue

                    # Convert date column to datetime
                    daily_pandas['analysis_date'] = pd.to_datetime(
                        daily_pandas['analysis_date'],
                        errors='coerce',
                        utc=True
                    )

                    # Remove invalid dates
                    daily_pandas = daily_pandas.dropna(
                        subset=['analysis_date'])

                    if daily_pandas.empty:
                        visualizations['warnings'].append(
                            f"All dates invalid for {value_col}")
                        continue

                    # Sort by date
                    daily_pandas = daily_pandas.sort_values('analysis_date')

                    # Prepare the data
                    ts_data = {
                        'dates': daily_pandas['analysis_date'].dt.strftime('%Y-%m-%d').tolist(),
                        # Handle nulls
                        'values': daily_pandas['value'].fillna(0).tolist(),
                        'record_counts': daily_pandas['record_count'].tolist(),
                        'aggregation_method': aggregation_method,
                        'data_type': 'timeseries'
                    }

                    time_series_data[value_col] = ts_data

                except Exception as e:
                    error_msg = f"Failed to process {value_col}: {str(e)}"
                    visualizations['warnings'].append(error_msg)

        except Exception as e:
            error_msg = f"Time series visualization generation failed: {str(e)}"
            visualizations['warnings'].append(error_msg)

        visualizations['time_series'] = time_series_data
        return visualizations
