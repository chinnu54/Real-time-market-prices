import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from datetime import datetime
import json

app = FastAPI()

def get_today_date():
    today = datetime.today()
    formatted_date = today.strftime("%d-%b-%Y")
    return formatted_date

@app.get('/{state}/{crop}')
def get_market_prices(state: str, crop: str):
    # Get today's date for the URL
    today_date = get_today_date()
    with open('crops.json','r') as File:
        crops_revised =json.load(File) 
    with open('states.json', 'r') as file:
        states = json.load(file)
    # states = 

    # Construct the URL based on the input parameters
    url = f"https://www.napanta.com/agri-commodity-prices/{states[state]}/{crops_revised[crop]}/{today_date}"

    # Make the request to the website
    response = requests.get(url)
    
    # Check if the response was successful
    if response.status_code != 200:
        return {'message': "Failed to fetch data from the website. Please try again later."}

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html5lib')

    # Define the properties to search for the table
    properties = {
        "id": "tablepaging",
        "class": "yui",
        "align": "center",
    }

    # Find all tables with the specified properties
    raw_data = soup.find_all('table', properties)

    # If no tables are found, return an error message
    if len(raw_data) < 1:
        return {'message': "Internal server error: No data found."}

    # Select the first table from the raw_data
    data = raw_data[0]

    # Retrieve all rows from the table
    rows = data.find_all('tr')

    # Initialize an empty list to store the prices
    prices_list = []

    # Iterate over the rows (skipping the first row as it contains headers)
    for row in rows[1:]:
        cols = row.find_all('td')

        # Check if the row has exactly 9 columns (ensure correct structure)
        if len(cols) == 9:
            try:
                # Debug: Print the values in cols
                print("Cols:", [col.text.strip() for col in cols])

                # Extract the required data
                district = cols[0].text.strip()
                market = cols[1].text.strip()
                commodity = cols[2].text.strip()
                variety = cols[3].text.strip()

                # Check the content of these columns before parsing
                max_price_str = cols[4].text.strip()
                min_price_str = cols[6].text.strip()
                avg_price_str = cols[5].text.strip()

                print("Max Price String:", max_price_str)
                print("Min Price String:", min_price_str)
                print("Avg Price String:", avg_price_str)

                # Convert the price strings to integers if they are valid numbers
                # maximum_price = int(max_price_str) if max_price_str.isdigit() else None
                # minimum_price = int(min_price_str) if min_price_str.isdigit() else None
                # average_price = int(avg_price_str) if avg_price_str.isdigit() else None
                maximum_price=max_price_str
                minimum_price=min_price_str
                average_price=avg_price_str

            except ValueError as e:
                print(f"Error parsing row: {row}")
                return {"message": "Data parsing error. Please try again later."}
            
            # Append the parsed data to the prices_list
            prices_list.append({
                "District": district,
                "Market": market,
                "Variety": variety,
                "Commodity/crop": commodity,
                "Maximum Price": maximum_price,
                "Average Price": average_price,
                "Minimum Price": minimum_price
            })
        else:
            # Skip rows that don't have 9 columns (malformed rows)
            continue

    # If no data was found in the table, return an error message
    if not prices_list:
        return {'message': "No market prices available for the selected crop and state."}

    # Return the prices list as a response
    return prices_list
