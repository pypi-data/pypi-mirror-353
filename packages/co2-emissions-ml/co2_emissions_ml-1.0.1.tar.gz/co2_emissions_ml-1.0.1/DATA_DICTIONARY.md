# Data Dictionary

This document describes each column in the `co2_emission_by_vehicles.csv` dataset.

| Column Name                      | Type        | Description                                         |
| -------------------------------- | ----------- | --------------------------------------------------- |
| Make                             | categorical | Manufacturer of the vehicle (e.g., Toyota, Ford)    |
| Model                            | categorical | Vehicle model name                                  |
| Vehicle Class                    | categorical | Category (e.g., SUV, Sedan, Truck)                  |
| Engine Size (L)                  | float       | Displacement in liters                              |
| Cylinders                        | integer     | Number of engine cylinders                          |
| Transmission                     | categorical | Transmission type (e.g., Automatic, Manual, CVT)    |
| Fuel Type                        | categorical | Fuel used (e.g., Gasoline, Diesel, Electric)        |
| Fuel Consumption City (L/100 km) | float       | City fuel consumption rating                        |
| Fuel Consumption Hwy (L/100 km)  | float       | Highway fuel consumption rating                     |
| Fuel Consumption Comb (L/100 km) | float       | Combined fuel consumption rating                    |
| CO$_2$ Emissions (g/km)          | float       | Tailpipe carbon dioxide emissions (target variable) |
