---
theme: dashboard
title: Analyzing my texts messages with my ex-boyfriend

---

# Analyzing my texts messages with my ex-boyfriend

```js
const derivedAllMessages = FileAttachment("data/derived_all_messages.json").json();
const derivedMessages = FileAttachment("data/derived_messages_with_topics.json").json();
const topicGroups = FileAttachment("data/topic_groups.json").json();
const labelledTopics = FileAttachment("data/topics.json").json();
const longestMessages = FileAttachment("data/longest_messages.json").json();

const LAST_RELATIONSHIP_MONTH = new Date(2016, 9);
```
<h3>by <a  href="https://teresaibarra.com/">Teresa Ibarra</a></h3>

<p>&nbsp;</p>

## Message Frequency
We got together in the summer of 2015 and broke up in the spring of 2016.

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Total messages from Teresa</h2>
    <span class="big">${derivedAllMessages.filter((d) => d.sender === "Teresa Ibarra").length}</span>
  </div>
  <div class="card">
    <h2>Total messages from him</h2>
    <span class="big">${derivedAllMessages.filter((d) => d.sender === "My ex").length}</span>
  </div>
</div>

<!-- Plot of message frequency -->

```js

console.log(topicGroups)

function messageFrequencyPlot(data, { width } = {}) {
  return Plot.plot({
    title: "Message count up until last contact",
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
    return timestamp < LAST_RELATIONSHIP_MONTH.getTime();
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
          negativeFill: "red",
        }
      )))
    ]
  })
}
```
<p>&nbsp;</p>

## Sentiment Analysis

"Sentiment analysis is a natural language processing (NLP) technique used to determine whether data is positive, negative or neutral." This was run on every text message exchanged during our relationship. The compound score (sum of the negative and positive score) is shown below.

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

## Longest Messages

These were the longest messages we sent to each other. 

I hoped this would be something spicy like a long, drawn-out argument, but it turns out I just needed help with my homebrew configuration and he was geeking out about his philosophy meetup.


<div class="grid grid-cols-2">
  <div class="card">
    <h2>Longest message from Teresa</h2>
    <i>This seems to be terminal output from an incorrect homebrew installation of Python. <br /><br /></i>
    <pre style="height: 80ex; overflow-y: scroll;">${longestMessages["Teresa Ibarra"]}</pre>
  </div>
  <div class="card">
    <h2>Longest message from him</h2>
    <i>This is a list of questions that are posed for a philosophy meetup group he was attending. <br /><br /></i>
    <pre>>${longestMessages["My ex"]}</pre>
  </div>
</div>

<p>&nbsp;</p>

## Key Words

This is how often we used these words in our messages. 

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
      Plot.barY(aggregateDataCount(data, LAST_RELATIONSHIP_MONTH), {
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

The following graphs depicts 40 topics found in our text messages and a topic was predicted for each message. The topics were identified with a Biterm topic model. Topics are grouped by theme. A list of words are associated with each topic and are ordered from most to least relevance and I have added a possible interpretation. 

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
      Plot.barY(aggregateDataCount(data, LAST_RELATIONSHIP_MONTH), {
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

## FAQ & Fun tidbits
<p>&nbsp;</p>

#### Q: How did you get the messages?
These messages were sent over Facebook Messenger. Facebook allows you to download all of the messages you've ever sent, ever, in JSON format. I processed these files with Python. 

#### Q: How did you perform sentiment analysis?
I used NLTK's SentimentIntensityAnalyzer Python module on every text message.

#### Q: How did you get the topics?
I trained and ran the Biterm topic model on all of my text messages, then had it return the most likely topics for each message.

#### Q: What was it like to show your friends this?
Interestingly enough, my friends have expressed surprise at the data and how much it didn't align with their perception of the relationship.

#### Q: Why did you do this?
I thought it would be funny.

#### Q: Where did this idea come from?
I conceived the idea for this in the era where large tech companies (social media) would hoard data, and it wasn't clear what they'd do with it. I wanted to explore the ways in which companies that have our data could analyze who we were from our data, how data we didn't think much of could reveal so much about ourselves.

Data is biased. The collection, the processing, and the presentation is all biased. I feel it's difficult to understand how this manifests in practice, and the questions that you ask about my biases in this project is the same scrunity we should hold towards all data and AI/ML tools.

#### Q: It's very personal to share this. Why did you do this?
that's art babey!!

#### Q: That's cool! I wonder what it'd be like to run it on my text messages.
I can't say I recommend it -- it was surreal and uncomfortable to read through messages from a decade ago. Programmatic analysis can reveal things about yourself, your partner, and your relationship that you may not want to know or accept.

#### Q: Could you release this so that people could do this themselves?
It's doable to release the Javascript-only graphs to a wider audience. However, the topic model is finely tuned to my data and would not transfer accurately to any one person's texts.

#### Q: Was this carthartic?
Not in the way I expected. I wanted to do this project since 2021 and I've told people about it for years. I felt bad that I was never able to start it. Completing this at Recurse Center gave me the release from the shame of not completing it.

<p>&nbsp;</p>

#### Fun tidbit
In training the topic model, I had to get rid of words that occurred too frequently to the point where it would negatively influence the accuracy of the topics. Some of them were 'like', 'think', and 'really', which are fitting for conversations between two Californian 17 year olds.

<p>&nbsp;</p>
<p>&nbsp;</p>

<script async defer src="https://www.recurse-scout.com/loader.js?t=cebb8f1aa2412719dcf855f950ab254c"></script>
<div class="rc-scout"></div>