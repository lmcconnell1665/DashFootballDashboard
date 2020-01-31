import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import datetime

# reading in data.frame
ratings_df = pd.read_csv("TV_Joined.csv")
team_colors = pd.read_csv("team_colors.csv")
team_colors = team_colors.set_index('Team').to_dict()
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
app.layout = html.Div([ #contains everything on page, necessary for styling like page background etc.
    
    # page header section
    html.Div([
        html.H1('College Football'), #Dashboard title
    ]), 
    
    #TV Viewers per team per year graph section
    html.Div([
        html.P([
                'Choose a Team:', #Dropdown instructions 
                #Team selection dropdown
                dcc.Dropdown(
                    id = 'First_Dropdown', 
                    options = teamNamesDict, 
                    multi = True, 
                    value = ['Tennessee'], 
                    style = { 'width':'400px', 'float':'right', 'display':'inline-block' } 
                ), 
                dcc.RadioItems( #Home, away, both selection button
                    id = 'home-away',
                    options = [ { 'label':i, 'value':i } for i in ['Home', 'Away', 'Both'] ],
                    value = 'Home',
                    labelStyle = { 'display':'inline-block', 'marginTop':25 }
                ), #closes RadioItem
            ] #closes list of items in html.P
            , style = { 'width':'600px', 'MarginTop':10, 'MarginLeft':5 }
        ), #closes html.P
        
        html.P([
            dcc.Graph(id = 'First_Graph') #TV attendance scatterplot
        ]),
        
        html.P([
                dcc.RangeSlider(
                    id = 'Year_Selection_Slider',
                    min = ratings_df.Date.min().year,
                    max = ratings_df.Date.max().year,
                    value = [ratings_df.Date.min().year, ratings_df.Date.max().year],
                    marks = { str(year): str(year) for year in ratings_df.Date.dt.year.unique() },
                    step = None
                ),           
            ],
            style = { 'width':'49%', 'marginTop':10, 'marignLeft':10}
        )
     
    ]) #closes TV Viewers per team per year graph section
    
]) # closes app.layout and the Section containing everything

#=============================================================================
# Create the callbacks here

@app.callback(
    Output(component_id = 'First_Graph', component_property = 'figure'),
    [Input(component_id = 'First_Dropdown', component_property = 'value'),
    Input(component_id = 'home-away', component_property = 'value'),
    Input(component_id = 'Year_Selection_Slider', component_property = 'value')]
)

def update_figure(teamX, Radio_Selection, Year_Selection):

    data = []
    for team in teamX:
        col = team_colors['Color'][team]
        if Radio_Selection == 'Home':
            Date = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                              (ratings_df['Date'].dt.year <= Year_Selection[1]) & 
                              (ratings_df['Home Team'] == team)]['Date']
            Viewers = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                                 (ratings_df['Date'].dt.year <= Year_Selection[1]) & 
                                 (ratings_df['Home Team'] == team)]['VIEWERS']
        elif Radio_Selection == 'Away':
            Date = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                              (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                              (ratings_df['Visitor Team'] == team)]['Date']
            Viewers = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                                 (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                                 (ratings_df['Visitor Team'] == team)]['VIEWERS']
        elif Radio_Selection == 'Both':
            Date = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) &
                              (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                              ((ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team))]["Date"]
            Viewers = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                                 (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                                 ((ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team))]["VIEWERS"]         
            
        data.append( dict(
                    type = "scatter",
                    mode = "markers",
                    x = Date,
                    y = Viewers,
                    name = team,
                    marker = dict(
                        color = col,
                        opacity = .6,
                        size = 7 ),
                    hovertext = ratings_df[(ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team)]["GAME"]
                    ) )
    layout = dict(
        title = 'TV Ratings by Team Over Time',
        showlegend=True,
        )
    fig = { 'data': data,
          'layout': layout
          }
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
    