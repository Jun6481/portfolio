
import pandas as pd

# Load the CSV file into a DataFrame
data = pd.read_csv('/content/202212-divvy-tripdata.csv')

# Check the data
print(data.head())

# Method 1: Using the shape attribute
row_count = data.shape[0]

# Method 2: Using the len() function
row_count = len(data)

# Print the number of rows
print("Total row count:", row_count)

print(data.head())
print(data.info())

# Check for duplicate data
print(data.duplicated().sum())

# Outlier detection (e.g., very long or short rental times)
# This part can vary depending on the characteristics of your data.

# Verify the freshness of the data
# This can be done by checking the 'started_at' or 'ended_at' columns.
print(data['started_at'].max())
print(data['ended_at'].max())

# Check for missing values
print(data.isnull().sum())

# Data type validation

# Extract unique station information based on latitude and longitude for both start and end stations
unique_start_stations = data.dropna(subset=['start_station_name', 'start_station_id']).drop_duplicates(['start_lat', 'start_lng'])
unique_end_stations = data.dropna(subset=['end_station_name', 'end_station_id']).drop_duplicates(['end_lat', 'end_lng'])

# Fill in missing start station information
for index, row in data.iterrows():
    if pd.isnull(row['start_station_name']) or pd.isnull(row['start_station_id']):
        match = unique_start_stations[(unique_start_stations['start_lat'] == row['start_lat']) & (unique_start_stations['start_lng'] == row['start_lng'])]
        if not match.empty:
            data.at[index, 'start_station_name'] = match.iloc[0]['start_station_name']
            data.at[index, 'start_station_id'] = match.iloc[0]['start_station_id']

# Fill in missing end station information
for index, row in data.iterrows():
    if pd.isnull(row['end_station_name']) or pd.isnull(row['end_station_id']):
        match = unique_end_stations[(unique_end_stations['end_lat'] == row['end_lat']) & (unique_end_stations['end_lng'] == row['end_lng'])]
        if not match.empty:
            data.at[index, 'end_station_name'] = match.iloc[0]['end_station_name']
            data.at[index, 'end_station_id'] = match.iloc[0]['end_station_id']

# Check for missing values
print(data.isnull().sum())

# Convert 'started_at' and 'ended_at' columns to datetime format
data['started_at'] = pd.to_datetime(data['started_at'])
data['ended_at'] = pd.to_datetime(data['ended_at'])
# Calculate trip duration
data['trip_duration'] = data['ended_at'] - data['started_at']

# Fare system setup
member_rate_per_week = 25  # Member users' weekly rate
casual_rate_per_minute = 0.45  # Casual users' per-minute rate

# Convert 'trip_duration' to seconds
data['trip_duration_seconds'] = data['trip_duration'].dt.total_seconds()

# Calculate member user revenue
member_revenue = data[data['member_casual'] == 'member'].shape[0] * member_rate_per_week

# Calculate casual user revenue
casual_revenue = (data[data['member_casual'] == 'casual']['trip_duration_seconds'].sum() / 60) * casual_rate_per_minute

# Print the results
print(f"Member user revenue: ${member_revenue:,.2f}")
print(f"Casual user revenue: ${casual_revenue:,.2f}")

import matplotlib.pyplot as plt

# Revenue data
revenues = [member_revenue, casual_revenue]
labels = ['Member Users', 'Casual Users']
explode = (0.1, 0)  # Only pop out the Member Users segment
colors = ['#00876c', '#89d0b0']  # Sophisticated green color palette

# Create the pie chart
fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(revenues, explode=explode, labels=labels, autopct='%1.1f%%',
                                   startangle=90, colors=colors, textprops=dict(color="w"))

# Set font size and color
plt.setp(texts, size=12, weight="bold", color="black")
plt.setp(autotexts, size=10, weight="bold")

# Make the pie chart circular
ax.axis('equal')

# Set the title with font style
plt.title('Revenue Share by User Type', fontdict={'fontsize': 16, 'fontweight': 'bold'})

# Show the pie chart
plt.show()

# Calculate usage frequency for member and casual users
member_usage_frequency = data[data['member_casual'] == 'member'].shape[0]
casual_usage_frequency = data[data['member_casual'] == 'casual'].shape[0]

# Print the usage frequency
print("Member User Usage Frequency:", member_usage_frequency)
print("Casual User Usage Frequency:", casual_usage_frequency)

# Calculate and print unit cost for member and casual users
member_unit_cost = member_revenue / member_usage_frequency
casual_unit_cost = casual_revenue / casual_usage_frequency

print("Member User Unit Cost:", member_unit_cost)
print("Casual User Unit Cost:", casual_unit_cost)

import matplotlib.pyplot as plt

# Calculate revenues and frequencies for 'member' and 'casual' users
# Here, we use arbitrary revenue and frequency values. You may need to adjust these based on actual data.
revenues = [member_revenue, casual_revenue]
frequencies = [data[data['member_casual'] == 'member'].shape[0], data[data['member_casual'] == 'casual'].shape[0]]

categories = ['member', 'casual']
positions = range(len(categories))
width = 0.4  # Bar width

fig, ax1 = plt.subplots(figsize=(8, 6))

# Bar chart for Revenue
color = 'tab:blue'
ax1.set_xlabel('Membership Type')
ax1.set_ylabel('Revenue ($)', color=color)
ax1.bar([p - width/2 for p in positions], revenues, width=width, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Adding 'M' to left y-axis tick labels
def millions_formatter(x, pos):
    return f'{x / 1_000_000}M'
ax1.yaxis.set_major_formatter(plt.FuncFormatter(millions_formatter))

# Bar chart for Frequency, set y-axis on the right and adjust the ticks
ax2 = ax1.twinx()
color = 'tab:orange'
ax2.set_ylabel('Frequency', color=color)
ax2.bar([p + width/2 for p in positions], frequencies, width=width, color=color)
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 160000)  # Set y-axis range from 0 to 160,000

# Set x-axis labels
ax1.set_xticks(positions)
ax1.set_xticklabels(categories)

plt.title('Comparison of Revenue and Frequency by Membership Type')
fig.tight_layout()

# Display the chart
plt.show()

# Calculate the percentage distribution of bike types based on the 'rideable_type' column
bike_type_counts = data['rideable_type'].value_counts(normalize=True) * 100

# Print the results
print(bike_type_counts)

# Group by start station and rideable type to calculate usage counts
station_bike_usage = data.groupby(['start_station_id', 'rideable_type']).size().unstack(fill_value=0)

# Select only electric_bike and classic_bike
station_bike_usage = station_bike_usage[['electric_bike', 'classic_bike']]

# Extract the top 20 stations based on total usage
top_20_stations = station_bike_usage.sum(axis=1).nlargest(20).index

# Get the usage counts of electric_bike and classic_bike for the top 20 stations
top_20_station_usage = station_bike_usage.loc[top_20_stations]

# Print the results
print(top_20_station_usage)

# Remove rows with missing values (NaN)
data.dropna(inplace=True)

# Calculate the total row count
row_count = data.shape[0]

# Print the total row count
print("Total number of rows:", row_count)

# Create a new DataFrame 'trip_data' by selecting specific columns
trip_data = data[['started_at', 'ended_at', 'trip_duration']]

trip_data['trip_duration'].min()

# Filtering rows where 'trip_duration' is negative
negative_duration_data = data[data['trip_duration'] < pd.Timedelta(0)]

# Checking the results
print(negative_duration_data)

# Calculate the number of rows in the 'negative_duration_data' DataFrame
number_of_rows = len(negative_duration_data)

# Display the result
number_of_rows

data['trip_duration'].describe()

ratio_caual_member=casual_usage_frequency/(member_usage_frequency + casual_usage_frequency)
ratio_caual_member

# Adding 'hour_of_day' column to represent the hour of the day when the trip started
data['hour_of_day'] = data['started_at'].dt.hour

# Calculating usage hour distribution for member and casual users
member_hour_usage = data[data['member_casual'] == 'member']['hour_of_day'].value_counts().sort_index()
casual_hour_usage = data[data['member_casual'] == 'casual']['hour_of_day'].value_counts().sort_index()

# Calculating major starting stations for member and casual users
member_start_stations = data[data['member_casual'] == 'member']['start_station_name'].value_counts()
casual_start_stations = data[data['member_casual'] == 'casual']['start_station_name'].value_counts()

# Printing the results
print("Member Usage Hour Distribution:\n", member_hour_usage)
print("\nCasual Usage Hour Distribution:\n", casual_hour_usage)
print("\nMajor Starting Stations for Members:\n", member_start_stations.head())
print("\nMajor Starting Stations for Casual Users:\n", casual_start_stations.head(10))

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

# Member Users - Lighter color and thinner line for a subtle appearance
plt.plot(member_hour_usage, label='Member', color='lightgray', linewidth=2)

# Casual Users - Darker color and thicker line for emphasis
plt.plot(casual_hour_usage, label='Casual', color='darkblue', linewidth=3)

plt.title('Hourly Usage Distribution: Member vs Casual')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Uses')
plt.xticks(range(0, 24))
plt.legend()
plt.show()

# List of stations of interest
stations = [
    'Shedd Aquarium',
    'Streeter Dr & Grand Ave',
    'Millennium Park',
    'DuSable Lake Shore Dr & Monroe St',
    'Kingsbury St & Kinzie St',
    'Clark St & Newport St',
    'LaSalle St & Illinois St',
    'Clark St & Elm St',
    'Wabash Ave & Grand Ave',
    'Michigan Ave & 8th St'
]

# Extract latitude and longitude information for each station
station_coordinates = {}
for station in stations:
    station_data = data[data['start_station_name'] == station].iloc[0]
    station_coordinates[station] = {
        'start_lat': station_data['start_lat'],
        'start_lng': station_data['start_lng']
    }

# Print the extracted information
for station, coords in station_coordinates.items():
    print(f"{station}: Latitude {coords['start_lat']}, Longitude {coords['start_lng']}")

import math
import pandas as pd

# Function to calculate distance using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    # Earth's radius (in kilometers)
    R = 6371.0

    # Convert latitude and longitude to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Calculate the differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate the final distance
    distance = R * c
    return distance

# Calculate distance for each row in the DataFrame
data['distance'] = data.apply(lambda row: haversine(row['start_lat'], row['start_lng'], row['end_lat'], row['end_lng']), axis=1)

# Check the results
print(data[['start_lat', 'start_lng', 'end_lat', 'end_lng', 'distance']].head())

# Calculate the average distance for Member users
member_avg_distance = data[data['member_casual'] == 'member']['distance'].mean()

# Calculate the average distance for Casual users
casual_avg_distance = data[data['member_casual'] == 'casual']['distance'].mean()

# Print the results
print(f"Average Distance for Member Users: {member_avg_distance} km")
print(f"Average Distance for Casual Users: {casual_avg_distance} km")

# Combine 'start_station_name' and 'end_station_name' to create routes
data['route'] = data['start_station_name'] + " to " + data['end_station_name']

# Calculate the top routes used by Member users
member_routes = data[data['member_casual'] == 'member']['route'].value_counts().head(10)

# Calculate the top routes used by Casual users
casual_routes = data[data['member_casual'] == 'casual']['route'].value_counts().head(10)

# Print the results
print("Top Routes Used by Member Users:\n", member_routes)
print("Top Routes Used by Casual Users:\n", casual_routes)

# Create a 'route' column by combining 'start_station_name' and 'end_station_name'
data['route'] = data['start_station_name'] + " to " + data['end_station_name']

# Calculate the top routes used by Member users
member_routes = data[data['member_casual'] == 'member']['route'].value_counts().head(10)

# Calculate the top routes used by Casual users
casual_routes = data[data['member_casual'] == 'casual']['route'].value_counts().head(10)

# Function to extract coordinates for routes
def get_route_coordinates(data, top_routes):
    route_coordinates = {}
    for route in top_routes.index:
        start_station, end_station = route.split(" to ")
        start_coords = data[data['start_station_name'] == start_station][['start_lat', 'start_lng']].iloc[0]
        end_coords = data[data['end_station_name'] == end_station][['end_lat', 'end_lng']].iloc[0]
        route_coordinates[route] = (start_coords.tolist(), end_coords.tolist())
    return route_coordinates

# Extract coordinates for top routes used by Member users
member_route_coords = get_route_coordinates(data, member_routes)

# Extract coordinates for top routes used by Casual users
casual_route_coords = get_route_coordinates(data, casual_routes)

# Print the coordinate results
print("Coordinates for Top Routes Used by Member Users:\n", member_route_coords)
print("Coordinates for Top Routes Used by Casual Users:\n", casual_route_coords)

import folium

# Coordinates for Member users' top routes
member_route_coords = {
    'Ellis Ave & 60th St to University Ave & 57th St': ([41.78509416666667, -87.60108833333334], [41.791478, -87.599861]),
    'Ellis Ave & 60th St to Ellis Ave & 55th St': ([41.78509416666667, -87.60108833333334], [41.79430062054, -87.6014497734]),
    'University Ave & 57th St to Ellis Ave & 60th St': ([41.791512, -87.59993216666666], [41.78509714636, -87.6010727606]),
    'Ellis Ave & 55th St to Ellis Ave & 60th St': ([41.79430062054, -87.6014497734], [41.78509714636, -87.6010727606]),
    'State St & 33rd St to Calumet Ave & 33rd St': ([41.834722281, -87.625763297], [41.8349, -87.61793]),
     'Calumet Ave & 33rd St to State St & 33rd St': ([41.834852815, -87.617890954], [41.834734, -87.625813]),
    'Loomis St & Lexington St to Morgan St & Polk St': ([41.87222873224032, -87.66136385500431], [41.871737, -87.65103]),
    'Morgan St & Polk St to Loomis St & Lexington St': ([41.872038484, -87.650987387], [41.87222873224032, -87.66136385500431]),
    'University Ave & 57th St to Kimbark Ave & 53rd St': ([41.791512, -87.59993216666666], [41.799568, -87.594747]),
    'Ellis Ave & 58th St to Ellis Ave & 60th St': ([41.78856366666667, -87.601174], [41.78509714636, -87.6010727606])
}

# Coordinates for Casual users' top routes
casual_route_coords = {
    'Streeter Dr & Grand Ave to Streeter Dr & Grand Ave': ([41.892278, -87.612043], [41.892278, -87.612043]),
    'Ellis Ave & 60th St to Ellis Ave & 55th St': ([41.78509416666667, -87.60108833333334], [41.79430062054, -87.6014497734]),
    'DuSable Lake Shore Dr & Monroe St to DuSable Lake Shore Dr & Monroe St': ([41.880958, -87.616743], [41.880958, -87.616743]),
    'Ellis Ave & 55th St to Ellis Ave & 60th St': ([41.79430062054, -87.6014497734], [41.78509714636, -87.6010727606]),
    'DuSable Lake Shore Dr & Monroe St to Streeter Dr & Grand Ave': ([41.880958, -87.616743], [41.892278, -87.612043]),
    'Ellis Ave & 60th St to University Ave & 57th St': ([41.78509416666667, -87.60108833333334], [41.791478, -87.599861]),
    'University Ave & 57th St to Ellis Ave & 60th St': ([41.791512, -87.59993216666666], [41.78509714636, -87.6010727606]),
    'University Ave & 57th St to Kimbark Ave & 53rd St': ([41.791512, -87.59993216666666], [41.799568, -87.594747]),
    'Streeter Dr & Grand Ave to Millennium Park': ([41.892278, -87.612043], [41.881032, -87.624084]),
    'Sheffield Ave & Fullerton Ave to Greenview Ave & Fullerton Ave': ([41.92556283333333, -87.6537395], [41.92533, -87.6658])
}

# Create a map centered at a specific location with a zoom level
m = folium.Map(location=[41.8781, -87.6298], zoom_start=12)

# Plot Member users' routes in blue
for route, coords in member_route_coords.items():
    folium.PolyLine(coords, color="blue").add_to(m)

# Plot Casual users' routes in red
for route, coords in casual_route_coords.items():
    folium.PolyLine(coords, color="red").add_to(m)

# Save the map to an HTML file
m.save("map.html")

import folium

# Coordinates for Casual users' top routes
casual_route_coords = {
    'Streeter Dr & Grand Ave to Streeter Dr & Grand Ave': ([41.892278, -87.612043], [41.892278, -87.612043]),
    'Ellis Ave & 60th St to Ellis Ave & 55th St': ([41.78509416666667, -87.60108833333334], [41.79430062054, -87.6014497734]),
    'DuSable Lake Shore Dr & Monroe St to DuSable Lake Shore Dr & Monroe St': ([41.880958, -87.616743], [41.880958, -87.616743]),
    'Ellis Ave & 55th St to Ellis Ave & 60th St': ([41.79430062054, -87.6014497734], [41.78509714636, -87.6010727606]),
    'DuSable Lake Shore Dr & Monroe St to Streeter Dr & Grand Ave': ([41.880958, -87.616743], [41.892278, -87.612043]),
    'Ellis Ave & 60th St to University Ave & 57th St': ([41.78509416666667, -87.60108833333334], [41.791478, -87.599861]),
    'University Ave & 57th St to Ellis Ave & 60th St': ([41.791512, -87.59993216666666], [41.78509714636, -87.6010727606]),
    'University Ave & 57th St to Kimbark Ave & 53rd St': ([41.791512, -87.59993216666666], [41.799568, -87.594747]),
    'Streeter Dr & Grand Ave to Millennium Park': ([41.892278, -87.612043], [41.881032, -87.624084]),
    'Sheffield Ave & Fullerton Ave to Greenview Ave & Fullerton Ave': ([41.92556283333333, -87.6537395], [41.92533, -87.6658])
}

# Usage frequency for each route
route_usage = {
    'Streeter Dr & Grand Ave to Streeter Dr & Grand Ave': 192,
    'Ellis Ave & 60th St to Ellis Ave & 55th St': 180,
    'DuSable Lake Shore Dr & Monroe St to DuSable Lake Shore Dr & Monroe St': 165,
    'Ellis Ave & 55th St to Ellis Ave & 60th St': 161,
    'DuSable Lake Shore Dr & Monroe St to Streeter Dr & Grand Ave': 155,
    'Ellis Ave & 60th St to University Ave & 57th St': 153,
    'University Ave & 57th St to Ellis Ave & 60th St': 133,
    'University Ave & 57th St to Kimbark Ave & 53rd St': 94,
    'Streeter Dr & Grand Ave to Millennium Park': 86,
    'Sheffield Ave & Fullerton Ave to Greenview Ave & Fullerton Ave': 81
}

# Create a map centered at a specific location with a zoom level
m = folium.Map(location=[41.8781, -87.6298], zoom_start=12)

# Plot Casual users' routes on the map with markers
for route, coords in casual_route_coords.items():
    # Adjust line thickness based on usage frequency
    line_weight = route_usage.get(route, 1) * 0.05  # Adjust line thickness based on usage frequency

    # Display the route as a polyline
    folium.PolyLine(coords, color="red", weight=line_weight, alpha=0.5).add_to(m)

    # Add a marker at the endpoint with route information as a popup
    folium.Marker(coords[1], popup=route).add_to(m)

# Save the map to an HTML file
m.save("map.html")

# Remove duplicates from 'start_station_id' and 'end_station_id' columns and calculate the total number of unique stations
unique_stations = pd.concat([data['start_station_id'], data['end_station_id']]).unique()
number_of_stations = len(unique_stations)

# Print the result
print(f"Total number of unique stations without duplicates: {number_of_stations}")

import folium

# Calculate station usage frequency
station_usage_start = data['start_station_id'].value_counts()
station_usage_end = data['end_station_id'].value_counts()
station_usage = station_usage_start.add(station_usage_end, fill_value=0)

# Extract station location data
station_locations = data.groupby('start_station_id').first()[['start_lat', 'start_lng']].dropna()

# Create a map
m = folium.Map(location=[station_locations['start_lat'].mean(), station_locations['start_lng'].mean()], zoom_start=12)

# Add markers for each station
for station_id, row in station_locations.iterrows():
    usage = station_usage.get(station_id, 0)
    # Limit the size of the circle to prevent it from being too large
    radius = min(usage, 1000) * 2  # Limit the maximum size to 1000
    folium.Circle(
        location=(row['start_lat'], row['start_lng']),
        radius=radius,
        color='blue',
        fill=True,
        fill_opacity=0.01,
        weight=0.1
    ).add_to(m)

# Save the map
m.save("map.html")

# Calculate the day of the week for each ride (1 = Sunday, 7 = Saturday)
data['day_of_week'] = data['started_at'].dt.dayofweek + 1

# Calculate the frequency of rides for the overall dataset by day of the week
overall_day_frequency = data['day_of_week'].value_counts().sort_index()

# Calculate the frequency of rides for member users by day of the week
member_day_frequency = data[data['member_casual'] == 'member']['day_of_week'].value_counts().sort_index()

# Calculate the frequency of rides for casual users by day of the week
casual_day_frequency = data[data['member_casual'] == 'casual']['day_of_week'].value_counts().sort_index()

# Print the results
print("Overall day frequency: {0}".format(overall_day_frequency))
print("Member day frequency: {0}".format(member_day_frequency))
print("Casual day frequency: {0}".format(casual_day_frequency))

import matplotlib.pyplot as plt

# Calculate the frequency of rides for the overall dataset by day of the week
overall_day_frequency = data['day_of_week'].value_counts().sort_index()

# Calculate the frequency of rides for member users by day of the week
member_day_frequency = data[data['member_casual'] == 'member']['day_of_week'].value_counts().sort_index()

# Calculate the frequency of rides for casual users by day of the week
casual_day_frequency = data[data['member_casual'] == 'casual']['day_of_week'].value_counts().sort_index()

# Create a figure for the plot
plt.figure(figsize=(12, 6))

# Plot the usage frequency for overall, member, and casual users
plt.plot(overall_day_frequency.index, overall_day_frequency.values, label='Overall', marker='o')
plt.plot(member_day_frequency.index, member_day_frequency.values, label='Member', marker='o')
plt.plot(casual_day_frequency.index, casual_day_frequency.values, label='Casual', marker='o')

# Set plot title and labels
plt.title('Day of the Week Usage Frequency')
plt.xlabel('Day of the Week (1=Sunday, 7=Saturday)')
plt.ylabel('Number of Rides')
plt.xticks(range(1, 8))
plt.legend()

# Display the plot
plt.show()

# Calculate usage by day of the week
data['day_of_week'] = data['started_at'].dt.day_name()

# Find the most common hour for each day of the week
best_marketing_times = data.groupby('day_of_week')['started_at'].apply(lambda x: x.dt.hour.mode().iloc[0]).reset_index()

# Print the results
print("Best Marketing Times by Day of the Week:")
for index, row in best_marketing_times.iterrows():
    print(f"{row['day_of_week']}: {row['started_at']} AM")

# Calculate usage count by day of the week and hour
usage_by_day_hour = data.groupby(['day_of_week', 'hour_of_day']).size().reset_index(name='Usage Count')

# Select the top 10 combinations
top_10_times = usage_by_day_hour.nlargest(10, 'Usage Count')

# Print the results
print("Top 10 Combinations of Day of the Week and Hour with Highest Usage Count:")
for index, row in top_10_times.iterrows():
    print(f"{row['day_of_week']} {row['hour_of_day']} AM - Usage Count: {row['Usage Count']} rides")

# Select casual users only
casual_data = data[data['member_casual'] == 'casual']

# Calculate usage count by day of the week and hour for casual users
usage_by_day_hour = casual_data.groupby(['day_of_week', 'hour_of_day']).size().reset_index(name='Usage Count')

# Select the top 10 combinations
top_10_times = usage_by_day_hour.nlargest(10, 'Usage Count')

# Print the results
print("Top 10 Combinations of Day of the Week and Hour with Highest Usage Count for Casual Users:")
for index, row in top_10_times.iterrows():
    print(f"{row['day_of_week']} {row['hour_of_day']} AM - Usage Count: {row['Usage Count']} rides")

import folium

# List of stations of interest
stations = [
    'Shedd Aquarium',
    'Streeter Dr & Grand Ave',
    'Millennium Park',
    'DuSable Lake Shore Dr & Monroe St',
    'Kingsbury St & Kinzie St',
    'Clark St & Newport St',
    'LaSalle St & Illinois St',
    'Clark St & Elm St',
    'Wabash Ave & Grand Ave',
    'Michigan Ave & 8th St'
]

# Frequency of each station (Location information is replaced with hypothetical data)
station_frequencies = {
    'Shedd Aquarium': 433,
    'Streeter Dr & Grand Ave': 406,
    'Millennium Park': 300,
    'DuSable Lake Shore Dr & Monroe St': 298,
    'Kingsbury St & Kinzie St': 246,
    'Clark St & Newport St': 242,
    'LaSalle St & Illinois St': 236,
    'Clark St & Elm St': 231,
    'Wabash Ave & Grand Ave': 231,
    'Michigan Ave & 8th St': 227
}

# Latitude and longitude coordinates for each station (Hypothetical data)
station_coordinates = {
    'Shedd Aquarium': {'start_lat': 41.867226, 'start_lng': -87.615355},
    'Streeter Dr & Grand Ave': {'start_lat': 41.892278, 'start_lng': -87.612043},
    'Millennium Park': {'start_lat': 41.881032, 'start_lng': -87.624084},
    'DuSable Lake Shore Dr & Monroe St': {'start_lat': 41.880958, 'start_lng': -87.616743},
    'Kingsbury St & Kinzie St': {'start_lat': 41.889177, 'start_lng': -87.638506},
    'Clark St & Newport St': {'start_lat': 41.944540, 'start_lng': -87.654678},
    'LaSalle St & Illinois St': {'start_lat': 41.890755, 'start_lng': -87.632009},
    'Clark St & Elm St': {'start_lat': 41.902973, 'start_lng': -87.631280},
    'Wabash Ave & Grand Ave': {'start_lat': 41.891738, 'start_lng': -87.626937},
    'Michigan Ave & 8th St': {'start_lat': 41.872773, 'start_lng': -87.623981}
}

# Create a map
map = folium.Map(location=[41.8781, -87.6298], zoom_start=13)

# Add markers for each station's location
for station, freq in station_frequencies.items():
    coords = station_coordinates[station]
    folium.Circle(
        location=[coords['start_lat'], coords['start_lng']],
        radius=freq/2,  # Adjust the size based on frequency
        color='blue',
        fill=True,
        fill_color='blue',
        popup=f"{station}: {freq} rides"
    ).add_to(map)

# Display the map
map

import folium

# Coordinates of the top routes used by casual users
casual_route_coords = {
    'Streeter Dr & Grand Ave to Streeter Dr & Grand Ave': ([41.892278, -87.612043], [41.892278, -87.612043]),
    'Ellis Ave & 60th St to Ellis Ave & 55th St': ([41.78509416666667, -87.60108833333334], [41.79430062054, -87.6014497734]),
    'DuSable Lake Shore Dr & Monroe St to DuSable Lake Shore Dr & Monroe St': ([41.880958, -87.616743], [41.880958, -87.616743]),
    'Ellis Ave & 55th St to Ellis Ave & 60th St': ([41.79430062054, -87.6014497734], [41.78509714636, -87.6010727606]),
    'DuSable Lake Shore Dr & Monroe St to Streeter Dr & Grand Ave': ([41.880958, -87.616743], [41.892278, -87.612043]),
    'Ellis Ave & 60th St to University Ave & 57th St': ([41.78509416666667, -87.60108833333334], [41.791478, -87.599861]),
    'University Ave & 57th St to Ellis Ave & 60th St': ([41.791512, -87.59993216666666], [41.78509714636, -87.6010727606]),
    'University Ave & 57th St to Kimbark Ave & 53rd St': ([41.791512, -87.59993216666666], [41.799568, -87.594747]),
    'Streeter Dr & Grand Ave to Millennium Park': ([41.892278, -87.612043], [41.881032, -87.624084]),
    'Sheffield Ave & Fullerton Ave to Greenview Ave & Fullerton Ave': ([41.92556283333333, -87.6537395], [41.92533, -87.6658])
}

# Usage frequency of each route
route_usage = {
    'Streeter Dr & Grand Ave to Streeter Dr & Grand Ave': 192,
    'Ellis Ave & 60th St to Ellis Ave & 55th St': 180,
    'DuSable Lake Shore Dr & Monroe St to DuSable Lake Shore Dr & Monroe St': 165,
    'Ellis Ave & 55th St to Ellis Ave & 60th St': 161,
    'DuSable Lake Shore Dr & Monroe St to Streeter Dr & Grand Ave': 155,
    'Ellis Ave & 60th St to University Ave & 57th St': 153,
    'University Ave & 57th St to Ellis Ave & 60th St': 133,
    'University Ave & 57th St to Kimbark Ave & 53rd St': 94,
    'Streeter Dr & Grand Ave to Millennium Park': 86,
    'Sheffield Ave & Fullerton Ave to Greenview Ave & Fullerton Ave': 81
}

# Create a map
m = folium.Map(location=[41.8781, -87.6298], zoom_start=12)

# Display casual users' routes with adjusted line thickness based on usage frequency
for route, coords in casual_route_coords.items():
    # Set line thickness based on usage frequency
    line_weight = route_usage.get(route, 1) * 0.05  # Adjust line thickness based on usage frequency

    # Display the route
    folium.PolyLine(coords, color="blue", weight=line_weight, opacity=0.8).add_to(m)

    # Add markers at the start and end points
    folium.Marker(coords[0], icon=folium.Icon(color='green'), popup=f"Start: {route.split(' to ')[0]}").add_to(m)
    folium.Marker(coords[1], icon=folium.Icon(color='red'), popup=f"End: {route.split(' to ')[1]}").add_to(m)

# Display the map
m

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Using actual data
data = {
    'day_of_week': ['Thursday', 'Thursday', 'Sunday', 'Saturday', 'Thursday', 'Tuesday', 'Saturday', 'Saturday', 'Thursday', 'Friday'],
    'hour_of_day': [17, 16, 15, 15, 15, 17, 12, 16, 18, 15],
    'usage_count': [579, 564, 561, 541, 528, 494, 489, 485, 484, 480]
}
df = pd.DataFrame(data)

# Create a pivot table for day_of_week and hour_of_day
pivot_table = df.pivot("day_of_week", "hour_of_day", "usage_count")

plt.figure(figsize=(10, 7))
sns.heatmap(pivot_table, annot=True, fmt=".0f", linewidths=.5, cmap="Blues")

plt.title('Heatmap of Usage Frequency by Day and Hour for Casual Users', fontsize=16)
plt.ylabel('Day of Week', fontsize=12)

# Change x-axis labels to 'PM'
hour_labels_pm = [f'{hour} PM' for hour in range(12, 19)]
plt.xticks(np.arange(0.5, len(hour_labels_pm) + 0.5), hour_labels_pm)

plt.xlabel('Hour of Day', fontsize=12)

plt.show()
