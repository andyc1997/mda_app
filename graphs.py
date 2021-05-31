import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from itertools import product

# considering only summer months from May to August
class subset_helper():
    def __init__(self, data):
        self.data = data

    def get_summer(self, df):
        return df[(df['MONTH'] <= 8) & (df['MONTH'] >= 5)]

    def get_year(self, df):
        return df[(df['YEAR'] < 2021) & (df['YEAR'] > 2008)]

    def subset(self):
        self.data = self.get_year(self.get_summer(self.data))
        return self.data


# overall visualizations for all 7 countries
class overall_plots():
    def __init__(self, df_concat):
        self.data = df_concat

    def boxplot(self):
        plt.figure(figsize=(7, 5), dpi=80)
        ax = px.box(self.data,x="COUNTRY", y="TEMP_MEAN",color='COUNTRY',
                    title = "Distribution of daily maximum temperature across different countries")
        return ax

    def scatterplot(self):
        df_group = self.data.groupby(['YEAR', 'COUNTRY']).mean()
        df_group = df_group.reset_index().round(2)
        fig = px.scatter(df_group, x="YEAR", y="HEAT_DAYS", color="COUNTRY", size="HEAT_DAYS",
                         title="Heat days per month of countries for period 2009-2020")
        return fig

    def lineplot(self):
        df_group = self.data.groupby(['YEAR', 'COUNTRY']).mean()
        df_group = df_group.reset_index().round(2)
        fig = px.line(df_group, x="YEAR", y="TEMP_MEAN", color="COUNTRY",
                      title='Temperature of countries for period 2009-2020')
        return fig


# country specific visuals
class country_plots():
    def __init__(self, data):
        self.data = data

    def heatmap(self,country):
        data =  self.data.loc[self.data['COUNTRY'] == country]
        df = data.groupby(['MONTH', 'YEAR']).mean()
        df = df.reset_index().round(2)
        df = df.pivot("MONTH", "YEAR", "HEAT_DAYS")
        df = df.fillna(0)
        fig = px.imshow(df, labels=dict(x="YEAR", y="MONTH", color="HEAT_DAYS"))
        fig.update_layout(yaxis_nticks=5, title="Heat Days per Year")
        return fig

    def lineplot(self,country):
        data = self.data.loc[self.data['COUNTRY'] == country]
        fig = px.line(data, x="MONTH", y="HEAT_DAYS", facet_col="YEAR", facet_col_wrap=4,
                      title="Monthly distribution")
        return fig
    
# model prediction
class prediction_table():
    def __init__(self,model):
        self.model = model
        
    def draw_table(self,data):
        ages = ['0-24', '25-44', '45-64', '65-74', '75-84', '85+']
        genders = ['F', 'M']
        data_ages = pd.DataFrame(list(product(ages, genders)), columns=['AGE-GROUP', 'SEX'])
        for key, val in data.items():
            data_ages[key] = val
        # Reorder the features
        data_ages = data_ages[['REGION', 'MONTH', 'YEAR', 'AGE-GROUP', 'SEX', 'COD', 'TEMP_MEAN', 'TEMP_RNG', 
                             'WS50M_MEAN', 'PRECTOT_MEAN', 'RH2M_MEAN', 'HEAT_DAYS']]
        # Dataframe for plotting
        output = pd.DataFrame()
        output['Gender'] = data_ages['SEX']
        output['Age groups'] = data_ages['AGE-GROUP']
        # Model prediction
        output['Predicted mortality'] = self.model.predict(data_ages)
        # Plot
        fig = px.bar(output, y='Age groups', x='Predicted mortality',
                     color='Gender', title='Mortality prediction', barmode='group', orientation='h')
        return fig