import bs4 as soup
import sqlite3
import requests
import re
import matplotlib.pyplot as plt

def loader():
    # Setup the empty SQLite Database
    conn = sqlite3.connect("index.db")
    curs = conn.cursor()
    # Create classification table
    curs.execute('CREATE TABLE IF NOT EXISTS onions([index] INTEGER PRIMARY KEY, url VARCHAR, drugs INTEGER, weapons INTEGER, csea INTEGER, fraud INTEGER, cyber INTEGER, classification VARCHAR);')
    conn.commit()

    # Create availablility table
    curs.execute('CREATE TABLE IF NOT EXISTS available(available_count INTEGER, unavailable_count INTEGER);')
    conn.commit()

    # Check if there is a value in the table
    results = curs.execute('SELECT * FROM available;')
    conn.commit()
    for row in results:
        # There is a value inside the table
        break
    else:
        # The table is empty
        curs.execute('INSERT INTO available (available_count, unavailable_count) VALUES(0, 0);')
        conn.commit()
    conn.close()

loader()
global available_count
global unavailable_count
available_count = 0
unavailable_count = 0

def requesturl(url):
    global available_count
    global unavailable_count
    # Make sure to add http in front of url if it does not have it yet
    if not "http://" in url:
        url = "http://" + url

    # Initialise the proxies
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    # Request the page and make sure you get a positive response
    if requests.get(url,proxies=proxies).ok:
        available_count += 1
        return requests.get(url,proxies=proxies).text
    else:
        unavailable_count += 1
        return None

onion_regex = "((?:<cite>)(\w+).onion(?:</cite>))"

# Visit index site and download onion addresses:
print("Obtaining Onion Addresses from indexing site...")
try:
    Raw_Onion_List = requesturl("http://ahmia.fi/search/?q=")
    # We do not want to count the indexing site
    available_count -= 1
except Exception as e:
    print("Cannot connect to indexing site")
    Raw_Onion_List = str("No onions")

# Find onion addresses
Raw_Onion_List = re.findall(onion_regex, Raw_Onion_List)

# Clear up the addresses 
clear_onion = []
for tup in Raw_Onion_List:
    clear_onion.append(tup[0])

# strip <cite> tags
stripped_onions = []
for address in clear_onion:
    address = address.replace('<cite>', '')
    address = address.replace('</cite>', '')
    stripped_onions.append(address)

# Make sure there are no duplicates
stripped_onions = list(set(stripped_onions))

# Take first 5 addresses (reduce processing time for testing)
process = stripped_onions[0:30]
# scrape the onion site and get the html
def scrape(url):
    try:
        html = requesturl(url)
        if html != None:
            soupcontent = soup.BeautifulSoup(html, "lxml")
            return soupcontent.prettify()
    except Exception:
        pass

print("Scraping addresses...")
site_html = []
site_url = []
for url in process:
    if scrape(url) != None:
        site_html.append(scrape(url))
        # Since for every scrape I call the fucntion twice I must subract one available 
        available_count -= 1
        site_url.append(url)

# Input data into a sqlite database
def input_data(url, drugs, weapons, csea, fraud, cyber, biggest):
    conn = sqlite3.connect("index.db")
    curs = conn.cursor()
    query = "INSERT INTO onions (url, drugs, weapons, csea, fraud, cyber, classification) VALUES (?, ?, ?, ?, ?, ?, ?);"
    data = (url, drugs, weapons, csea, fraud, cyber, biggest)
    curs.execute(query, data)
    conn.commit()
    conn.close()

# Update the availability of the services
def input_av(av, unav):
    conn = sqlite3.connect("index.db")
    curs = conn.cursor()

    # Get values currently in available
    results = curs.execute("SELECT available_count, unavailable_count FROM available;")
    conn.commit()

    for row in results:
        ava = row[0]
        unava = row[1]
        break

    # Add current availability to newly found availablity
    av = av + ava
    unav = unav + unava

    # Update the database
    query = "UPDATE available SET available_count = ?, unavailable_count = ?;"
    data = (av, unav)
    curs.execute(query, data)
    conn.commit()
    conn.close()


# Keywords used to classify the services
print("Categorising...")
drugs = ["drugs", "ecstasy", "weed", "cocaine", "methamphetamine", "heroine", "valium", "xanax", "fentanyl", "acid", "lsd", "meth"]
weapons = ["gun", "guns", "weapon", "weapons", "glock", "ak-47", "m16", "m4", "ar-15", "uzi", "mac-10", "m1911", "ruger", "magnum", "desert eagle"]
csea = ["pedo", "pedophile", "child", "underage", "teenager", "teen", "hebephilia", "hebephile", "ephebophilia", "ephebophiles"]
fraud = ["credit card", "swindling", "bank account", "tax", "paypal", "accounts", "hacked card", "dumps", "credit card dump"]
cyber = ["ransomware", "hacking", "hacker", "trojan", "virus", "worm", "ddos", "malware", "rat", "botnet"]

# Initialise the count for classifications
drugs_count = 0
weapons_count = 0
csea_count = 0
fraud_count = 0
cyber_count = 0
index = 0
values = {"drugs" : 0, "weapons" : 0, "csea" : 0, "fraud" : 0, "cyber" : 0 }

for site in site_html:
    # Make sure the connection was successful and html aquired
    if type(site) is None:
        continue
    else:
        # Split each site into seperate words for processing
        words = site.split(" ")

    # Look for drugs
    for keyword in drugs:
        for word in words:
            if keyword in word.lower():
                drugs_count += 1
    # Look for weapons
    for keyword in weapons:
        for word in words:
            if keyword in word.lower():
                weapons_count += 1
    # Look for csea
    for keyword in csea:
        for word in words:
            if keyword in word.lower():
                csea_count += 1
    # Look for fraud
    for keyword in fraud:
        for word in words:
            if keyword in word.lower():
                fraud_count += 1
    # Look for cyber
    for keyword in cyber:
        for word in words:
            if keyword in word.lower():
                cyber_count += 1

    values["drugs"] = drugs_count
    values["weapons"] = weapons_count
    values["csea"] = csea_count
    values["fraud"] = fraud_count
    values["cyber"] = cyber_count

    # Check which content classification is most likely for which site 
    if all(value == 0 for value in values.values()):
        biggest = "Insufficient data"
    else:
        biggest = max(values, key=values.get)

    # input data into database
    input_data(site_url[index], drugs_count, weapons_count, csea_count, fraud_count, cyber_count, biggest)
    
    # Set count to 0 for every new site
    drugs_count = 0
    weapons_count = 0
    csea_count = 0
    fraud_count = 0
    cyber_count = 0
    index += 1 

# Input how many services are available 
input_av(available_count, unavailable_count)

print("Creating charts...")
# Set figure for both subplots (pie charts)
fig = plt.figure(figsize=(10,4), dpi=144)

# --- find the total in each category ---
conn = sqlite3.connect("index.db")
curs = conn.cursor()
result = curs.execute('SELECT * FROM onions;')
conn.commit()

drug_total = 0
weapon_total = 0
csea_total = 0
fraud_total = 0
cyber_total = 0
ins_total = 0

for row in result:
    if row[7] == "drugs":
        drug_total += 1
    elif row[7] == "weapons":
        weapon_total += 1
    elif row[7] == "csea":
        csea_total += 1
    elif row[7] == "fraud":
        fraud_total += 1
    elif row[7] == "cyber":
        cyber_total += 1
    elif row[7] == "Insufficient data":
        ins_total += 1

# parse results to display in chart
category = []
for key, value in values.items():
    category.append(key)
category.append("Insufficient data")

totals = [drug_total, weapon_total, csea_total, fraud_total, cyber_total, ins_total]

# color for each label
colors = ['r', 'y', 'g', 'b', 'c', 'm']

# Set axis and title for categorization pie chart
ax1 = fig.add_subplot(121)
ax1.set_title("Categorisation", pad = 20)

# Plot categorization pie chart
ax1.pie(totals, labels = category, colors=colors, 
        startangle=90, radius = 1.2, autopct = '%1.1f%%')

# --- Get availability ---
av_results = curs.execute('SELECT * FROM available;')
conn.commit()
for row in av_results:
    site_available = row[0]
    site_not_available = row[1]
    break

conn.close()

# Labels for chart
labels = ["available", "not available"]
# Values for chart
nums = [site_available, site_not_available]
# Colors for chart
colors2 = ['g', 'r']

# Set axis and title for availability pie chart
ax2 = fig.add_subplot(122)
ax2.set_title("Service Availability", pad = 20)

# Plot availability pie chart
ax2.pie(nums, labels = labels, colors=colors2, 
        startangle=90, radius = 1.2, autopct = '%1.1f%%')

# Display database contents into console
print("\nDATABASE CONTENTS: ")
conn = sqlite3.connect("index.db")
curs = conn.cursor()

result = curs.execute('SELECT * FROM onions;')
conn.commit()

for row in result:
    print(row)
conn.close()

# Show charts
plt.show()