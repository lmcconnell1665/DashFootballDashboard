import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime

# reading in data.frame
ratings_df = pd.read_csv("TV_Ratings_onesheet.csv")

# Makes the date column a column of dates
ratings_df.Date = pd.to_datetime(ratings_df.Date)

# Drops some silly columns
ratings_df.drop(columns = ["GameID", "TeamIDsDate"])

# Sorting the df makes the plots turn out nicer in the case you want to use lines.
ratings_df = ratings_df.sort_values(by = "Date")

# Dropping old games.
currentGames = [x.year > 2010 for x in ratings_df.Date]
ratings_df = ratings_df.loc[currentGames]

# Getting the list of unique Home Team names
teamNames = ratings_df["Home Team"].unique()

# Creating an object for "options" in the dropdown menu.
teamNamesDict = [{'label' : tn, 'value': tn} for tn in teamNames]

#Adding external stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Create the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create the layout
app.layout = html.Div(
    # children =
    [html.H1('College Football'), #Dashboard title
     html.P(['Choose a Team.', #Dropdown instructions
            dcc.Dropdown(id='First_Dropdown', options=teamNamesDict, multi=True, value=['Tennessee'] ) ] #Team selection dropdown
            , style={'width':'400px'}),
     dcc.Graph( id = 'First_Graph'), #TV attendance scatterplot
     dcc.RadioItems( #Home, away, both selection button
            id='home-away',
            options=[{'label': i, 'value': i} for i in ['Home', 'Away', 'Both']],
            value='Home',
            labelStyle={'display': 'inline-block'}
        ) #closes RadioItem
     
    ] # Closes out the children of outermost html.Div of app.layout
) # closes app.layout outermost html.Div 

# Create the callbacks here

@app.callback(
    Output(component_id='First_Graph', component_property='figure'),
    [Input(component_id='First_Dropdown', component_property='value'),
    Input(component_id='home-away', component_property='value')]
)

def update_figure(teamX, Radio_Selection):

    data = []
    for team in teamX:
        if Radio_Selection == 'Home':
            Date = ratings_df[(ratings_df["Home Team"] == team)]['Date']
            Viewers = ratings_df[(ratings_df["Home Team"] == team)]['VIEWERS']
        elif Radio_Selection == 'Away':
            Date = ratings_df[(ratings_df["Visitor Team"] == team)]['Date']
            Viewers = ratings_df[(ratings_df["Visitor Team"] == team)]['VIEWERS']
        elif Radio_Selection == 'Both':
            Date = ratings_df[(ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team)]["Date"]
            Viewers = ratings_df[(ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team)]["VIEWERS"]         
            
        data.append( dict(
                    type = "scatter",
                    mode = "markers",
                    x = Date,
                    y = Viewers,
                    name = team,
                    marker = dict(
                        color = 'rgb(0,0,0)',
                        opacity = .6,
                        size = 7 ),
                    hovertext = ratings_df[(ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team)]["GAME"]
                    ) )
    
    fig = { 'data': data}
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
    

    
# can you pull branch