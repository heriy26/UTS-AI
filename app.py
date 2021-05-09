from flask import Flask,render_template, redirect, request
import re
import tweepy
from textblob import TextBlob

app = Flask(__name__, template_folder='templates')

class TwitterClient(object):

    def __init__(self):
        consumer_key = "e0XhAua0XWpRploIzTgoa2sFG"
        consumer_secret = "CndgSvCOVi36i8HKB9ZuEa1IogL7Ia5G4Zo2zYGh78albdLOZF"
        access_token = "1168410070897455104-rOW3I4vTLhsYP3hfADErd3f1LQIr1A"
        access_token_secret = "V1qA8dmsbV2khjxDgs87b0pvvufA9gIFNz2nGTsmOYuZJ"

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)
    
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
    
    def get_tweets(self, query, count = 10):
        tweets = []

        try:
            fetched_tweets = self.api.search(q = query, count = count)

            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
            
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            return tweets
        except tweepy.TweepError as e:
            print("Error: " + str(e))

    @app.route('/', methods=['GET', 'POST'])        
    def main():
        if request.method == 'POST':
            api = TwitterClient()
            username = request.form['username']
            tweets = api.get_tweets(query = username, count = 200)

            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
            neutraltweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
            
            pos = len(ptweets), "{} %".format(100*len(ptweets)/len(tweets))
            neg = len(ntweets), "{} %".format(100*len(ntweets)/len(tweets))
            neutral = len(neutraltweets), "{} %".format(100*len(tweets)-len(ntweets)+len(ptweets)/len(tweets))

            return render_template('index.html', username=username, ptweets=ptweets, ntweets=ntweets, neutraltweets=neutraltweets, pos=pos, neg=neg, neutral=neutral)
        return render_template('form.html')
    if __name__ == '__main__':
        main()