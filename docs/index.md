---
theme: ["air", "midnight"]
title: Analyzing my text messages with my ex-boyfriend

---

# Analyzing my text messages with my ex-boyfriend

```js
const derivedAllMessages = FileAttachment("data/derived_all_messages.json").json();
const derivedMessages = FileAttachment("data/derived_messages_with_topics.json").json();
const topicGroups = FileAttachment("data/topic_groups.json").json();
const labelledTopics = FileAttachment("data/topics.json").json();
const longestMessages = FileAttachment("data/longest_messages.json").json();

const lastMonthOfRelationship = new Date(2016, 9);
```
<h3>by <a href="https://teresaibarra.com/">Teresa Ibarra</a></h3>

<p>&nbsp;</p>

## Message frequency
We began dating in the summer of 2015 and broke up in the spring of 2016.

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Total messages from Teresa</h2>
    <span class="big">${derivedAllMessages.filter((d) => d.sender === "Teresa Ibarra").length}</span>
  </div>
  <div class="card">
    <h2>Total messages from my ex</h2>
    <span class="big">${derivedAllMessages.filter((d) => d.sender === "My ex").length}</span>
  </div>
</div>

<!-- Plot of message frequency -->

```js
function messageFrequencyPlot(data, { width } = {}) {
  return Plot.plot({
    title: "Message count over time",
    x: { axis: null },
    fx: { type: "utc", interval: "month", label: "month" },
    y: { grid: true, label: "message count" },
    color: { legend: true },
    width,
    marks: [
      Plot.barY(aggregateDataCount(data, new Date()), {
        x: "sender",
        y: "count",
        fx: d => d3.utcMonth(d.timestamp),
        fill: "sender",
        tip: true,
      }),
      Plot.ruleY([0])
    ]
  })
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => messageFrequencyPlot(derivedAllMessages, {width}))}
  </div>
</div>

<!-- Plot of compound sentiment analysis -->

```js
function sentimentPlot(data, { width } = {}) {
  const dataWithCutoff = data.filter(item => {
    const timestamp = item.timestamp;
    return timestamp < lastMonthOfRelationship.getTime();
  });

  return Plot.plot({
    
    width,
    y: {
      grid: true,
      domain: [-0.2, 0.2],
    },
    marks: [
      Plot.ruleY([0]),
      Plot.differenceY(dataWithCutoff, Plot.shiftX("21 days", Plot.windowY(
        275,
        {
          x: "timestamp",
          y: "compound_score",
          positiveFill: "#3dc06c",
          negativeFill: "#D3212C"
        }
      )))
    ]
  })
}
```
<p>&nbsp;</p>

## Sentiment analysis

Sentiment analysis is the process of computationally identifying and categorizing the emotions expressed in a piece of text as positive, negative, or neutral. 
[NLTK's VADER tools](https://www.nltk.org/_modules/nltk/sentiment/vader.html) were run on every message that contained text. The following graphs represent the [compound score](https://github.com/cjhutto/vaderSentiment?tab=readme-ov-file#about-the-scoring) over time.

<div class="grid grid-cols-1">
  <div class="card">
  <h2>Combined messages</h2>
    ${resize((width) => sentimentPlot(derivedAllMessages, {width}))}
  </div>
</div>

<div class="grid grid-cols-1">
  <div class="card">
  <h2>Teresa's messages</h2>
    ${resize((width) => sentimentPlot(derivedAllMessages.filter((m) => m.sender === "Teresa Ibarra"), {width}))}
  </div>
</div>


<div class="grid grid-cols-1">
  <div class="card">
  <h2>His messages</h2>
    ${resize((width) => sentimentPlot(derivedAllMessages.filter((m) => m.sender === "My ex"), {width}))}
  </div>
</div>

<p>&nbsp;</p>

## Longest messages

These were the longest messages we ever sent to each other. 

In a way I hoped this would be something spicy like a long, drawn-out argument. But it turns out I just needed help with configuring Homebrew and he was geeking out about his philosophy meetup.


<div class="grid grid-cols-2">
  <div class="card">
    <h2>Longest message from Teresa</h2>
    <i>These are warnings from terminal output due to issues in my Homebrew configuration. <br /><br /></i>
    <pre style="height: 80ex; overflow-y: scroll;">${longestMessages["Teresa Ibarra"]}</pre>
  </div>
  <div class="card">
    <h2>Longest message from him</h2>
    <i>This is a list of questions for a philosophy meetup group he was attending. <br /><br /></i>
    <pre>>${longestMessages["My ex"]}</pre>
  </div>
</div>

<p>&nbsp;</p>

## Key words

The following graphs represent how often we sent specific words to each other.

```js
function keywordPlot(data, { width } = {}, title) {
  return Plot.plot({
    title,
    x: { ticks: [], axis: null, label: null },
    fx: { type: "utc", interval: "week", label: "week" },
    y: { grid: true },
    color: { legend: true },
    width,
    marks: [
      Plot.barY(aggregateDataCount(data, lastMonthOfRelationship), {
        x: "sender",
        y: "count",
        fx: d => d3.utcWeek(d.timestamp),
        fill: "sender",
        tip: true,

      }),
      Plot.ruleY([0])
    ]
  })
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => keywordPlot(derivedAllMessages.filter(message => message.keywords.includes("pet_name")), {width}, "Messages containing our pet names for each other"))}
  </div>
</div>

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => keywordPlot(derivedAllMessages.filter(message => message.keywords.includes("love")), {width}, 'Messages containing the word "love"'))}
  </div>
</div>


<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => keywordPlot(derivedAllMessages.filter(message => message.keywords.includes("sorry")), {width}, 'Messages containing the word "sorry"'))}
  </div>
</div>

<p>&nbsp;</p>

## Topics over time

I trained a [Biterm topic model](https://xiaohuiyan.github.io/paper/BTM-WWW13.pdf) to identify 40 recurring topics in our text messages. The model then assigned a topic to every message containing text. The following graphs describe the frequency of a given topic over time.

The model describes a given topic as a list of words. The list is ordered from most to least relevance. I added a possible interpretation of this list for each topic. 

```js
function topicPlot(data, { width } = {}, index, teresaMessages, exMessages) {
  const topicInfo = labelledTopics.find(topic => topic.index === index)
  return Plot.plot({
    title: topicInfo.words.map(wordObj => wordObj.word).join(', '),
    subtitle: "Possible interpretation: " + topicInfo.interpretation,
    x: { ticks: [], axis: null, label: null },
    fx: { type: "utc", interval: "week", label: "week" },
    y: { grid: true, label: "message count" },
    color: { legend: true },
    width,
    marks: [
      Plot.barY(aggregateDataCount(data, lastMonthOfRelationship), {
        x: "sender",
        y: "count",
        fx: d => d3.utcWeek(d.timestamp),
        fill: "sender",
        tip: true,

      }),
      Plot.ruleY([0])
    ]
  })
}
```

<p>&nbsp;</p>

<div class="grid grid-cols-1">
  <span>
      ${topicGroups.map(group => {
      const { title, description, topics } = group;
      return html`
        <span>
          <div>
            <h3>${title}</h3>
            <p>${description}</p>
            ${topics.map(topicIndex => {
              const filteredMessages = derivedMessages.filter(message => message.topic === topicIndex);
              const teresaMessages = filteredMessages.filter(message => message.sender === 'Teresa Ibarra');
              const exMessages = filteredMessages.filter(message => message.sender !== 'Teresa Ibarra');
              return html`
                <div class="card">
                  <h3>Topic ${topicIndex}</h3>
                  ${resize((width) => topicPlot(filteredMessages, { width }, topicIndex, teresaMessages, exMessages))}
                </div>
              `;
            })}
          </div>
        </span>
        <p>&nbsp;</p>
      `;
    })}
  </span>
</div>


```js
function aggregateDataCount(data, endDate) {
  const senders = Array.from(new Set(data.map(item => item.sender)));
  const earliestTimestamp = d3.min(data, d => d.timestamp);
  const weeks = d3.timeWeek.range(new Date(earliestTimestamp), endDate, 1).map(d => +d);

  const reducedData = [];
  senders.forEach(sender => {
    weeks.forEach(week => {
      reducedData.push({ sender: sender, timestamp: week, count: 0 });
    });
  });

  data.forEach(myData => {
    const sender = myData.sender;
    const senderData = reducedData.filter(item => item.sender === sender);
    const timestamp = myData.timestamp;

    senderData.forEach(item => {
      if (timestamp >= item.timestamp && timestamp < item.timestamp + 604800000) {
        item.count++;
      }
    });
  });

  return reducedData;
}
```

## FAQ
<p>&nbsp;</p>

#### Q: Why did you do this?
I thought it would be funny.

#### Q: How did you get the messages?
These messages were sent over Facebook Messenger. Facebook allows you to download all of the messages you've ever sent, ever, as JSON files. I processed these files with Python. You can see the scripts I wrote for processing in [this folder](https://github.com/teresaibarra/texts/tree/main/models).

#### Q: How did you perform sentiment analysis?
I used [NLTK's VADER tools](https://www.nltk.org/_modules/nltk/sentiment/vader.html) on every text message. You can see how I did this [here](https://github.com/teresaibarra/texts/blob/main/models/data_processing/add_sentiment.py).

#### Q: How did you get the topics?
I trained a [Biterm topic model](https://github.com/xiaohuiyan/BTM) on all of my text messages and had it identify the most likely topic for each message. You can see how I trained and ran the model [here](https://github.com/teresaibarra/texts/tree/main/models/btm_files).

#### Q: How did you do the visualizations?
I used [Observable Plot](https://observablehq.com/plot/) to make the charts. This site was generated with [Observable Framework](https://observablehq.com/framework/). You can find my code for the visualizations [here](https://github.com/teresaibarra/texts/blob/main/docs/index.md?plain=1).

#### Q: What was it like to show your friends this?
One friend in particular was surprised by the data and how it didn't align with their perception of the relationship.

#### Q: Does your ex know that you did this?
He does! He was the first person I talked to about it. He thought that this turned out amazing... (ಥ﹏ಥ)

#### Q: Where did this idea come from?
I came up with the idea for this in 2020. Large social media companies hoards data and at the time, it wasn't clear to me what they'd do with it. I wanted to explore the ways in which private companies could analyze who we were from our data. We don't think so much about the data that we consent to sharing and it's hard to conceptualize how data can reveal so much.

Data are biased. The existence, expression, collection, and the presentation of data are all biased. I hope that you question how I actually relate to this data and how I made decisions on this project. I believe we should apply the same scrunity towards all data analysis, artificial intelligence, and machine learning tools.

#### Q: It's very personal to share this. Why did you do this?
that's art babey!!

#### Q: That's cool! I wonder what it'd be like to run it on my text messages.
I can't say I recommend it -- it was surreal and uncomfortable to read through messages from a decade ago. Programmatic analysis can reveal things about yourself, your partner, and your relationship that you may not want to know or accept. It's also easy to intentionally or unintentionally manipulate data to favor a narrative.

#### Q: Can you release this so that people could do this themselves?
I'm considering it. However, the topic model is custom to my data and would not transfer accurately to anyone else's texts. 

#### Q: Was this cathartic?
Not in the way I expected. I wanted to complete this project for a long time and I've told people about it for years. I felt bad that I was never able to do it. Dedicating time to work on this at [Recurse Center](https://www.recurse.com/) released me from that shame.

<p>&nbsp;</p>

#### Fun tidbit
When I was training the topic model, some words occurred so frequently that it would negatively influence topic accuracy. Some of the words were 'like', 'think', and 'really', which are fitting for text messages between two Californian 17 year olds.

<p>&nbsp;</p>
<p>&nbsp;</p>

This project was created by [Teresa Ibarra](https://teresaibarra.com/).
<script async defer src="https://www.recurse-scout.com/loader.js?t=cebb8f1aa2412719dcf855f950ab254c"></script>
<div class="rc-scout"></div>