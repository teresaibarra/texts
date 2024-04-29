# How to process your own text messages
The following steps are for processing Facebook Messenger data. If you'd like to process data that's not originally in this format, see message_x.json in the example_data directory for tips.


### Step 1: Download your data.

Facebook allows you to download your data, including your Messenger data. See more information on how to do so here: https://www.facebook.com/help/messenger-app/212802592074644

Chat messages are stored in JSON files. These files were found in a folder titled "your_activity_across_facebook" -- there may be multiple of these files, so check the contents of each.

In my case, my messages specifically with my ex were located in a folder "inbox" > "Ex's Name". For conversations with many text messages, messages are split into several JSON files. In my case, there are 10 message.json files.

### Step 2: Upload your data to private_data.
For data processing purposes, we should combine these files into one file. Place all of your raw message data into the `private_data` dir in this folder.

### Step 3: Run process_data.py.
Best of luck!
