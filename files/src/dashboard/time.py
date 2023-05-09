import json
from datetime import datetime

# Load the JSON data from a file
#with open('mydata.json', 'r') as f:
#    data = json.load(f)

# Generate a dictionary with the data
data_dict = {
    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}

# Write the dictionary to a file in JSON format
with open('./docs/_images/forecast/mydata_dict.json', 'w') as f:
    json.dump(data_dict, f)
