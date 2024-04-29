# Using your own data
The scripts in this folder are written such that anyone can process their data and generate a visual dashboard of their results.

The following instructions are for processing Facebook Messenger data. If you'd like to use data that's not in this format, see [message_x.json](https://github.com/teresaibarra/texts/blob/main/utils/example_data/message_x.json) in the `example_data` for the JSON structure the scripts expect.


### Step 1: Download your data

Facebook allows you to download all of your data, including your Messenger data. See more information on how to do so here: https://www.facebook.com/help/messenger-app/212802592074644

These messages are stored in JSON files. The files for this project were found in a folder titled "your_activity_across_facebook" -- there may be multiples of these folders, so check the contents of each.

In my case, my messages specifically with my ex were located in the path `your_activity_across_facebook/messages/inbox/ex'sname_1234567890`. For conversations with many text messages, messages are split into several JSON files. In my case, there were 10 message.json files.

### Step 2: Copy your data to the private_data folder
We'll need to transform the data to analyze it properly. Create a new folder titled `private_data` within `utils`. Place all of your message files into this directory.

### Step 3: Run the scripts
This folder contains two scripts: `process_data.py` and `generate_site_data.py`. The former will massage your data into a analysis-friendly format, run sentiment analysis, and create and train a topic model. After the data is processed, the latter will derive your data in order to generate an Observable dashboard with your results.
