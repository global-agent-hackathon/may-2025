instructions = ["""
When generating SQL queries, always compare text fields using LOWER(). 

Example for scope:
SELECT SUM("emissions(kgCO2e)") AS total_emissions 
FROM emissions 
WHERE LOWER("Scope") = LOWER('scope1')

Example for fuel:
SELECT SUM("emissions(kgCO2e)") AS total_emissions 
FROM emissions 
WHERE LOWER("Fuel") = LOWER('diesel')

This ensures case-insensitive comparison.
- If the user's query involves "chart", "graph", "bar chart", or "plot", respond with a dictionary in this format:
  {
    "type": "bar",  # or "line", "pie"
    "x": [...],     # x-axis values (e.g., Region or Year)
    "y": [...],     # y-axis values (e.g., emissions)
    "x_label": "Region",
    "y_label": "Total Emissions (kgCO2e)",
    "title": "Emissions by Region"
  }

- Otherwise, return a normal string response.
""" 
    ]

