import json
from datetime import datetime, timezone


KEYWORDS = ["pet_name", "love", "sorry"]

def get_unix_timestamp_milliseconds(year, month, day=1, hour=0, minute=0, second=0):
    return int(datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc).timestamp() * 1000)

def extract_keywords(content):
    relevant_keywords = []
    for keyword in KEYWORDS:
        if keyword in content:
            # if keyword == "pet_name":
            #     relevant_keywords.append("pet_name")
            # else:
            #     relevant_keywords.append(keyword)
            relevant_keywords.append(keyword)
    return relevant_keywords

def transform_messages(messages, eval_content):
    transformed_data = []

    for message in messages:
        timestamp = message['timestamp_ms'] 
        sender = message['sender_name']
        if "compound" in message:
            compound = message['compound']
        else:
            compound = 0

        
        if eval_content:
            keywords = extract_keywords(message['content'])
            topic = message['topic_index']
        
            transformed_data.append({
                'timestamp': timestamp,
                'sender': sender,
                'keywords': keywords,
                'topic': topic
            })

        else:
            keywords = []
            if "content" in message:
                keywords = extract_keywords(message['content'])
            transformed_data.append({
            'timestamp': timestamp,
            'sender': sender,
            'keywords': keywords,
            'compound_score': compound
        })

    return transformed_data


# input_file_path = 'docs/real_data/processed_messages.json'
# output_file_path = 'docs/data/derived_all_messages.json'
# with open(input_file_path, 'r') as input_file:
#     message_data = json.load(input_file)["messages"]
#     transformed_data = transform_messages(message_data, False)

#     with open(output_file_path, 'w') as file:
#         json.dump(transformed_data, file, indent=4)

# input_file_path = 'docs/real_data/messages_with_topics.json'
# output_file_path = 'docs/data/derived_messages_with_topics.json'
# with open(input_file_path, 'r') as input_file:
#     message_data = json.load(input_file)["messages"]
#     transformed_data = transform_messages(message_data, True)

#     with open(output_file_path, 'w') as file:
#         json.dump(transformed_data, file, indent=4)

topic_groups_path = 'docs/data/topic_groups.json'
labeled_topics_path = 'docs/real_data/labeled_topics.json'
output_file_path = 'docs/data/topics.json'

filtered_topics = []
with open(topic_groups_path, 'r') as topic_group_file:
    with open(labeled_topics_path, 'r') as labeled_topics_file:
        topic_groups = json.load(topic_group_file)
        labeled_topics = json.load(labeled_topics_file)

        for group in topic_groups:
            for topic in group["topics"]:
                filtered_topics.append(labeled_topics[topic])

with open(output_file_path, 'w') as file:
    json.dump(filtered_topics, file, indent=4)