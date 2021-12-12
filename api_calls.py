# Data API file
#
# UGA Fall 2021 - CSCI 4370
# Final Project: Election Statistics Database
# Authors: Abbie Thomas, Ayush Kumar, Faisal Hossain, Khemisha Brown, Sagar Asthana 
# Professor: Mario Guimaraes

#Import Modules
import requests 
import pandas as pd

# open /Applications/Python\ 3.7/Install\ Certificates.command

# ------ API functions ------
def get_results_by_county(sheet_number=2, year = 2016, month = 11, result_column="total_votes"): 
    """
    Uses api endpoint to get the total votes aggregated to the county level. 
    Parameters (all optional): 
    ------------------------------------------------
    year (default 2016) - the year of the election
    month (default 11) - the month of th election
    sheet_number (default 2) - the contest number of the election
    result_column (default total_votes) Options [election_day, provisional, absentee_by_mail, advance_in_person, total_votes]   
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"sheet_number": sheet_number, "year": year, "month": month, "result_column": result_column}
    response = requests.get(invoke_url + "/get_results", params=params)
    df = pd.read_json(response.text)
    
    return df

def get_turnout_by_county(year=2016, month=11, race=None, gender=None, age_grp=None): 
    """
    Uses api endpoint to the turnout by demographic with optional filtering by a single gender, 
    single race, and/or single age group. 
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"year": year, "month": month}
    if race: 
        params["race"] = race 
    if gender: 
        params["gender"] = gender
    if age_grp: 
        params["age_grp"] = age_grp

    response = requests.get(invoke_url + "/get_turnout", params=params)
    return pd.read_json(response.text)

def get_distribution(county_name="Fulton", year=2016, month=11, axis="age_grp", metric="voted"):
    """
    Uses api endpoint to get the distribution of the metric by the axis. 
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"county_name": county_name, "year": year, "month": month, "axis": axis, "metric": metric}
    response = requests.get(invoke_url + "/get_distribution", params=params)
    return pd.read_json(response.text)



# ------ Get data from API ------
results = get_results_by_county()
counties = results['county_name']

values = results['county_name']
contests = results['county_name']
years = ['2016']

FIPS_df = pd.read_csv("https://raw.githubusercontent.com/fhossain75/georgia-election-map/main/data/georgiaFIPS.csv")
countyResults = results
countyResults['winner'] = countyResults[['DONALD J. TRUMP', 'GARY JOHNSON', 'HILLARY CLINTON']].idxmax(axis=1)
countyResults.insert(0, "FIPS", FIPS_df["FIPS"])