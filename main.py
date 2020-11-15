# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:25:53 2020

@author: Lukas
"""
# Required packages and functions

import pandas as pd

# custom classes
import vbl_webdriver
import vbl_api

# read all the teamguids for which we want to extract all the matchinfos in its series
with open("teamguids.txt") as f:
    own_teamguids = [line.rstrip() for line in f]
    
# Use our custom class to employ the VBL API and get the necessary info (guids & other details per match for all the matches in our team's series)
vbl_api = vbl_api.VblApi()
series_matchinfos = []

for own_teamguid in own_teamguids:
    series_teamguids = vbl_api.series_teamguids(own_teamguid) # get the teamguids
    series_matchinfos.append(vbl_api.series_matchinfos(series_teamguids)) # get the matchinfos using the teamguids
    
# login credentials
login = pd.read_csv("login.txt", sep = ": ", header = None, engine='python')
username = login[1][0]
password = login[1][1]

### Webdriver
# Call the webdriver class to generate a webdriver instance
website = vbl_webdriver.Webdriver()

# Login using login credentials
website.redirect_page("https://vblweb.wisseq.eu/Home/login") # go to login page
website.login(username, password)

# create lists to fill with all matchinfos of all series
dfs_points_players_all = []
dfs_points_quarters_all = []

for current_team_series in series_matchinfos:
    # Use our dictionary of matchguids to redirect to each page and download the data tables. Only get tables that have data in them (no unplayed games in the data).

    # list to fill with exported dataframes of selected series
    dfs_points_players = []
    dfs_points_quarters = []

    # Loop through each team in the series
    for teaminfo in [value for value in current_team_series.values()]:
        # Loop through each match per team
        for matchinfo in teaminfo:
            # Create url of our current match & redirect to that page
            url = "https://vblweb.wisseq.eu/Home/MatchDetail?wedguid=" + matchinfo[0] + "&ID=Uitslag"
            website.redirect_page(url)
            website.button_verslag()

            # Export the correct table on that page (thuis or uit)
            points_players, points_quarters_thuis, points_quarters_uit = website.export_verslag(matchinfo[1])

            # If list is not empty (= if match was played) then create dataframes of the data
            if points_players:       
                ## Points per players
                # Create dataframe
                df_points_players = pd.DataFrame(points_players, columns = ["nr","naam","starter","punten"])   
                df_points_players['ploeg'] = matchinfo[3]
                df_points_players['thuis/uit'] = matchinfo[1]
                df_points_players['matchguid'] = matchinfo[0]
                df_points_players['datum'] = matchinfo[2]
                 # Convert empty strings to 0's
                df_points_players['punten'] = pd.to_numeric(df_points_players['punten']).fillna(0)

                # Change dtypes in dataframe
                df_points_players = df_points_players.astype({'nr':'int32', 'naam':'string', 'starter':'string','punten':'int32','thuis/uit':'string','matchguid':'string'})

                 # Extra check to see if match was played; if all the players made 0 points we assume the match wasn't played
                if not all(df_points_players.punten.values == 0):
                    dfs_points_players.append(df_points_players)

                ## Points per quarters
                # Create dataframe
                df_points_quarters_thuis = pd.DataFrame(points_quarters_thuis, columns = {"periode","time_outs","fouten","punten"})
                df_points_quarters_uit = pd.DataFrame(points_quarters_uit, columns = {"periode","time_outs","fouten","punten"}) 

                # Put the correct info on the left of the dataframe to identify it as the teams info
                if matchinfo[1] == "thuis":
                    df_points_quarters = pd.concat([df_points_quarters_thuis, df_points_quarters_uit], axis = 1, ignore_index = True)
                elif matchinfo[1] == "uit":
                    df_points_quarters = pd.concat([df_points_quarters_uit, df_points_quarters_thuis], axis = 1, ignore_index = True)

                df_points_quarters.columns = ['periode','time_outs','fouten','punten','periode2','time_outs_tegen','fouten_tegen','punten_tegen']
                df_points_quarters.drop('periode2', axis = 1, inplace=True) # drop the second column with quarter_nrs    

                df_points_quarters['ploeg'] = matchinfo[3]
                df_points_quarters['thuis/uit'] = matchinfo[1]
                df_points_quarters['matchguid'] = matchinfo[0]
                df_points_quarters['datum'] = matchinfo[2]

                dfs_points_quarters.append(df_points_quarters)
    
    dfs_points_players_all.append(dfs_points_players)
    dfs_points_quarters_all.append(dfs_points_quarters)
