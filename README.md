# Live football predictions

Show real-time predictions of football matches based on betting data


## Introduction

The goal of this project is to create a live win probability based on betting odds from the internet, as well as to show its change over time as the game progresses.


## Results (sped-up):

![scotlland-ukraine](https://user-images.githubusercontent.com/66125885/191607369-4d0ac535-c1a8-456a-bc71-68b9663c0fdf.gif)

![monza-juve-300s](https://user-images.githubusercontent.com/66125885/191607379-76db6946-6319-4b04-b796-34011de525a6.gif)



## Pipeline

![download](https://user-images.githubusercontent.com/66125885/190826735-e5c9c31b-4aaa-4a1e-b01f-772d4b759c4c.jpeg)

1. Match data is scraped with selenium, using the [undetected  chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) to avoid CloudFlare's restrictions
2. Data is pushed to a pub/sub topic, this has a few advantages:
    - Decoupling: Avoid writing a connector for earch sink, ability to replay the data.
    - Scaling: Distributed computing and a queque in case I push thousands of record per second
3. A BigQuery suscription consumes the data
    - Data is stored in a table partitioned by date
4. A transformation is done in SQL, transforming betting odds into an implied probability, and storing the results in a view
5. Live plotting using python and the library plotly deployed in Compute Engine queries the view from BigQuery


## Set-up instructions

1. Install the dependencies
```
pip install -r requirements.txt
```

2. Create the cloud resources 
Change the project name, authenticate and run
```
terraform init
```
```
terraform apply
```

3. Set the enviromental variables with the team names
```
export TEAM1="scotland"
```

```
export TEAM2="ukraine"
```

4. Run the main script
```
python scrap.py
```



