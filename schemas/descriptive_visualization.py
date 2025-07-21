from pydantic import BaseModel


class PieChartInputSchema(BaseModel):
    """Pie Chart Input"""
    names: str
    title: str = None
    subtitle: str = None
    hole: float = None
    color: str = None


class BarChartInputSchema(BaseModel):
    """Bar Chart Input"""
    x: str
    y: str
    title: str = None
    subtitle: str = None
    color: str = None
    barmode: str = None


class LineChartInputSchema(BaseModel):
    """Line Chart Input"""
    x: str
    y: str
    title: str = None
    subtitle: str = None


class HistogramInputSchema(BaseModel):
    """Histogram Input"""
    x: str
    y: str
    title: str = None
    subtitle: str = None
    color: str = None
    barmode: str = None


class ScatterPlotInputSchema(BaseModel):
    """Scatter Plot Input"""
    x: str
    y: str
    title: str = None
    subtitle: str = None
    color: str = None


class HeatMapSchema(BaseModel):
    """Heat Map Input"""
    x: str
    y: str
    title: str = None
    subtitle: str = None


class DescriptiveVisualizations(BaseModel):
    pie_chart_input: PieChartInputSchema = None
    line_chart_input: LineChartInputSchema = None
    scatter_plot_input: ScatterPlotInputSchema = None
    bar_chart_input: BarChartInputSchema = None
    histogram_input: HistogramInputSchema = None
    heat_map_input: HeatMapSchema = None
