import plotly.express as px

import pandas as pd

import matplotlib.pyplot as pit
from matplotlib.projections import projection_registry

df = pd.read_csv("avgIQpercountry.csv")
df['Population - 2023']= df['Population - 2023'].str.replace(',','').astype(float)

print(float)

fig = px.scatter_geo(df,locations='Country',locationmode='Country names'
                     ,over_name='Country',size="Average IQ",color='Continent',
                     projection='natural earth',title="Average IQ by Country",
                     size_max=20,template='plotly_dark')

fig.show()
