import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("tokyo_weather.csv")


df.columns = df.columns.str.strip()


df['date'] = pd.to_datetime(df['year'].astype(str) + '/' + df['day'])


df['temperature'] = pd.to_numeric(
    df['temperature'].astype(str).str.replace(r'[()]', '', regex=True),
    errors='coerce'
)


average_temp = df['temperature'].mean()

print("Average Temperature:")
print(f"{average_temp:.2f} °C")


df['month'] = df['date'].dt.month

monthly_avg = df.groupby('month')['temperature'].mean()

print("\nMonthly Average Temperatures:")
print(monthly_avg)


plt.figure(figsize=(10,5))

monthly_avg.plot(kind='bar', color='skyblue')

plt.title("Monthly Average Temperature")
plt.xlabel("Month")
plt.ylabel("Temperature (°C)")

plt.show()


hottest_day = df.loc[df['temperature'].idxmax()]
coldest_day = df.loc[df['temperature'].idxmin()]

print("\nHottest Day:")
print(hottest_day)

print("\nColdest Day:")
print(coldest_day)


plt.figure(figsize=(12,5))

plt.plot(df['date'], df['temperature'], color='red')

plt.title("Temperature Over Time")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")

plt.show()


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

df['season'] = df['date'].dt.month.apply(get_season)

seasonal_avg = df.groupby('season')['temperature'].mean()

print("\nSeasonal Average Temperatures:")
print(seasonal_avg)


plt.figure(figsize=(8,5))

seasonal_avg.plot(
    kind='bar',
    color=['blue', 'green', 'orange', 'brown']
)

plt.title("Seasonal Average Temperature")
plt.xlabel("Season")
plt.ylabel("Temperature (°C)")

plt.show()