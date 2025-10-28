# services/visualization/plot_generator.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from typing import Dict, Any


class PlotGenerator:
    """Generate interactive plots from analysis results"""

    @staticmethod
    def create_histogram(hist_data: Dict[str, Any], title: str) -> go.Figure:
        """Create histogram from histogram data"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hist_data['bin_edges'][:-1],
            y=hist_data['histogram'],
            name=title
        ))
        fig.update_layout(
            title=title,
            xaxis_title='Value',
            yaxis_title='Frequency'
        )
        return fig

    @staticmethod
    def create_correlation_heatmap(corr_data: Dict[str, Any]) -> go.Figure:
        """Create correlation heatmap"""
        fig = go.Figure(data=go.Heatmap(
            z=corr_data['matrix'],
            x=corr_data['columns'],
            y=corr_data['columns'],
            colorscale='RdBu',
            zmid=0
        ))
        fig.update_layout(title='Correlation Matrix')
        return fig

    @staticmethod
    def create_time_series_plot(ts_data: Dict[str, Any]) -> go.Figure:
        """Create time series plot"""
        fig = go.Figure()
        for col, data in ts_data.items():
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['values'],
                name=col,
                error_y=dict(
                    type='data',
                    array=data['stddev'],
                    visible=True
                )
            ))
        fig.update_layout(title='Time Series Analysis',
                          xaxis_title='Date', yaxis_title='Value')
        return fig

    @staticmethod
    def generate_dashboard(analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate a complete dashboard from analysis results"""
        dashboard = {}
        vis_data = analysis_results.get('visualizations', {})

        # Convert plots to JSON
        if 'basic' in vis_data:
            basic_vis = vis_data['basic']
            if 'correlation_heatmap' in basic_vis:
                fig = PlotGenerator.create_correlation_heatmap(
                    basic_vis['correlation_heatmap'])
                dashboard['correlation_plot'] = fig.to_json()

            if 'histograms' in basic_vis:
                for col, hist_data in basic_vis['histograms'].items():
                    fig = PlotGenerator.create_histogram(
                        hist_data, f'Distribution of {col}')
                    dashboard[f'histogram_{col}'] = fig.to_json()
            if 'time_series' in vis_data and vis_data['time_series']:
                try:
                    # Check if we have the expected structure
                    ts_data = vis_data['time_series']
                    if isinstance(ts_data, dict) and any('dates' in series_data for series_data in ts_data.values() if isinstance(series_data, dict)):
                        fig = PlotGenerator.create_time_series_plot(ts_data)
                        dashboard['time_series_plot'] = fig.to_json()
                    else:
                        dashboard['time_series_plot'] = PlotGenerator.create_fallback_plot(
                            "Time series data not available").to_json()
                except Exception as e:
                    dashboard['time_series_plot_error'] = str(e)

            # ... handle other visualization types ...

            return dashboard

    @staticmethod
    def debug_data_structure(analysis_results: Dict[str, Any]):
        """Debug method to see the actual data structure"""
        vis_data = analysis_results.get('visualizations', {})
        print("=== DEBUG: Visualization Data Structure ===")
        print(f"Available keys: {list(vis_data.keys())}")

        if 'time_series' in vis_data:
            print("Time series data structure:")
            for key, value in vis_data['time_series'].items():
                print(f"  {key}: {type(value)}")
                if isinstance(value, dict):
                    print(f"    Subkeys: {list(value.keys())}")
                    # Print first few items for sample
                    for subkey, subvalue in list(value.items())[:2]:
                        print(f"    {subkey}: {type(subvalue)}")
                        if isinstance(subvalue, list):
                            print(
                                f"      Sample: {subvalue[:3] if len(subvalue) > 3 else subvalue}")

        print("=== END DEBUG ===")

    @staticmethod
    def create_fallback_plot(error_message: str) -> go.Figure:
        """Create a simple plot showing the error"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"Visualization Error: {error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Visualization Not Available",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
