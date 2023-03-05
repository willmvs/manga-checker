import csv
import os
import random
import requests
import time
from bs4 import BeautifulSoup

# Author: https://github.com/willmvs
# Goal: find the status (Complete/Cancelled/Ongoing) of a given list of mangas.
# Script based on the mangaupdates.com website, and the public view of each manga page.
# If it breaks, check their HTML for any changes and adjust the script.
# In this first version the script relies on a text file containing links to each
# manga page. One link by line. Example:
# https://www.mangaupdates.com/series/axmopy6/jujutsu-kaisen
# https://www.mangaupdates.com/series/stwyptc/nanatsu-no-taizai
# You can create your own list of mangas on mangaupdates.com and later copy the links
# from the My Lists page using a browser extension, like Copy Selected Links (Chrome). 
# TODO add the option to read the My Lists page instead of an input file.

# TODO use dictionaries instead of lists
# Initialize the lists for each status
list_complete = []
list_cancelled = []
list_ongoing = []

# Use path split to find the current path from where the script is running, 
# same folder where we store the input and output files
filepath, filename = os.path.split(__file__)

# Open file for read (default)
with open(filepath+'\\manga_links.txt',encoding='utf8') as manga_links:
    # Read file adding each line as an item on a list
    input_lines = manga_links.readlines()

    # TODO crosscheck input file against a list of complete/cancelled so we avoid
    # checking the same complete/cancelled manga each time the script is run

    # Print for reference
    total_mangas = len(input_lines)
    print("Number of mangas in the input file: ", total_mangas)
    print("Processing started...")

    # Check if the csv file exists and if not, add the header line. #TODO improve this
    csv_exists = os.path.exists(filepath+'\\completed_cancelled.csv')
    if not csv_exists:
        with open('completed_cancelled.csv', 'a', newline='') as f:
            writer = csv.writer(f, dialect='excel-tab')
            writer.writerow(["Status", "Manga name", "Latest Release"])

    # Open the CSV file for writing / appending.
    with open('completed_cancelled.csv', 'a', newline='') as f:
        # Define writer for the CSV file, indicating it should use Excel's TAB
        # since some manga names might have commas and they could cause issues
        writer = csv.writer(f, dialect='excel-tab')

        count = 0 

        for URL in input_lines:
            # Example = "https://www.mangaupdates.com/series/7z3yqqk/naruto"
            # Use requests and BeautifulSoup to parse the page HTML source
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, "html.parser")

            # Obtain the manga title from the page title. 
            # Example: 'Naruto - Baka-Updates Manga'
            # Strip leading/trailing whitespaces and remove the Baka part
            for title in soup.find_all('title'):
                full_title = title.get_text().strip()
                baka_position = full_title.rfind(" - Baka")
                manga_name = full_title[:baka_position]

            # Find the main_content div
            main_content = soup.find(id="main_content")
            # Find all the sContent divs within main_content
            scontents = main_content.find_all("div", class_="sContent")
            
            # Item [5] usually contains the "Latest Release(s)" section, which might have multiple lines
            # Example: c.700 by MANGA Plus over 2 years ago
            latest_release = scontents[5].get_text()
            # I only care about the first line and the c.xxx chapter number, so using split to grab that (hopefully)
            latest_release = latest_release.split()[0]

            # Item [6] usually contains the "Status in Country of Origin" section, mentioning
            # if the manga is (Ongoing), (Complete), or (Cancelled). 
            # TODO IndexError with scontents empty = server error.
            status = scontents[6].get_text()

            # TODO List how many chapters I'm away from the latest released.
            # Check if these strings are found before starting. -1 = not found 
            complete = status.find("Complete")
            cancelled = status.find("Cancelled")
            ongoing = status.find("Ongoing")

            # Check if the status were found and add to the appropriate list
            # Trying to cover edge cases in which the status can have both ongoing and complete/cancelled,
            #  by checking for Ongoing first. Example: https://www.mangaupdates.com/series/ylx5wzn/chainsaw-man
            if ongoing > -1:
                list_ongoing.append(manga_name)
                writer.writerow(["Ongoing", manga_name, latest_release])
            elif complete > -1:
                list_complete.append(manga_name)
                writer.writerow(["Complete", manga_name, latest_release])
            elif cancelled > -1:
                list_complete.append(manga_name)
                writer.writerow(["Cancelled", manga_name, latest_release])
            else:
                # Covers Hiatus and other statuses
                list_ongoing.append(manga_name)
                writer.writerow(["Ongoing", manga_name, latest_release])


            # Print something just for a visual representation that the script is progressing
            count = count + 1
            print("/"*(total_mangas-count))

            # Wait a few seconds before trying the next manga to avoid overloading the server.
            wait_seconds = random.randint(5, 15)
            time.sleep(wait_seconds)

# Print the lists just for comparison with the .csv file
for item in sorted(list_complete):
    print("Status: Complete -", item)
    # TODO remove complete and cancelled mangas from the manga_links.txt, so the next run can be faster
    
for item in sorted(list_cancelled):
    print("Status: Cancelled -", item)

for item in sorted(list_ongoing):
    print("Status: Ongoing  -", item)
