
# coding: utf-8

# # What movie for a user who saw "Inferno" from R. Howard ?

# *[Based on the MovieLens dataset](https://grouplens.org/datasets/movielens/)*
# 
# *by Quentin Vajou*
# 
# *March 2017*
# 
# ---
# 
# ## Content
# 
# 
#  1. Business Understanding (5 min)
#      * Objective
#      * Description
#  2. Data Understanding (45 min)
#     * Libraries, Data & Function Definition
#     * Data Visualization
#  3. Data Preparation (1h15 min)
#     * Basic Preparation
#     * Feature Engineering
#  4. Modeling Answer (1h30 min)
#     * Generate & Assemble Data
#     * Answer

# ## 1. Business Understanding

# ### 1.1 Objective

# What do you propose to someone who has just been to see Inferno, by Ron Howard?

# ### 1.2 Description

# You are hired by a young Parisian cinema, which offers its members movies in VOD (over a year old), according to the movies they came to see in the week.

# ## 2. Data Understanding

#  ### 2.1 Libraries, Data & Function Definition

# #### Import libraries

# In[1]:

#Handle table-like data and matrices
import numpy as np
import pandas as pd
from itertools import *

import requests, json


# #### Import data

# In[2]:

#import all data from db
genome_scores = pd.read_csv("genome-scores.csv")
genome_tags = pd.read_csv("genome-tags.csv")
links = pd.read_csv("links.csv")
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")
tags = pd.read_csv("tags.csv")


# #### Setup helper functions

# In[3]:

def split_cat_genres(list_genres):
    movies_same_cat = pd.DataFrame()
    movies_other_cat = pd.DataFrame()
    for index, row in islice(movies.iterrows(), 0, None):
        cat1 = pd.Series(list(movies.genres.iloc[index])).isin(list_genres)
        if np.sum(cat1) <= len(list_genres) & np.sum(cat1) >= int(len(list_genres)/2)+1:
            movies_same_cat = movies_same_cat.append(row, ignore_index=True)
        else:
            movies_other_cat = movies_other_cat.append(row, ignore_index=True)
    return movies_same_cat, movies_other_cat

def get_genres_from_omdb(title, year):
    r = requests.get('http://www.omdbapi.com/?t=' + str(title) + '&y=' + str(year))
    movie_dict = json.loads(r.text)
    movie_seen = pd.DataFrame.from_records([movie_dict])
    list_genres_auto = [x.strip() for x in movie_seen.Genre[0].split(',')]
    return list_genres_auto


# ### 2.2 Data Visualization

# In[4]:

#Discover data
print("genome_scores : \n", genome_scores.head())
print("genome_tags : \n", genome_tags.head())
print("links : \n", links.head())
print("movies : \n", movies.head())
print("ratings : \n", ratings.head())
print("tags : \n", tags.head())


# In[5]:

movies[movies['title'].str.contains("Inferno")==True]


# Inferno from Ron Howard doesnt seem to be in the database. To propose the user another movie to watch, I must be able to compare Inferno with other movies. From the observation of the data it seems that tags and genres are redundant information. So I need to get the genre of the movie to advise properly my user

# ## 3. Data Preparation

# ### 3.1 Basic Preparation

# In[6]:

# Generate list in place of string for genres
movies["genres"] = pd.DataFrame(movies.genres.str.split('|'))

# Extract release date from title
movies['release_date'] = movies['title'].str.replace(r'[^(]*\(|\)[^)]*', '')
#movies['release_date'] = movies['title'].str.extract(r'(^\d[0-9]{4,4}$)')
movies['release_date'] = pd.to_numeric(movies.release_date, errors='coerce')


# ### 3.2 Feature Engineering

# #### Fast Answer
# 
# If the context suggests that I must find a solution as soon as possible I would proceed this way :
# I'd go to imdb.com and find in what genres the movie "Inferno" is clustered:
# 
# Genres | 
# ---|---
#  |Action|Adventure|Crime|Drama|Mystery|Thriller

# In[7]:

#List entered manually
list_genres = ["Action", "Adventure", "Crime", "Drama", "Mystery", "Thriller"]
print(list_genres)


# #### Automated answer
# On the other hand, if the context suggest that we would have to reproduce the experience or integrate this process automatically, I would proceed that way:
# 
# I'd use the omdb API to retrieve the "genre" information having 2 input (title & release year)

# In[8]:

movie_seen_title = 'inferno'
movie_seen_year = '2016'

list_genres = get_genres_from_omdb(movie_seen_title, movie_seen_year)
print(list_genres)


# ## 4. Modeling Answer

# ### 4.1 Generate & Assemble Data

# Then I would split the movies into 2 categories:
# 
# * Those with the same genres (at least half of the genres from the movie seen are shared by the other movies in that categorie).
# 
# * Those with different genres
# 
# I'd make 2 propositions to my customer who just watched Inferno:
# 
# Movie liked | Movie not liked
# ---|---
# same genres categorie|other genres categorie
# 
# 
# 
# To do so I would rank the movies with the average rating users gave them. Then I would split the movies into the 2 categories we discussed and sort them from best average rating to worst and from most recent date of release to older ones.
# 
# So let's get and average rating for each movie and then split movies into 2 categories:
# 
# * movie_same_cat => movies sharing same genres
# * movies_other_cat => movies with other genres

# In[9]:

# Get average movie rating
movies['avg_rating'] = pd.Series(ratings.groupby('movieId').rating.mean().reset_index(level=0, drop=True))

# Split the movies DataFrame into 2 categories
movies_same_cat, movies_other_cat = split_cat_genres(list_genres)

# Sort by average rating and release date
movies_same_genres = movies_same_cat.sort_values(['avg_rating', 'release_date'], ascending=False)
movies_other_genres = movies_other_cat.sort_values(['avg_rating', 'release_date'], ascending=False)


# ### 4.2 Answer

# In[10]:

print("If you liked Inferno, we advise you to watch : ", movies_same_genres.title.iloc[0])
print("If you did not like Inferno, we advise you to watch : ", movies_other_genres.title.iloc[0])

