## Big Data Analysis Endpoints

### 1. **Get Big Data Analysis Result**

#### Endpoint

`GET /api/v1/analysis/big-data/{task_id}/result`

#### Description

Retrieve the result of a completed big data analysis task by its `task_id`.

#### Request

##### URL Parameters

| Name      | Type   | Required | Description                     |
| --------- | ------ | -------- | ------------------------------- |
| `task_id` | string | Yes      | The unique ID of the analysis task. |

##### Headers

| Name            | Type   | Required | Description                           |
| --------------- | ------ | -------- | ------------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |

#### Response

##### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the result of the analysis.

```json
{
	"status": "success",
	"message": "Large data report retrieved successfully",
	"data": {
		"user_id": "8810df9b-e755-42c6-ac8b-31414b52b203",
		"data_summary": {
			"total_rows": 161568,
			"total_columns": 5,
			"visualization_count": 5,
			"analysis_types": [
				"timestamp",
				"analysis_config",
				"data_summary",
				"analyses",
				"visualizations",
				"warnings"
			]
		},
		"analysis_results": {
			"task_id": "d06fd59c-5a06-4747-8397-4d9fe74c25dc",
			"timestamp": "2025-10-28T16:01:46.834114",
			"analysis_config": {
				"detected_schema": {
					"numeric_columns": [
						"Confirmed",
						"Recovered",
						"Deaths"
					],
					"string_columns": [
						"Country"
					],
					"timestamp_columns": [
						"Date"
					],
					"total_columns": 5,
					"sample_size": 161568
				},
				"analysis_options": {
					"data_profiling": true,
					"statistical_analysis": true,
					"time_series_analysis": true,
					"anomaly_detection": true,
					"visualizations": true
				},
				"title": "Big Data Analysis",
				"source_config": {
					"type": "url",
					"path": null,
					"url": "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv",
					"format": "csv",
					"table": null,
					"table_name": null,
					"bootstrap_servers": null,
					"topic": null,
					"username": null,
					"password": null,
					"provider": null,
					"options": {},
					"properties": null
				},
				"numeric_columns": null,
				"time_column": "Date",
				"value_column": null,
				"group_columns": null,
				"perform_anomaly_detection": false,
				"anomaly_method": "iqr",
				"period": null,
				"model": "additive",
				"generate_visualizations": true,
				"value_columns": [
					"Confirmed",
					"Recovered",
					"Deaths"
				]
			},
			"data_summary": {
				"basic_stats": {
					"total_rows": 161568,
					"total_columns": 5,
					"column_types": {
						"Date": "date",
						"Country": "string",
						"Confirmed": "int",
						"Recovered": "int",
						"Deaths": "int"
					}
				}
			},
			"analyses": {
				"data_profile": {
					"total_rows": 161568,
					"total_columns": 5,
					"column_names": [
						"Date",
						"Country",
						"Confirmed",
						"Recovered",
						"Deaths"
					],
					"schema": [
						{
							"column_name": "Date",
							"data_type": "DateType()",
							"nullable": true
						},
						{
							"column_name": "Country",
							"data_type": "StringType()",
							"nullable": true
						},
						{
							"column_name": "Confirmed",
							"data_type": "IntegerType()",
							"nullable": true
						},
						{
							"column_name": "Recovered",
							"data_type": "IntegerType()",
							"nullable": true
						},
						{
							"column_name": "Deaths",
							"data_type": "IntegerType()",
							"nullable": true
						}
					],
					"missing_values": {
						"Date_nulls": 0,
						"Country_nulls": 0,
						"Confirmed_nulls": 0,
						"Recovered_nulls": 0,
						"Deaths_nulls": 0
					},
					"data_quality": {
						"Date": {
							"missing_count": 0,
							"completeness_rate": 1.0,
							"null_count": 0,
							"nan_count": 0
						},
						"Country": {
							"missing_count": 0,
							"completeness_rate": 1.0,
							"null_count": 0,
							"nan_count": 0
						},
						"Confirmed": {
							"missing_count": 0,
							"completeness_rate": 1.0,
							"null_count": 0,
							"nan_count": 0
						},
						"Recovered": {
							"missing_count": 0,
							"completeness_rate": 1.0,
							"null_count": 0,
							"nan_count": 0
						},
						"Deaths": {
							"missing_count": 0,
							"completeness_rate": 1.0,
							"null_count": 0,
							"nan_count": 0
						}
					},
					"unique_analysis": {
						"Date": {
							"distinct_count": 821,
							"cardinality_ratio": 0.005081451772628243
						},
						"Country": {
							"distinct_count": 190,
							"cardinality_ratio": 0.0011759754406813231
						},
						"Confirmed": {
							"distinct_count": 92405,
							"cardinality_ratio": 0.5719263715587245
						},
						"Recovered": {
							"distinct_count": 42062,
							"cardinality_ratio": 0.26033620518914635
						},
						"Deaths": {
							"distinct_count": 29056,
							"cardinality_ratio": 0.17983759160229748
						}
					},
					"numeric_statistics": {
						"Confirmed": {
							"count": 161568.0,
							"mean": 736156.9340092097,
							"stddev": 3578884.2226683735,
							"min": 0.0,
							"max": 80625120.0
						},
						"Recovered": {
							"count": 161568.0,
							"mean": 145396.71189220637,
							"stddev": 974827.5085659551,
							"min": 0.0,
							"max": 30974748.0
						},
						"Deaths": {
							"count": 161568.0,
							"mean": 13999.43608882947,
							"stddev": 59113.58127111721,
							"min": 0.0,
							"max": 988609.0
						}
					}
				},
				"statistical_analysis": {
					"correlation_matrix": {
						"columns": [
							"Confirmed",
							"Recovered",
							"Deaths"
						],
						"matrix": [
							[
								1.0,
								0.2777966410156644,
								0.9149927237245798
							],
							[
								0.2777966410156644,
								1.0,
								0.3181600409759226
							],
							[
								0.9149927237245798,
								0.3181600409759226,
								1.0
							]
						]
					},
					"quantiles": {
						"Confirmed": {
							"p5": 0.0,
							"p25": 1076.0,
							"median": 23697.0,
							"p75": 254273.0,
							"p95": 2652947.0
						},
						"Recovered": {
							"p5": 0.0,
							"p25": 0.0,
							"median": 91.0,
							"p75": 16618.0,
							"p95": 396219.0
						},
						"Deaths": {
							"p5": 0.0,
							"p25": 14.0,
							"median": 342.0,
							"p75": 4482.0,
							"p95": 52683.0
						}
					},
					"Confirmed": {
						"skewness_approx": 11.701412287862217,
						"coefficient_of_variation": 4.861577820339596
					},
					"Recovered": {
						"skewness_approx": 18.155841584240854,
						"coefficient_of_variation": 6.704604910795155
					},
					"Deaths": {
						"skewness_approx": 8.662549394953375,
						"coefficient_of_variation": 4.222568744628616
					}
				},
				"time_series_analysis": {
					"Confirmed": {
						"model": "additive",
						"frequency": "D",
						"period": 7,
						"components": {
							"observed": {
							
								"2022-04-16T00:00:00+00:00": 2546239.6919191917,
                                ...
							},
							"trend": {
							
								"2022-04-13T00:00:00+00:00": 2534030.6298701297,
							...
							},
							"seasonal": {
								"2020-01-22T00:00:00+00:00": -65.39660709225231,
								...
								
						
							},
							"resid": {
								"2020-01-25T00:00:00+00:00": -401.9812726908141,
                                ...
								
							}
						},
						"stats": {
							"residual_mean": -10.020868152768394,
							"residual_std": 684.298964812604,
							"seasonal_amplitude": 1254.9259704563324,
							"trend_strength": 0.999999028572579
						},
						"metadata": {
							"original_rows": 161568,
							"processed_rows": 816,
							"date_range": {
								"start": "2020-01-22 00:00:00+00:00",
								"end": "2022-04-16 00:00:00+00:00"
							},
							"frequency_set": "D"
						},
						"warnings": []
					},
					"Recovered": {
						"model": "additive",
						"frequency": "D",
						"period": 7,
						"components": {
							"observed": {
								"2020-01-22T00:00:00+00:00": 0.15151515151515152,
								...
							},
							"trend": {
						
								"2020-01-25T00:00:00+00:00": 0.26839826839826836,
							 ...
							},
							"seasonal": {
								"2020-01-22T00:00:00+00:00": 2425.6987063132024,
                                    ...

					
							},
							"resid": {
								"2020-01-25T00:00:00+00:00": 681.8721251541847,
                                ...
								
								
							}
						},
						"stats": {
							"residual_mean": -4.967807422809462,
							"residual_std": 17541.097726756405,
							"seasonal_amplitude": 4865.967293896343,
							"trend_strength": 0.9920980801644385
						},
						"metadata": {
							"original_rows": 161568,
							"processed_rows": 816,
							"date_range": {
								"start": "2020-01-22 00:00:00+00:00",
								"end": "2022-04-16 00:00:00+00:00"
							},
							"frequency_set": "D"
						},
						"warnings": []
					}
				},
				"anomaly_detection": {
					"Confirmed": {
						"method": "iqr",
						"anomaly_count": 24612,
						"anomaly_percentage": 15.23321449792038,
						"bounds": {
							"lower": -378719.5,
							"upper": 634068.5
						}
					},
					"Recovered": {
						"method": "iqr",
						"anomaly_count": 31984,
						"anomaly_percentage": 19.795999207763913,
						"bounds": {
							"lower": -24927.0,
							"upper": 41545.0
						}
					},
					"Deaths": {
						"method": "iqr",
						"anomaly_count": 25254,
						"anomaly_percentage": 15.630570409982175,
						"bounds": {
							"lower": -6688.0,
							"upper": 11184.0
						}
					}
				}
			},
			"visualizations": {
				"basic": {
					"histograms": {
						"Confirmed": {
							"histogram": [
								869,
								42,
								13,
								8,
								8,
								5,
								7,
								5,
								6,
								3,
								3,
								17,
								3,
								0,
								0,
								0,
								0,
								1,
								2,
								8
							],
							"bin_edges": [
								0.0,
								453024.75,
								906049.5,
								1359074.25,
								1812099.0,
								2265123.75,
								2718148.5,
								3171173.25,
								3624198.0,
								4077222.75,
								4530247.5,
								4983272.25,
								5436297.0,
								5889321.75,
								6342346.5,
								6795371.25,
								7248396.0,
								7701420.75,
								8154445.5,
								8607470.25,
								9060495.0
							],
							"type": "histogram"
						},
						"Recovered": {
							"histogram": [
								906,
								40,
								23,
								3,
								3,
								2,
								3,
								3,
								3,
								2,
								0,
								1,
								2,
								1,
								0,
								1,
								2,
								1,
								1,
								3
							],
							"bin_edges": [
								0.0,
								221049.75,
								442099.5,
								663149.25,
								884199.0,
								1105248.75,
								1326298.5,
								1547348.25,
								1768398.0,
								1989447.75,
								2210497.5,
								2431547.25,
								2652597.0,
								2873646.75,
								3094696.5,
								3315746.25,
								3536796.0,
								3757845.75,
								3978895.5,
								4199945.25,
								4420995.0
							],
							"type": "histogram"
						},
						"Deaths": {
							"histogram": [
								821,
								99,
								18,
								3,
								2,
								4,
								3,
								4,
								4,
								1,
								2,
								1,
								1,
								3,
								1,
								3,
								3,
								5,
								14,
								8
							],
							"bin_edges": [
								0.0,
								6417.2,
								12834.4,
								19251.6,
								25668.8,
								32086.0,
								38503.2,
								44920.4,
								51337.6,
								57754.799999999996,
								64172.0,
								70589.2,
								77006.4,
								83423.59999999999,
								89840.8,
								96258.0,
								102675.2,
								109092.4,
								115509.59999999999,
								121926.8,
								128344.0
							],
							"type": "histogram"
						}
					},
					"correlation_heatmap": {
						"matrix": [
							[
								1.0,
								0.2518152071719809,
								0.917359718269641
							],
							[
								0.2518152071719809,
								1.0,
								0.3261470909982002
							],
							[
								0.917359718269641,
								0.3261470909982002,
								1.0
							]
						],
						"columns": [
							"Confirmed",
							"Recovered",
							"Deaths"
						],
						"type": "heatmap"
					},
					"box_plots": {
						"Confirmed": {
							"q1": 1123.5,
							"q2": 32472.5,
							"q3": 199929.25,
							"whisker_low": 0.0,
							"whisker_high": 3154486.6999999997,
							"outliers": [
								3165121,
							
							],
							"type": "boxplot"
						},
						"Recovered": {
							"q1": 0.0,
							"q2": 587.0,
							"q3": 34822.75,
							"whisker_low": 0.0,
							"whisker_high": 474100.6999999993,
							"outliers": [
								488231,
                                    ...
							],
							"type": "boxplot"
						},
						"Deaths": {
							"q1": 38.5,
							"q2": 907.5,
							"q3": 3654.5,
							"whisker_low": 0.0,
							"whisker_high": 44598.999999999905,
							"outliers": [
								46575,
                                ...

							],
							"type": "boxplot"
						}
					}
				},
				"time_series": {
					"time_series": {},
					"warnings": [
						"Failed to process Confirmed: min() takes 1 positional argument but 2 were given",
						"Failed to process Recovered: min() takes 1 positional argument but 2 were given",
						"Failed to process Deaths: min() takes 1 positional argument but 2 were given"
					],
					"metadata": {
						"time_column": "Date",
						"value_columns_used": [
							"Confirmed",
							"Recovered",
							"Deaths"
						],
						"aggregation_method": "mean",
						"total_records": 161568,
						"date_range": {
							"min": "2020-01-22",
							"max": "2022-04-16"
						}
					}
				}
			},
			"warnings": []
		},
		"id": "d06fd59c-5a06-4747-8397-4d9fe74c25dc",
		"updated_at": "2025-10-28T15:02:02.943256Z",
		"title": "Big Data Analysis",
		"data_visualizations": {
			"correlation_plot": "{\"data\":[...}",
			"histogram_Confirmed": "{\"data\":[...}",
			"histogram_Recovered": "{\"data\":[...}",
			"histogram_Deaths": "{\"data\":[...}",
			"time_series_plot": "{\"data\":[] ...}"
		},
		"ai_insights": "Here is a simple summary of the data:\n\n**Data Overview**\n\n* **Total Rows:** 161,568\n* **Total Columns:** 5\n* **Visualizations:** 5 different types\n\n**Analysis Types**\n\nWe have information on the following 6 analysis types:\n1. Timestamp\n2. Analysis Config\n3. Data Summary\n4. Analyses\n5. Visualizations\n6. Warnings\n\nLet me know if you'd like me to help with anything else!",
		"created_at": "2025-10-28T15:02:02.943003Z",
		"_class_": "BigDataResult"
	}
}
```

##### Error Response

- **Status Code:** `404 Not Found`
  - **Detail:** Task result not found.
  - **Example:**
    ```json
    {
        "detail": "Task result not found"
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Failed to retrieve the analysis result.
  - **Example:**
    ```json
    {
        "detail": "Failed to retrieve analysis result: <error_message>"
    }
    ```
