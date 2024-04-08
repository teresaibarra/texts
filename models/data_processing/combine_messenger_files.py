import json

# Path to the existing JSON files
input_file_path = 'data/messenger/raw_message_data/message_{}.json'
# Path to the new JSON file
output_file_path = 'data/messenger/all_messages.json'

message_data = []

# For conversations with many text messages, messages are output into several JSON files.
# This combines all files into one. In this case, there are 10 message.json files.
for i in range(1, 10):
    with open(input_file_path.format(i), 'r') as input_file:
        data = json.load(input_file)
        message_data.extend(data["messages"])

with open(output_file_path, 'w') as output_file:
    json.dump(message_data, output_file, indent=4)