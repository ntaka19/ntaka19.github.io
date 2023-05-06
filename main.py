import datetime
import os

if not os.path.exists('data'):
    print("error")

# Get the current date and time
now = datetime.datetime.now()

# Open the file in write mode
with open("./data/sample.txt", "a") as file:
    # Write the current date and time to the file
    file.write(str(now) + '\n')
