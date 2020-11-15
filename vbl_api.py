# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 00:15:13 2020

@author: Lukas
"""
import requests
from datetime import date
from datetime import datetime

class VblApi:
    
    """
    This class employs functions that use the VBL API to extract matchcodes and teamcodes
    
    >>> vbl_api = VblApi()
    """

    def series_teamguids(self, own_teamguid):
        """
        Starts with a teamguid, find its series and returns a dictionary of all the teamnames and their teamguids
        
        :param own_teamguid: a teamguid to start the search, should be read from the "teamguids.txt" in the correct format
        :return: a dictionary of teamnames and their teamguids
        
        >>> vbl_api.series_teamguids('BVBL1117HSE++1')
        
        """
        # Create API url
        url_teamdetail = 'http://vblcb.wisseq.eu/VBLCB_WebService/data/TeamDetailByGuid?teamguid=' + own_teamguid
        series_teamguids = {}
        
        # FIll a dictionary with all the teamnames and their guids in the series. Clean up the guids to be able to use later.
        response = requests.get(url_teamdetail)
        
        try:
            for teamdetail in response.json()[0]['poules'][0]['teams']:
                series_teamguids[teamdetail['naam']] = teamdetail['guid'].replace(" ","+") # Teamname = key, teamguid = value. Replace spaces with '+' in key 

            series_teamguids = {key:val for key, val in series_teamguids.items()} # Copy the dictionary but remove our own teamguid
            return(series_teamguids)

        except:
            print('Invalid Response or Error: ' + str(response))
        
    def team_matchinfos(self, teamguid, teamname):
        """
        Starts with a teamguid to return a list with details of all the team's games before the current date 
        Details are: all the matchguids that are before the current date, whether the matches were 'thuis' or 'uit', the date of the match, & the name of the team
        
        :param teamguid: a teamguid for which we want all the matchinfos
        :param teamname: the teamname corresponding to the matchguid
        :return: a list with the matchguids, 'thuis' or 'uit', the dates, and the teamname
        
        >>> vbl_api.team_matchguids('BVBL1117HSE++1', 'Telstar B.B.C. Mechelen HSE B')
        """
        
        # Create API url
        url_teammatches = 'http://vblcb.wisseq.eu/VBLCB_WebService/data/TeamMatchesByGuid?teamguid=' + teamguid
        matchinfos = []
        today = date.today()
        
        # If the match was played (before today), create a list of lists with matchinfo for a specific team
        try:
            response = requests.get(url_teammatches)
            for teammatches in response.json():
                if datetime.strptime(teammatches['datumString'], "%d-%m-%Y").date() < today: # If matchday is before today, then append the matchguid to list
                    if teammatches['tTNaam'] == teamname:
                        matchinfos.append([teammatches['guid'], 'thuis', teammatches['datumString'], teamname])
                    if teammatches['tUNaam'] == teamname:
                        matchinfos.append([teammatches['guid'], 'uit', teammatches['datumString'], teamname])
            return(matchinfos)
        except:
            print('Invalid Response or Error: ' + str(response))

    def series_matchinfos(self, teamguids):
        """
        Uses the team_matchinfos function in a loop to return a dictionary of all teamnames in the series and all their matchguids before today
        
        :param teamguids: a dictionary of teamguids (keys) and the teamnames (values)
        :return: a dctionary of teamguids (keys) and a list of matchinfos before the current date (value)
        
        >>> vbl_api.series_matchinfos({'BC Cobras Schoten-Brasschaat HSE B': 'BVBL1277HSE++2',
                                       'Phantoms Basket Boom HSE B': 'BVBL1505HSE++2'})
        
        """
        series_matches = {}
        
        # Apply team_matchguids function to all the teams in the series to get a full dictionary of lists of all matchinfos for all teams
        for key, value in teamguids.items():
            series_matches[key] = self.team_matchinfos(value, key)
        return(series_matches)