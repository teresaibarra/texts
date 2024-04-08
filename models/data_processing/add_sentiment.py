import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer


input_file_path = 'data/messenger/all_messages.json'
output_file_path = 'data/messenger/messages_with_sentiment.json'

# this code reads a JSON file containing all Messenger messages and then adds sentiment analysis and word count data
with open(input_file_path, 'r') as input_file:
    message_data = json.load(input_file)

    # add positive, negative, and composite sentiment analysis to every message
    sid = SentimentIntensityAnalyzer()
    
    for message in message_data:
        if 'content' in message: # some messages do not contain text content and will not have the "content" key
            # add sentiment analysis scores
            scores = sid.polarity_scores(message['content'])
            message['neg'] = scores['neg']
            message['pos'] = scores['pos']
            message['compound'] = scores['compound']

    with open(output_file_path, 'w') as file:
        json.dump(message_data, file, indent=4)