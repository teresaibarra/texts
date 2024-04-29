import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
private_data_dir = os.path.join(current_dir, 'private_data/')

def process_bool_input(input):
    if input == "Y":
        return True
    return False

def interpret_topics(topics):
    for topic in topics:
        print()
        words = ''
        for word_dict in topic["words"]:
            words = words + " " + word_dict["word"]
        print("Key words: " + words)

        print("Do you have an interpretation for this topic AND would feel comfortable including it in your dashboard?")
        print("If yes, how would you describe this topic in one sentence or less? If not, press ENTER.")

        topic["interpretation"] = input()

    print("Wonderful! We've classified all of your topics.")
    return topics

def print_topics(topic_map):
    print()
    print(" =========== TOPICS =========== ")
    for i, interpretation in topic_map.items():
        print(str(i) + ': ' + interpretation)


def generate_topic_groups(topics):
    topic_groups = []

    print()
    print("Now, it's time to group your topics together. I'll show you all of your topics.")
 
    topic_map = {}
    for i, topic in enumerate(topics):
        interpretation = topic["interpretation"]
        if interpretation:
            topic_map[i] = interpretation

    print()

    opt_in = True

    while opt_in: 
        print_topics(topic_map)

        print("What's the title of your topic group?")
        group_name = input()
        
        print("How would you describe this topic group in less than one sentence?")
        description = input()

        print("Please enter a comma-separated list of the indices you feel belong to this topic. (ex '1,2, 34')")
        input_str = input()

        indices_str = input_str.split(',')
        indices = [int(num.strip()) for num in indices_str]

        for i in indices:
            del topic_map[i]

        topic_groups.append({
            "title": group_name,
            "description": description,
            "topics": indices
        })

        print("Would you like to add another topic group? (Y/n)")
        if process_bool_input(input()):
            print("Great! Let's do this again.")
        else:
            opt_in = False

    return topic_groups

def derive_data(generated_topics, topic_groups, messages):
    name_map = {message['sender_name']: message['sender_name'] for message in messages}

    for real_name in list(name_map.keys()):
        new_name = input(f"We'll display '{real_name}'. Enter new display name or press enter to keep it: ").strip()
        if new_name:
            name_map[real_name] = new_name
    
    print("Next, let's examine the frequency of the words in your conversations. Please list the words you'd like to measure counts for.")
    print("ex. love, hate, sorry, your_pet_name")
    
    input_str = input()
    keywords = [word.strip() for word in input_str.split(",")]

    should_find_longest = False
    print("Would you like to show your longest messages? (Y/n)")
    if process_bool_input(input()):
        should_find_longest = True

    print("****DISCLAIMER*****")
    print("I strongly recommend you review your generated datasets for any identifiable (or embarrassing) information before publishing it or showing it to other people.")
    print("Promise me you'll take a look? (Y/n)")

    has_read = False
    if process_bool_input(input()):
        has_read = True

    while not has_read:
        print("No, seriously. This is an ultimatum.")
        print("Promise me you'll take a look? (Y/n)")
        if process_bool_input(input()):
            has_read = True
    
    print("We ride!")

    return transform_messages(messages, name_map, keywords), filter_topics(generated_topics, topic_groups), get_longest_messages(messages, name_map, should_find_longest)

def transform_messages(messages, name_map, keywords):
    transformed_data = []

    for message in messages:
        timestamp = message['timestamp_ms'] 
        sender = name_map[message['sender_name']]

        compound = 0
        if "compound" in message:
            compound = message['compound']
            
        keywords_present = []
        if "content" in message:
            for keyword in keywords:
                if keyword.lower() in message["content"].lower():
                    keywords_present.append(keyword)
        
        topic = None
        if "topic_index" in message:
            topic = message["topic_index"]

        transformed_data.append({
            'timestamp': timestamp,
            'sender': sender,
            'keywords': keywords_present,
            'compound_score': compound,
            'topic': topic
        })
        
    return transformed_data
    
def filter_topics(generated_topics, topic_groups):
    all_topics = set()
    for item in topic_groups:
        all_topics.update(item['topics'])

    return [topic for topic in generated_topics if topic['index'] in all_topics]

def get_longest_messages(messages, name_map, should_find_longest):
    longest_messages_by_sender = {display_name: "" for display_name in name_map.values()}

    if not should_find_longest:
        return longest_messages_by_sender
    
    for message in messages:
        if "content" in message:
            sender = message['sender_name']
            display_name = name_map[sender]
            content_length = len(message['content'])

            if content_length > len(longest_messages_by_sender[display_name]):
                longest_messages_by_sender[display_name] = message["content"]
        
    return longest_messages_by_sender


def main():
    print("Hello!")
    print("Before we get started, let's interpret each topic. This should be your interpretation of what the key words of your topic describe.")
    print("For example, key words like 'today', 'tomorrow', 'cafe' could be interpreted as 'Planning and scheduling meetups at a cafe'.")
    print("Because you're looking at a bag of words, it may be helpful to reference at some of the messages that were classified by your model by checking their topic indices.")

    parent_directory = os.path.dirname(current_dir)
    GENERATED_TOPICS_PATH = os.path.join(private_data_dir, 'topics.json')
    TOPIC_GROUPS_PATH = os.path.join(parent_directory, 'docs', 'public_data', 'topic_groups.json')

    topics_with_interpretation = []

    with open(GENERATED_TOPICS_PATH, 'r') as input_file:
        topics = json.load(input_file)

        print("If you're not running this script for the first time, have you already interpreted your topics? (Y/n)")

        if process_bool_input(input()):
            print("Great! We'll skip the interpretation part.")
            topics_with_interpretation = topics
        else:
            topics_with_interpretation = interpret_topics(topics)
            print("Now updating your topics file with your interpretations...")

            with open(GENERATED_TOPICS_PATH, 'w') as input_file:
                json_data = json.dumps(topics_with_interpretation, indent=4)
                input_file.write(json_data)

        topic_groups = generate_topic_groups(topics_with_interpretation)

        print("Now generating a topic_groups file...")

        with open(TOPIC_GROUPS_PATH, 'w') as input_file:
            json_data = json.dumps(topic_groups, indent=4)
            input_file.write(json_data)

    print("Now it's time to derive your data.")
    print("""When generating a static site with Observable Framework, the site will serve the files used for the visualizations. Ideally, we should
not surface the content of all of the text messages you've ever sent to the World Wide Web, so we'll derive a safe version of the text
messages so the visualizations only process data that they need.""")
    
    DERIVED_MESSAGES_PATH = os.path.join(parent_directory, 'docs', 'public_data', 'derived_messages.json')
    DERIVED_TOPIC_GROUPS_PATH = os.path.join(parent_directory, 'docs', 'public_data', 'topics.json')
    LONGEST_MESSAGES_PATH = os.path.join(parent_directory, 'docs', 'public_data', 'longest_messages.json')

    with open(private_data_dir + "messages.json", 'r') as messages_file:
        messages = json.load(messages_file)

        derived_data, filtered_topics, longest_messages = derive_data(topics_with_interpretation, topic_groups, messages)

        with open(DERIVED_MESSAGES_PATH, 'w') as input_file:
            json_data = json.dumps(derived_data, indent=4)
            input_file.write(json_data)

        with open(DERIVED_TOPIC_GROUPS_PATH, 'w') as input_file:
            json_data = json.dumps(filtered_topics, indent=4)
            input_file.write(json_data)

        with open(LONGEST_MESSAGES_PATH, 'w') as input_file:
            json_data = json.dumps(longest_messages, indent=4)
            input_file.write(json_data)

    print("You'll find your files in /docs/public_data. Remember to review them!")

if __name__ == "__main__":
    main()
