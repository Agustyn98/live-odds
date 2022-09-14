# Live football predictions

Show real-time predictions of football matches based on betting data


## Introduction

This goal of this project is to show live prediction based on betting odds from the internet, as well as to show its change over time.


## Results:

-- Gif/Video demostration 1 --

-- Gif/Video demostration 2 --


## Pipeline

<img src="https://user-images.githubusercontent.com/66125885/190246413-ce2cfa0e-b479-40d3-b739-a1d21bd88540.png" width=50% height=50%>


1. Match data is scraped with selenium, using the [undetected  chromedriver]("https://github.com/ultrafunkamsterdam/undetected-chromedriver") to avoid CloudFlare's restrictions
2. Data is pushed to a pub/sub topic
3. A BigQuery suscription consumes the data
4. Live plotting using python and the library plotly deployed in Compute Engine consumes data from BigQuery
