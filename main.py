#python module
import time,pymongo,threading,json, concurrent.futures
from flask import Flask,request,jsonify
import tweepy
import pandas as pd
import sys
import csv
import pickle
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from collections import Counter
app = Flask(__name__)
    
consumer_key = ""
consumer_secret = "" 
access_key = ""
access_secret = "" 

def percentage(part,whole):
     return 100 * float(part)/float(whole)

def twitter_setup():

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    try:
        api.verify_credentials()
        print("Successful Authentication")
    except:
        print("Failed authentication")
    return api


extractor = twitter_setup()


def keywords_tweets(api, keyword, number_of_tweets):
    new_keyword = keyword + " -filter:retweets"
    tweets = []
    for status in tweepy.Cursor(api.search_tweets, q=new_keyword, 
                                lang="en", tweet_mode='extended', 
                                result_type='mixed').items(number_of_tweets):
          tweets.append(status)
    return tweets

if (not api):
    print("Problem Connecting to API")


@app.route('/api', methods = ['GET', 'POST'])

def query_model():
  req_data = request.get_json()
  hash_tag = req_data['hash_tag']
  number = req_data['number']
  location = req_data['location']

  # Grab Currrent Time Before Running the Code

   # Scrape tweets based on keywords
  keyword_alltweets = keywords_tweets(extractor,hash_tag, number)



  data = pd.DataFrame(data=[tweet.full_text for tweet in keyword_alltweets],columns=['Tweets'])
  data['Tweets_ID'] = [tweet.id for tweet in keyword_alltweets]
  data['Date'] = [tweet.created_at for tweet in keyword_alltweets]
  data['Source'] = [tweet.source for tweet in keyword_alltweets]
  data['Likes_no'] = [tweet.favorite_count for tweet in keyword_alltweets]
  data['Retweets_no'] = [tweet.retweet_count for tweet in keyword_alltweets]
  data['Location'] = [tweet.user.location for tweet in keyword_alltweets]
  data['UID'] = [tweet.user.id for tweet in keyword_alltweets]
  data['Username'] = [tweet.user.screen_name for tweet in keyword_alltweets]
  data['DisplayName'] = [tweet.user.name for tweet in keyword_alltweets]
  data['Verified'] = [tweet.user.verified for tweet in keyword_alltweets]  
  data['ProfileLink'] = [tweet.user.screen_name for tweet in keyword_alltweets]
  data['Tweet_URL'] = [tweet.id_str for tweet in keyword_alltweets]
  for i in range(len(keyword_alltweets)):
       data['Tweet_URL'][i]="https://twitter.com/"+data['ProfileLink'][i] +"/status/"+data['Tweet_URL'][i]
       data['ProfileLink'][i] = "https://twitter.com/" + data['ProfileLink'][i]  
  data.to_csv('file1.csv')
  positive = 0
  negative = 0
  neutral = 0
  polarity = 0
  tweet_list = []
  neutral_list = []
  negative_list = []
  positive_list = []
  for tweet in data['tweets']:
   
   #print(tweet.text)
      analysis = TextBlob(tweet)
      score = SentimentIntensityAnalyzer().polarity_scores(tweet)
      neg = score['neg']
      neu = score['neu']
      pos = score['pos']
      comp = score['compound']
      polarity += analysis.sentiment.polarity
      
      if neg > pos:
          negative_list.append(tweet)
          negative += 1
      elif pos > neg:
          positive_list.append(tweet)
          positive += 1
          
      elif pos == neg:
          neutral_list.append(tweet)
          neutral += 1
      return positive,negative,neutral,polarity


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)


