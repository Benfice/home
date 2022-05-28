from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup
import os
from smtplib import SMTP
from dotenv import load_dotenv

 # Take environment variables from .env.
load_dotenv()

# Get my email and password from environment variables
my_email = os.environ['MY_EMAIL']
my_email_password = os.environ['MY_EMAIL_PASSWORD']

# Get content for houses in Temerin cheaper than 110 000€ and bigger than 85m²
url = "https://sasomange.rs/c/kuce-prodaja/f/temerin?productsFacets.facets=priceValue:(*-110000),facility_area_range_house_sale:(85-*),"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

# Find all houses displayed in the page
# Chose the class "item-container" instead of "product-item" because too many repetition of the same houses with "product-item"
# homes = soup.find_all(class_="product-item")
homes = soup.find_all(class_="item-container")

# List of the new interesting houses
homes_list = []

# Today and yesterday dates
today = date.today()
yesterday = today - timedelta(days=1)

# For each home get the link of the ads and the start date
for home_container in homes:
    # Ads start date
    home = home_container.contents[1]
    start_date_raw = home.find(class_="start-date-content").get_text()
    start_date_split = start_date_raw.split()[0].split(".")
    start_date = date(year=int(start_date_split[2]), month=int(start_date_split[1]), day=int(start_date_split[0]))

    # Home link
    home_link = "https://sasomange.rs" + home.get('href')

    # Add houses if they are from today or yesterday
    # "home_link not in homes_list" is too avoid repetition
    if (start_date == today or start_date == yesterday) and home_link not in homes_list:
        homes_list.append(home_link)

# Send me by email the links of those houses
message = ""
for home_link in homes_list:
    message = message + home_link +"\n"

if homes_list:
    with SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(user=my_email, password=my_email_password)
        connection.sendmail(from_addr=my_email,
                            to_addrs="bfreuloncours@gmail.com",
                            msg=f"Subject:New interesting houses\n\n" + message)