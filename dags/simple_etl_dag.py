import codecs
import csv
from contextlib import closing
from datetime import datetime

import requests
from airflow.decorators import dag, task


@dag(schedule=None, start_date=datetime(2022, 1, 1), catchup=False)
def simple_etl():

    @task
    def extract():
        url = 'https://data.bloomington.in.gov/dataset/117733fb-31cb-480a-8b30-fbf425a690cd/resource/8673744e-53f2' \
              '-42d1-9d05-4e412bd55c94/download/monroe-county-crash-data2003-to-2015.csv'
        with closing(requests.get(url, stream=True)) as response:
            reader = csv.DictReader(codecs.iterdecode(response.iter_lines(), encoding='windows-1252'), delimiter=',')
            return [row["Year"] for row in reader]

    @task(multiple_outputs=True)
    def transform(year_list: list):
        year_dict = {}
        for year in year_list:
            year_dict[year] = 0
        for year in year_list:
            year_dict[year] += 1
        return year_dict

    @task
    def load(year_dict: dict):
        for year, number_of_car_accidents in year_dict.items():
            print(f"Number of car accidents in {year} was: {number_of_car_accidents}")

    download_data = extract()
    count_number_of_accidents = transform(download_data)
    load(count_number_of_accidents)


simple_etl()
