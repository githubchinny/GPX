#!/usr/bin/env python
# coding: utf-8

# # GPX HeatMap 
# 
# This will read all the gpx files within a directory, read the track_points and use them to make a heatmap.
# 
# ![HeatMap output](HeatMapOutput.png "HeatMap Output")
# 
# Prior to using this, download your gpx files to a local location.  Make sure your activitiesDir path matches your local location.  If taking lots of files from GarminConnect use https://github.com/pe-st/garmin-connect-export
# This notebook then reads the gpx files, opens each file into a GeoPandas DataFrame and appends the contents to a GeoDataFrame to hold all the points.
# We then find the centre of all the points to centralise the map on opening
# Create HeatMap data by reading in the appended GeoDataFrame line by line and produce the map
# 
# Set up some libraries

# In[ ]:


import numpy as np
import pandas as pd
import os
import subprocess
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from shapely.geometry import Point
from folium import Choropleth, Marker
import argparse

#----------------------------------------------------------------------------+
# process arguments
#----------------------------------------------------------------------------+
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename",default='ALL',
                    help="name of nmon file to process")
parser.add_argument("-d", "--days",default=45,
                    help="number of days in the past to use in file searches")
args = parser.parse_args()




# Activities directory
#activitiesDir used when filename not passed
activitiesDir = "/media/psf/Home/Documents/GitHub/GPX/MyActivities"


# Set up a function to show the map and save the html file

# In[2]:


def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')


# Make sure we've got the latest files downloaded

# read in track_points from the gpx file into a GeoPandas dataframe

# In[4]:


#build find command to search mypath directory for directories changed in past 45 days | sort 
#findCMD = ("find " + mypath + " -name \"*.nmon\" -ctime -45 -type f | grep -v xlsx | sort")

if args.filename != 'ALL':  
    print ("Finding all files containing {} changed in past {} days.  Change this by running script with -d parameter.".format(args.filename, args.days))
    findCMD = ("find " + activitiesDir + " -name " +args.filename+ "\"*gpx\" -ctime -" +str(args.days) +" -type f | sort")
else: 
    print ("Finding {} files changed in past {} days.  Change this by running script with -d parameter.".format(args.filename, args.days))
    findCMD = ("find " + activitiesDir + " -name \"*gpx\" -ctime -" +str(args.days) +" -type f | sort")

#pass findCMD into Popen process which will run the command
out = subprocess.Popen(findCMD,shell=True,stdin=subprocess.PIPE, 
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# Get standard out and error
(stdout, stderr) = out.communicate()
 
# Save found files to list
filelist = stdout.decode().split()

#loop around filelist, writing out an index for each file
for index, file in enumerate(filelist):

  #print the index and file for selection
  print (index, file)

target=int(input("Select a file to process:")) # assumes user clever enough to give an integer


gdf = []

# initialise an empty dataframe called gdf_all
gdf_all = gpd.GeoDataFrame()

# loop through the files in filelist
for file in (filelist):
        
#   Doing this in 2 steps as reading in and appending in one go didn't seem to work
    gdf = gpd.read_file(file, layer='track_points')
    gdf_all = gdf_all.append(gdf)
        
# This finds the centre lat and lon of the whole geodataframe, which I use to centre the map on opening        
start_lon = gdf_all.unary_union.centroid.x
start_lat = gdf_all.unary_union.centroid.y


# In[5]:


def add_markers(mapobj, gdf):
    heat_data = [[row.geometry.y,row.geometry.x] for index, row in gdf.iterrows()]
    HeatMap(data=heat_data, radius=12).add_to(mapobj)
    
# f = folium.Figure(height = 400)
m = folium.Map([start_lat, start_lon], zoom_start = 9)
# m.add_to(f)

# this calls the add_markers function
add_markers(m, gdf_all)

embed_map(m, "HeatMap.html")


# In[ ]:




