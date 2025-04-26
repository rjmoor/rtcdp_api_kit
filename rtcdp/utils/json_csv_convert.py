import pandas as pd
import json
import os

# Function to convert JSON file to CSV
def json_to_csv():
    try:
        # Prompt the user for the JSON file path
        json_file_path = input("Please enter the full path of the JSON file: ")
        
        # Check if the file exists
        if not os.path.exists(json_file_path):
            print(f"File not found: {json_file_path}")
            return
        
        # Load JSON data from the file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        
        # Convert JSON to DataFrame
        df = pd.DataFrame(data)
        
        # Generate the output CSV path in the same directory
        directory = os.path.dirname(json_file_path)
        csv_output_path = os.path.join(directory, 'output.csv')
        
        # Save DataFrame to CSV
        df.to_csv(csv_output_path, index=False)
        
        print(f"CSV file has been created: {csv_output_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the conversion function
json_to_csv()

