from tweepy import API 
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        consumer_key = 'UY3UFPnHRrm1azphovjSf6R4W'
        consumer_secret = 'yBYsvvWkrOB5acqXbR4NeTPwCUIuhn1SoGXP5BqPiOHvh5xo08'
        access_token = '1151717288-wVmXm7BA8tI0Hz1HWFOFY076ohK504yPgXZkIR0'
        access_token_secret = 'aHs19iVkx1Bzg8L5rdMUjBnr0hCthjwtePwOKlLkIcWP2'
        try:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            return auth
        except:
            print("Error: Authentication Failed")


class TwitterStreamer():

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


class TweetAnalyzer():

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.polarity

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.full_text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df

 
if __name__ == '__main__':

    # # # # # PERFORM SENTIMENT ANALYSIS # # # # #

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    bbc_tweets = api.user_timeline(screen_name="BBC", count=100, exclude_replies=True, include_rts = False, tweet_mode="extended")
    df = tweet_analyzer.tweets_to_data_frame(bbc_tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    bbc_score = round(sum(df['sentiment'])/len(bbc_tweets), 3)

    cbc_tweets = api.user_timeline(screen_name="CBCNews", count=100, exclude_replies=True, include_rts = False, tweet_mode="extended")
    df = tweet_analyzer.tweets_to_data_frame(cbc_tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    cbc_score = round(sum(df['sentiment'])/len(cbc_tweets), 3)

    cnn_tweets = api.user_timeline(screen_name="CNN", count=100, exclude_replies=True, include_rts = False, tweet_mode="extended")
    df = tweet_analyzer.tweets_to_data_frame(cnn_tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    cnn_score = round(sum(df['sentiment'])/len(cnn_tweets), 3)

    ctv_tweets = api.user_timeline(screen_name="CTVNews", count=100, exclude_replies=True, include_rts = False, tweet_mode="extended")
    df = tweet_analyzer.tweets_to_data_frame(ctv_tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    ctv_score = round(sum(df['sentiment'])/len(ctv_tweets), 3)

    fox_tweets = api.user_timeline(screen_name="FoxNews", count=100, exclude_replies=True, include_rts = False, tweet_mode="extended")
    df = tweet_analyzer.tweets_to_data_frame(fox_tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    fox_score = round(sum(df['sentiment'])/len(fox_tweets), 3)

    global_tweets = api.user_timeline(screen_name="globalnews", count=100, exclude_replies=True, include_rts = False, tweet_mode="extended")
    df = tweet_analyzer.tweets_to_data_frame(global_tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    global_score = round(sum(df['sentiment'])/len(global_tweets), 3)

    print('\033[1m' + 'Sentiment Scores')
    print('\033[0m' + 'BBC:', bbc_score)
    print('CBC:', cbc_score)
    print('CNN:', cnn_score)
    print('CTV:', ctv_score)
    print('Fox:', fox_score)
    print('Global:', global_score)

    # # # # # VISUALIZE RESULTS # # # # #

    scores = (bbc_score, cbc_score, cnn_score, ctv_score, fox_score, global_score)

    ind = np.arange(len(scores))
    width = 0.35

    fig, ax = plt.subplots()
    graph = ax.bar(ind, scores, align = 'center', color = 'SkyBlue')

    ax.set_ylabel('Sentiment Score')
    ax.set_title('Sentiment Scores of News Outlets (based on last 100 tweets)')
    ax.set_xticks(ind)
    ax.set_xticklabels(('BBC', 'CBC', 'CNN', 'CTV', 'Fox', 'Global'))

    for bar in graph:
        ax.text(bar.get_x() + bar.get_width()*0.5, bar.get_height(), bar.get_height(), ha='center', va='bottom')

    plt.show()

