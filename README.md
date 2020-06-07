# Tweet Analyser
A multi-threaded Python based forensics tool used to parse dumped Twitter JSON data to quickly identify crime via OSINT.
![Screenshot of Tweet Analyser displaying random tweets on import.](https://i.imgur.com/IxUcrhi.jpg)

## Features

 - Simple GUI
 - REGEX based searching
 - Predetermined template searching for crimes
 - Map export (Heat map & Plotted map)
 - GeoLocation display

## What is this?
Tweet Analyser is a python based tool to quickly and efficiently index and search through a large collection of tweets from a JSON dump. It extracts relevant information to display to the user, and allows term based and REGEX based searching through the tweets in order to improve investigation time. The program also has the capability to export heatmaps using GEOJSON data and Folium to identify hotspots.

## Requirements
Tweet Analyser requires the following libraries:

 - folium
 - pandas
 - numpy
 
To install, simply use pip, or download the requirements.txt from the repo and run

```bash
python -m pip install -r requirements.txt
```

## How to install
Either download the repo via a zip, or clone using git.
```bash
wget https://github.com/TikvahTerminator/TweetAnalyser/archive/master.zip
```
or

```bash
git clone https://github.com/TikvahTerminator/TweetAnalyser.git
```
## How to use
The program uses a rather basic GUI. 

 1. Once launched, open a twitter JSON file (Try to limit it to around 5000 tweets otherwise tkinter starts to get sad!) 
 2. Use the search bar to search for strings or REGEX or Use a predetermined template to look for crimes.
 3. Read tweets and investigate!

*To export a map, simply choose a map via the dropdown menu, and click export!*

## Maps
![A geojson HeatMap created by Tweet Analyser](https://i.imgur.com/cqBxHIO.jpg)Tweet Analyser uses Folium to create maps. There's two modes:
### Plot Maps
Plot maps just plot the tweets onto the map at their geographical location along with data about the tweet.
### Heat Maps
Heat maps use GeoJSON data to assign a density to a administrative ward, and marks how many tweets are within an area; allowing investigators to find hotspots for crime.
**NOTE**: To use this function, you MUST place wards.json from [Martinjc's UK-geoJSON](https://github.com/martinjc/UK-GeoJSON/blob/master/json/electoral/eng/wards.json) repo into the same working directory as the Tweet Analyser.

## Thanks
Thank you to [Majdi Owda](https://www.linkedin.com/in/majdi-owda-65b1156) & Dr [Robert Hegarty](https://www.linkedin.com/in/robert-hegarty-320a7180) of Manchester Metropolitan University for their help during development!
