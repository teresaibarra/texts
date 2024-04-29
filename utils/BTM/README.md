These files are for use with the Biterm model in this [repository](https://github.com/xiaohuiyan/BTM). 

The file output of add_sentiment.py must be prepared for this script by taking each message's content and preparing it for NLP analysis (set to lowercase, tokenize, lemmatize, etc.), then generating a file where each message is on a new line. In this process, we get rid of any message who contents don't meet the criteria for being processed by the Biterm topic model. 

The example shell script should be updated with different parameters. The shell will present the topics and top words for each topic -- these should be evaluated, ideally qualitatively. The output of the script should then be reprocessed into a valid JSON file.