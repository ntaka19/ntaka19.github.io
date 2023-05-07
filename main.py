import datetime
import os
import time

if not os.path.exists('data'):
    print("error")

# Get the current date and time
now = datetime.datetime.now()


# Open the file in write mode
with open("./data/sample.txt", "a") as file:
    # Write the current date and time to the file
    file.write(time.localtime().tm_zone + " " + str(now) + '\n')
