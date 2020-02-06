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
    
    # page header
    html.Div([
        html.Div([
            html.H2('College Football TV Influence'), #Dashboard title
        ], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'}), #closes title html.Div
        
        html.Div([
            html.Img(
                src = app.get_asset_url('NCAA_logo.png'),
                id = 'logo',
                style = {'height': 100, 'width': 'auto'}
            ) #closes Html.Img
        ], style={'width': '49%', 'display': 'inline-block', 'textAlign': 'right', 'margin-bottom': 10}) #closes logo html.Div
    ]), #closes header html.Div
    
    # option selector section
    html.Div([
        html.P([
                html.Div([
                'Choose a Team:', #Dropdown instructions 
                #Team selection dropdown
                dcc.Dropdown(
                    id = 'First_Dropdown', 
                    options = teamNamesDict, 
                    multi = True, 
                    value = ['Tennessee']
                ) ], style={'width': '49%', 'display': 'inline-block', 'marginBottom': 20}), #closes html.Div
            
                html.Div([
                #Year range selector
                'Choose a Year Range:',
                dcc.RangeSlider(
                    id = 'Year_Selection_Slider',
                    min = ratings_df.Date.min().year,
                    max = ratings_df.Date.max().year,
                    value = [ratings_df.Date.min().year, ratings_df.Date.max().year],
                    marks = { str(year): str(year) for year in ratings_df.Date.dt.year.unique() },
                    step = None
                ) ], style={'width': '49%', 'display': 'inline-block'}), #closes html.Div
            
                html.Div([
                'Select an Option Below:',
                #Home, away, or both radio selection
                dcc.RadioItems(
                    id = 'home-away',
                    options = [ { 'label':i, 'value':i } for i in ['Home', 'Away', 'Both'] ],
                    value = 'Home',
                    labelStyle = { 'display': 'inline-block'}
                )], style={'width': '49%', 'display': 'inline-block'}) #closes html.Div

            ] #closes list of user selection items in html.P
            ) #closes html.P
    ]), #closes html.Div
    
    #Graph section
    html.Div([  
        #TV Viewers per team per year graph section
        html.Div([
            dcc.Graph(id = 'First_Graph') #TV attendance scatterplot
        ], style={'width': '49%', 'display': 'inline-block'}), #closes html.Div
        
        #Second graph
        html.Div([
            dcc.Graph(id = 'Second_Graph') #Average stadium attendance year by year
        ], style={'width': '49%', 'display': 'inline-block'}) #closes html.Div
     
    ]) #closes the graph section
]) #closes the layout section

#=============================================================================
# Create the callbacks here

#First graph callback
@app.callback(
    Output(component_id = 'First_Graph', component_property = 'figure'),
    [Input(component_id = 'First_Dropdown', component_property = 'value'),
    Input(component_id = 'home-away', component_property = 'value'),
    Input(component_id = 'Year_Selection_Slider', component_property = 'value')]
)

def update_figure1(teamX, Radio_Selection, Year_Selection):

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
        title = 'TV Viewers by Team Over Time',
        xaxis = {'title': 'Date'},
        yaxis = {'title': 'Number of Viewers'},
        showlegend=True,
        )
    fig = { 'data': data,
          'layout': layout
          }
    
    return fig

#Second graph callback
@app.callback(
    Output(component_id = 'Second_Graph', component_property = 'figure'),
    [Input(component_id = 'First_Dropdown', component_property = 'value'),
    Input(component_id = 'home-away', component_property = 'value'),
    Input(component_id = 'Year_Selection_Slider', component_property = 'value')]
)

def update_figure2(teamX, Radio_Selection, Year_Selection):

    data = []
    for team in teamX:
        col = team_colors['Color'][team]
        if Radio_Selection == 'Home':
            Date = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                              (ratings_df['Date'].dt.year <= Year_Selection[1]) & 
                              (ratings_df['Home Team'] == team)]['Date']
            Viewers = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                                 (ratings_df['Date'].dt.year <= Year_Selection[1]) & 
                                 (ratings_df['Home Team'] == team)]['score_home']
        elif Radio_Selection == 'Away':
            Date = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                              (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                              (ratings_df['Visitor Team'] == team)]['Date']
            Viewers = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                                 (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                                 (ratings_df['Visitor Team'] == team)]['score_home']
        elif Radio_Selection == 'Both':
            Date = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) &
                              (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                              ((ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team))]["Date"]
            Viewers = ratings_df[(ratings_df['Date'].dt.year >= Year_Selection[0]) & 
                                 (ratings_df['Date'].dt.year <= Year_Selection[1]) &
                                 ((ratings_df["Home Team"] == team) | (ratings_df["Visitor Team"] == team))]["score_home"]         
            
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
        title = 'TV Viewers by Total Home Team Score',
        xaxis = {'title': 'Date'},
        yaxis = {'title': 'Home Team Final Score'},
        showlegend=True,
        )
    fig = { 'data': data,
          'layout': layout
          }
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
    