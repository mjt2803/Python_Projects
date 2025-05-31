#import necessary packages
import numpy as np
import pandas as pd
import datetime as datetime
from itertools import islice
import math

#read CSV files into the program
game_data = pd.read_csv('Game.2024.csv')
team_data = pd.read_csv('Team.2024.csv')

#filter the dataframe to include only necessary columns
filtered1_data = game_data[['SeasonType', 'Status', 'Day', 'AwayTeamID', 'HomeTeamID', 'AwayTeamScore', 'HomeTeamScore']]

#filter the dataframe to include only regular season games and games that have been completed
filtered2_data = filtered1_data[filtered1_data['SeasonType']==1]
filtered3_data = filtered2_data[(filtered2_data['Status'] == 'Final') | (filtered2_data['Status'] == 'F/OT')]
filtered_data = filtered3_data

#create a dictionary of new ID's for teams so that there are no gaps in ID data
new_ids = {}
idcount = 0
for index, row in filtered_data.iterrows():
    if row['AwayTeamID'] not in new_ids.keys():
        new_ids[row['AwayTeamID']] = idcount
        idcount += 1
    if row['HomeTeamID'] not in new_ids.keys():
        new_ids[row['HomeTeamID']] = idcount
        idcount += 1

#modify the dataframe to incorporate new ID system
#this step responds to the problem of gaps in ID data that eventually leads to a singular matrix_MTM when populating matrix_M by team IDs
for index, row in filtered_data.iterrows():
    filtered_data.loc[index, 'AwayTeamID'] = new_ids[row['AwayTeamID']]
    filtered_data.loc[index, 'HomeTeamID'] = new_ids[row['HomeTeamID']]

#determine the number of columns of matrix M
max_awayteamid = filtered_data['AwayTeamID'].max()
max_hometeamid = filtered_data['HomeTeamID'].max()
def get_greater(a, b):
    if a >= b:
        return a
    else:
        return b
total_id = get_greater(max_awayteamid, max_hometeamid)+1

#determine the number of rows of matrix M
total_games = len(filtered_data)

#create a dictionary of new indices for each row so that there are no gaps in the dataframe index
#this step responds to the problem of gaps in index values for the dataframe filtered_data that eventually leads to an index-out-of-range error when populating matrix_M by dataframe index values
index_to_newindex = {}
indexcount = 0
for index, row in filtered_data.iterrows():
    index_to_newindex[index] = indexcount
    indexcount += 1

#form the matrix M from the previous dataframe using new indices
matrix_M = np.zeros((total_games, total_id))
for index, row in filtered_data.iterrows():
    if int(row['AwayTeamScore']) > int(row['HomeTeamScore']):
        matrix_M[index_to_newindex[index],int(row['AwayTeamID'])]=1
        matrix_M[index_to_newindex[index],int(row['HomeTeamID'])]=-1
    elif int(row['AwayTeamScore']) < int(row['HomeTeamScore']):
        matrix_M[index_to_newindex[index],int(row['AwayTeamID'])]=-1
        matrix_M[index_to_newindex[index],int(row['HomeTeamID'])]=1
    else:
        raise Exception("there is a game resulting in a tie")

#form vector d from the previous dataframe using new indices
vector_d = np.zeros((total_games, 1))
for index, row in filtered_data.iterrows():
    vector_d[index_to_newindex[index],0]=abs(int(row['AwayTeamScore'])-int(row['HomeTeamScore']))
    
#create a list of all game days during the season
date_list = []
for index, row in filtered_data.iterrows():
    if datetime.strptime(row['Day'], "%m/%d/%Y %H:%M:%S %p") not in date_list:
        date_list.append(datetime.strptime(row['Day'], "%m/%d/%Y %H:%M:%S %p"))

#find the first and last days of the season
max_date = max(date_list)
min_date = min(date_list)

#create a linear function that takes gameday as input and produces a time-in-season ratio as output
#add 0.01 to ensure matrix_MTWM is singular
def linear_function(game_date):
    datetime_game_date = datetime.strptime(game_date, "%m/%d/%Y %H:%M:%S %p")
    delta1 = datetime_game_date - min_date
    delta2 = max_date - min_date
    total_seconds_delta1 = delta1.total_seconds()
    total_seconds_delta2 = delta2.total_seconds()
    return (total_seconds_delta1 / total_seconds_delta2)+0.01

#form weighted linear_W from the previous dataframe using linear_function()
linear_W = np.zeros((total_games, total_games))
for index, row in filtered_data.iterrows():
    linear_W[index_to_newindex[index],index_to_newindex[index]]=linear_function(row['Day'])

#create an exponential function that takes a float as input and produces a float as output
def exponential_function(value):
    return math.exp(value)

#form weighted exponential_W from the previous dataframe using linear_function() called by the exponential_function()
exponential_W = np.zeros((total_games, total_games))
for index, row in filtered_data.iterrows():
    exponential_W[index_to_newindex[index],index_to_newindex[index]]=exponential_function(linear_function(row['Day']))
    
#create a logarithmic function that takes a float as input and produces a float as output
def logarithmic_function(value):
    return math.log(value+1)

#form weighted logarithmic_W from the previous dataframe using linear_function() called by the logarithmic_function()
logarithmic_W = np.zeros((total_games, total_games))
for index, row in filtered_data.iterrows():
    logarithmic_W[index_to_newindex[index],index_to_newindex[index]]=logarithmic_function(linear_function(row['Day']))
    
#form weighted stepfunction_W from the previous dataframe using linear_function() and defining a step function using for loops
stepfunction_W = np.zeros((total_games, total_games))
for index, row in filtered_data.iterrows():
    for number in range(1,12):
        if linear_function(row['Day']) <= (number/11):
            stepfunction_W[index_to_newindex[index],index_to_newindex[index]]=(number/11)
            break
        else:
            pass

#form matrix MTM by performing matrix operations
#option: edit the following matrix operations to include linear, exponential, logarithmic, or step function W for different weighting schemes
matrix_MTM = np.matmul(matrix_M.transpose(),matrix_M)

#form the Massey Matrix MTM by replacing the last row with 1s
list_of_ones = [1] * total_id
matrix_MTM[total_id-1] = list_of_ones

#form vector MTd by performing matrix operations
vector_MTd = np.matmul(matrix_M.transpose(),vector_d)

#form the adjusted vector MTd by replacing the last row with a 0
vector_MTd[total_id-1] = [0]

#calculate the inverse of Massey Matrix MTM
matrix_MTM_inverse = np.linalg.inv(matrix_MTM)

#multiply the inverse of Massey Matrix MTM with adjusted vector MTd
vector_final_ratings = np.matmul(matrix_MTM_inverse,vector_MTd)

#create a dictionary mapping old ID's to school names
id_to_school = {}
for index, row in team_data.iterrows():
    if row['TeamID'] not in id_to_school.keys():
        id_to_school[row['TeamID']] = row['School']

#recover ratings with the original school name and place school-rating pairs into a dictionary
def get_key_from_value(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key
    return None
team_ratings = {}
for index, value in enumerate(vector_final_ratings):
    team_ratings[id_to_school[get_key_from_value(new_ids, index)]] = value.item()

#alphabetize the dictionary by school name
alphabet_team_ratings = dict(sorted(team_ratings.items()))

#option 1: print the alphabetized final results to the output
#for key, value in sorted_team_ratings.items():
#    print(f"Team Name: {key}, Rating: {value}")

#sort the dictionary by rating highest -> lowest
hi_to_low_ratings = dict(sorted(team_ratings.items(), key=lambda item: item[1], reverse=True))

#option 2: print the top 100 final results from highest -> lowest to the output
for key, value in islice(hi_to_low_ratings.items(), 100):
    print(f"Team Name: {key}, Rating: {value}")