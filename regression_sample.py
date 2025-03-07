import csv

#Define the header and initial data
header = ["feature1", "feature2", "feature3", "target"]
initial_data = [
    [1.0, 2.0, 3.0, 10.0],
    [2.0, 3.0, 4.0, 15.0],
    [3.0, 4.0, 5.0, 20.0],
    [4.0, 5.0, 6.0, 25.0],
    [5.0, 6.0, 7.0, 30.0],
    [6.0, 7.0, 8.0, 35.0],
    [7.0, 8.0, 9.0, 40.0],
    [8.0, 9.0, 10.0, 45.0],
    [9.0, 10.0, 11.0, 50.0],
    [10.0, 11.0, 12.0, 55.0]
]

# Generate additional rows
data = []
for i in range(100):
    for row in initial_data:
        new_row = [value + i * 10 for value in row]
        data.append(new_row)

# Write the data to a CSV file
with open("regression_sample_large.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(data)
