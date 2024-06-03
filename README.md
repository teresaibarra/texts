# Analyzing a relationship's text messages

This project aims to visualize emotional and thematic trends and provide insight about personal relationship dynamics. This code can be used as a exploration tool for navigating the nuance of digital communication and understanding the biases that can emerge from machine learning analysis.


[![Screenshot of Visualization](https://github.com/teresaibarra/texts/assets/7967489/e4f7533b-05a1-449b-9719-17b67daf4563)](http://teresaibarra.com/texts/)

## Features

- **Pretty comprehensive analysis**: Analyzes 80,000 text messages exchanged over the span of a relationship with natural language processing techniques.
- **Trained topic model**: Uses a [Biterm topic model](https://github.com/xiaohuiyan/BTM/tree/master) specifically trained on the dataset.
- **Sentiment analysis**: Runs [sentiment analysis](https://www.nltk.org/_modules/nltk/sentiment/vader.html) on all messages to gauge emotional trends.
- **Visualization**: Results are visualized using [Observable Plot](https://observablehq.com/plot/), and the static site is generated with [Observable Framework](https://observablehq.com/framework/).
- **DIY-friendly**: See the ["Using your own data"](#using-your-own-data) section.
- **Live demo**: Check out the live demo [here](https://teresaibarra.com/texts).

## Running locally

Clone this repo and execute:

```bash
npm run dev
```

## Using your own data
You can adapt this code by running the Python scripts provided in the [`utils` folder](https://github.com/teresaibarra/texts/tree/main/utils). Check out the `README` for more information.


## Credits
- This project was created during my time at the [Recurse Center](http://recurse.com) in Spring 2024.
- Thanks to all the folks who paired with me on this project at RC!
- Special thanks to my ex in their support of this project.
