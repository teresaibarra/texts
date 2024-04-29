from collections import Counter
import json
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import re
from nltk.stem import WordNetLemmatizer

MIN_TOKEN_LENGTH = 2
MIN_STRING_LENGTH = 3

##
## This function processes the list of messages and outputs a file that the Biterm model can use to train
##

def prepare_files():
    input_file_path = 'data/messenger/messages_with_sentiment.json'
    valid_messages = 'valid_messages.json' # Messages that have valid content after processing
    btm_messages = '../sample-data/messages.txt'

    final_text_data = []
    texts = []

    def filter_tokens(message):
        content = message['content']
        lowercase_msg = re.sub(r"http\S+","", content.lower()).replace('â', "'re") 
        tokens = tokenizer.tokenize(lowercase_msg)
        return [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and not token.isdigit() and len(lemmatizer.lemmatize(token)) >= MIN_TOKEN_LENGTH]
    
    with open(input_file_path) as json_file:
        message_data = json.load(json_file)

        tokenizer = RegexpTokenizer(r'\w+')
        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        
        # These words are specific to the collection of text messages and should be adjusted
        additional_stop_words = ['ð', 'â', 'ï', 'í', 'ì', '_', '__', '___', 'ìºì', 'ã', 'like', 'think', 'know', 'want', 'oh', 'get', 'yeah', 'really', 'people', 'feel', 'yes', 'feel', 'would', 'also', 'see', 'one', 'things', 'make', 'lin', 'much', 'thing', 'time', 'right', 'good', 'got', 'going', 'way', 'lot', 'go', 'could', 'something', 'though', 'stuff', 'probably', 'first', 'still', 'back', 'two']
        stop_words.update(additional_stop_words)

        # Count the occurrences of each token in the entire document collection
        # We should remove tokens that have occurred 10 or less times in the doc collection
        token_counts = Counter()

        for message in message_data['messages']:
            if "content" in message:
                filtered_tokens = filter_tokens(message)
                token_counts.update(filtered_tokens)
        
        # Get the top 100 words for token adjustment
        # top_words = token_counts.most_common(100)
        # print(top_words)

        for message in message_data['messages']:
            if "content" in message:
                filtered_tokens = filter_tokens(message)
                final_tokens = [token for token in filtered_tokens if token_counts[token] >= 10]
                final_string = " ".join(final_tokens).strip()

                if len(final_tokens) > MIN_STRING_LENGTH and len(final_string) > 0:
                    final_text_data.append(message)
                    texts.append(final_string)

    with open(valid_messages, 'w') as f:
        json_data = json.dumps(final_text_data, indent=4)
        f.write(json_data)

    with open(btm_messages, "w") as f:
        for string in texts:
            f.write(string + "\n")

##
## Helper functions for processing BTM results
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

##
## This function processes the results from the BTM model and adds topic data to the message JSON files
##    

def process_results():
    VALID_MESSAGES_PATH = 'valid_messages.json'
    TOPIC_VECTOR_PATH = '../output/model/k40.pw_z'
    VOCAB_PATH = '../output/voca.txt'
    PZ_PATH = '../output/model/k40.pz'
    PREDICTED_TOPICS_PATH = '../output/model/k40.pz_d'

    MESSAGES_WITH_TOPICS_PATH = 'messages_with_topics.json'

    vocab = read_voca(VOCAB_PATH) # BTM generates a file containing vocab from the input file
    topic_map = []

    with open(VALID_MESSAGES_PATH) as json_file:
        message_data = json.load(json_file)

        with open(TOPIC_VECTOR_PATH) as topic_top_words:
            pz = read_pz(PZ_PATH)
            k = 0
            
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

                # make a list of topics and each of its associated topic words
                topic_map.append({
                    'index': i,
                    'p(z)': pz[k],
                    'words': topic_prob_list
                })
                k += 1
                
        # add topic data to each message
        with open(MESSAGES_WITH_TOPICS_PATH, 'w') as f:
            predicted_topics = read_pz_d(PREDICTED_TOPICS_PATH)
            for i, message in enumerate(message_data):
                message['topic_index'] = predicted_topics[i]

            json_data = json.dumps({'topics': topic_map, 'messages': message_data}, indent=4)
            f.write(json_data)
