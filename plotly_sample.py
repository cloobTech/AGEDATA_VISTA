# import plotly.express as px
# import plotly.io as pio
# import pandas as pd
# import numpy as np
# from services.data_processing.visualization import descriptive_analysis
# pio.renderers.default = "notebook"

# # Set random seed for reproducibility


# np.random.seed(42)

# # Generate a dataset with 100 rows
# df = pd.DataFrame({
#     "Employee_ID": np.arange(1, 101),
#     "Age": np.random.randint(22, 60, 100),
#     "Salary": np.random.randint(40000, 120000, 100),
#     "Department": np.random.choice(["IT", "HR", "Finance", "Marketing", "Operations"], 100),
#     "Performance_Score": np.random.randint(1, 10, 100),
#     "Work_Hours": np.random.randint(30, 50, 100),
#     "Joining_Date": pd.date_range(start="2015-01-01", periods=100, freq="M"),
#     "Gender": np.random.choice(["Male", "Female"], 100)
# })


# bar = px.bar(df, x="Department", y="Salary", title="Average Salary by Department", color="Gender", barmode="group")
# chart = px.pie(df, names="Department",   title="Employee Distribution by Gender")
# line = px.line(df, x="Salary", y="Age")
# histogram = px.histogram(df, x="Department", y="Salary", title="Age Distribution", color="Gender", barmode="group")
# scatter = px.scatter(df, x="Department", y="Salary", title="Age Distribution", color="Gender")
# heat = px.density_heatmap(df, x="Department", y="Salary", title="Age Distribution")
# # scatter.show()

# heat.show()

# # line.show()

# # bar.show()

# # chart.show()




# from groq import Groq

# client = Groq(
#     api_key=os.environ.get("GROQ_API_KEY"),
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Explain the importance of fast language models",
#         }
#     ],
#     model="llama-3.3-70b-versatile",
#     stream=False,
# )

