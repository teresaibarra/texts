import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
private_data_dir = os.path.join(current_dir, 'private_data/')

# Combine the contents of all message files into one list
def get_all_messages():
    prefix = "message_"
    file_ext = ".json"
    file_count = 0
    for filename in os.listdir(private_data_dir):
        if filename.startswith(prefix) and filename.endswith(file_ext):
            file_count += 1
    
    raw_messages = []
    for i in range(0, file_count):
        print("Now combining " + private_data_dir + "message_{}.json".format(i + 1))
        with open(private_data_dir + "message_{}.json".format(i + 1), 'r') as input_file:
            data = json.load(input_file)
            raw_messages.extend(data["messages"])

    return raw_messages


# Add sentiment analysis scores to each of the messages that have the "content" attribute. Having this attribute implies the message has text information.
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def add_sentiment(messages):
    sid = SentimentIntensityAnalyzer()

    for message in messages:
        if 'content' in message:
            scores = sid.polarity_scores(message['content'])

            message['neg'] = scores['neg']
            message['pos'] = scores['pos']
            message['compound'] = scores['compound']

    return messages

from collections import Counter
import json
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import re
from nltk.stem import WordNetLemmatizer

MIN_TOKEN_LENGTH = 2 # After lemmatizing, tokens will be shortened, but we don't want tokens that are too short
MIN_DOCUMENT_LENGTH = 3 # This describes the minimum number of tokens in a document (aka a text message)

# Process the list of messages and outputs a file that the Biterm model will be trained on
def generate_model_files(messages):
    processed_texts = []

    tokenizer = RegexpTokenizer(r'\w+')
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    # These words are specific to my data and should be adjusted to your corpus (aka a collection of text messages)
    additional_stop_words = ['like', 'ok', 'want', 'think', 'year', 'feel', 'know', 'really', 'need', 'get', 'yeah', 'oh', 'thing', 'also', 'one', 'okay', 'would', 'wanna', 'see', 'go', 'gonna' ]
    stop_words.update(additional_stop_words)

    # We should remove tokens that have occurred 10 or less times in the document collection, as they're less likely to be relevant.
    # Thus, we should count the occurrences of each token and then filter them
    token_counts = Counter()

    def get_valid_tokens(message):
        content = message['content']
        lowercase_msg = re.sub(r"http\S+","", content.lower()).replace('â', "'re") 
        tokens = tokenizer.tokenize(lowercase_msg)
        return [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and not token.isdigit() and len(lemmatizer.lemmatize(token)) >= MIN_TOKEN_LENGTH]

    for message in messages:
        if "content" in message:
            valid_tokens = get_valid_tokens(message)
            token_counts.update(valid_tokens)
    
    for message in messages:
        if "content" in message:
            valid_tokens = get_valid_tokens(message)
            filtered_tokens = [token for token in valid_tokens if token_counts[token] >= 10]
            final_string = " ".join(filtered_tokens).strip()

            if len(filtered_tokens) > MIN_DOCUMENT_LENGTH and len(final_string) > 0:
                message["tokens"] = filtered_tokens
                processed_texts.append(final_string)

    # For this specific Biterm model module, it consumes a corpus that's in the format of a plaintext file with each document on a new line 
    btm_corpus = os.path.join(current_dir, 'BTM', 'model_input', 'messages.txt')
    
    with open(btm_corpus, "w") as f:
        for string in processed_texts:
            f.write(string + "\n")


# To train the model, we call a shell script with parameters tuned specifically to our corpus. This script and its accompanied code
# has been copied to this repo. The original code can be found here: https://github.com/xiaohuiyan/BTM/tree/master

import subprocess

def train_model():
    shell_script_path = os.path.join(current_dir, 'BTM', 'script', 'runExample.sh')
    subprocess.run(['bash', shell_script_path])


##
## The following are helper functions for processing the results from our model. They are pulled from the original BTM module code.
##            

def read_voca(pt):
    voca = {}
    for l in open(pt):
        wid, w = l.strip().split('\t')[:2]
        voca[int(wid)] = w
    return voca

def read_pz(pt):
    return [float(p) for p in open(pt).readline().split()]

def read_pz_d(pt):
    data = []
    for line in open(pt):
        values = line.split()
        floats = [float(value) for value in values]
        max_value = max(floats)
        max_index = floats.index(max_value)
        data.append(max_index)
    return data

# Process the results from the model and update our collection of text messages with their assigned topic.
def add_topics(messages):
    btm_output_dir = os.path.join(current_dir, 'BTM', 'model_output')

    VOCAB_PATH = os.path.join(btm_output_dir, 'voca.txt')
    TOPIC_VECTOR_PATH = os.path.join(btm_output_dir, 'model', 'k30.pw_z') # Note that the file names contain the number of topics
    PZ_PATH = os.path.join(btm_output_dir, 'model', 'k30.pz')
    PREDICTED_TOPICS_PATH = os.path.join(btm_output_dir, 'model', 'k30.pz_d')

    vocab = read_voca(VOCAB_PATH) # BTM generates a file containing the model's vocabulary, aka a list of all tokens
    topic_map = []

    with open(TOPIC_VECTOR_PATH) as topic_top_words:
        pz = read_pz(PZ_PATH)
        
        # Much of this code is adapted from the code in ./BTM/topicDisplay.py
        for i, l in enumerate(topic_top_words):
            topic_prob_list = []
            vs = [float(v) for v in l.split()]
            wvs = zip(range(len(vs)), vs)
            wvs = sorted(wvs, key=lambda d:d[1], reverse=True)

            for w,v in wvs[:10]:
                topic_prob_list.append({
                    'word': vocab[w],
                    'probability': v
                })

            # We'll create a file that contains the mapping of topics to their associated words
            topic_map.append({
                'index': i,
                'p(z)': pz[i],
                'words': topic_prob_list
            })
            
    current_topic_index = 0
    predicted_topics = read_pz_d(PREDICTED_TOPICS_PATH)
    for message in messages:
        # For every message that was included in our model's corpus, we should update each with their topic information.
        # We can identify these messages if they have a "tokens" attribute.
        if "tokens" in message:
            message['topic_index'] = predicted_topics[current_topic_index]
            current_topic_index += 1

    # We'll save the generated topics into a new file, where you'll be able to evaluate and characterize the results of your model
    GENERATED_TOPICS_PATH = os.path.join(private_data_dir, 'topics.json')
    with open(GENERATED_TOPICS_PATH, 'w') as file:
        json.dump(topic_map, file, indent=4)
    
    return messages



def process_bool_input(input):
    if input == "Y":
        return True
    return False

def main():
    print("Hello! Best of luck running this script!")

    print("First, can you confirm that all of your data is correctly formatted? See data_processing.md for more information. (Y/n)")
    if process_bool_input(input()):
        print("Great!  Now combining data files...")
    else:
        print("Apologies, this script isn't going to work out. It's not me, it's you.")
        return

    all_messages = get_all_messages()

    print("Now adding sentiment analysis scores to messages...")
    messages_with_sentiment = add_sentiment(all_messages)

    # We'll train a Biterm topic model to identify topics for each message. We'll be working with the original paper authors' code for
    # creating the model. We interface with the model through a shell script, and the data processing and training is done with C++.
    print("Now generating file for training our Biterm topic model. File will be saved in ./BTM/model_input.")
    generate_model_files(messages_with_sentiment)


    print("Now training the model...")
    train_model()
    print("Model output will be stored in ./BTM/model_output.")
    
    print("Now assigning topics to your messages...")
    messages_with_topics = add_topics(messages_with_sentiment)

    with open(private_data_dir + "messages.json", 'w') as input_file:
        json_data = json.dumps(messages_with_topics, indent=4)
        input_file.write(json_data)
        
    print("Your scored and classified messages are now stored in ./private_data/messages.json. The topics generated by the model are stored in ./private_data/topics.json")
    print("Please review the results of this model. Do these topics seem to make sense to you? If not, please adjust the parameters of your model before proceeding.")
    print("If you'd like to generate a dashboard displaying your results, check out the generate_site_data.py script.")
    

if __name__ == "__main__":
    main()
