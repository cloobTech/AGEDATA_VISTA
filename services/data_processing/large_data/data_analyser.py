class DataAnalyzer:
    def __init__(self, spark_loader):
        self.loader = spark_loader
        self.spark = spark_loader.spark
    
    def basic_data_profile(self, df):
        """Comprehensive data profiling"""
        from pyspark.sql.functions import col, count, when, isnan, isnull
        
        
        # Basic counts
        total_rows = df.count()
        total_columns = len(df.columns)
        
        # Missing values analysis
        missing_data = df.select([
            count(when(isnull(c), c)).alias(c + "_nulls") for c in df.columns
        ] + [
            count(when(isnan(c), c)).alias(c + "_nan") for c in df.columns
            if dict(df.dtypes)[c] in ['double', 'float']
        ])
        
        # Data types
        schema_info = [(field.name, field.dataType) for field in df.schema.fields]
        
        # Unique values per column
        unique_counts = {}
        for column in df.columns:
            unique_counts[column] = df.select(column).distinct().count()
        
        profile = {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "missing_values": missing_data.collect()[0].asDict(),
            "schema": schema_info,
            "unique_counts": unique_counts
        }
        
        return profile
    


    def statistical_analysis(self, df):
        """Generate comprehensive statistics"""
        from pyspark.sql.functions import mean, stddev, min, max, percentile_approx
        
        print("=" * 50)
        print("📈 STATISTICAL ANALYSIS")
        print("=" * 50)
        
        # Descriptive statistics for numeric columns
        numeric_cols = [col_name for col_name, dtype in df.dtypes 
                        if dtype in ['int', 'bigint', 'double', 'float', 'decimal']]
        
        if numeric_cols:
            stats_df = df.select(numeric_cols).describe()
            stats_df.show()
            
            # Additional statistics
            for col_name in numeric_cols:
                quantiles = df.approxQuantile(col_name, [0.25, 0.5, 0.75], 0.01)
                print(f"\n{col_name} Quantiles (25%, 50%, 75%): {quantiles}")
        
        return stats_df