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
    
consumer_key =''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

if (not api):
    print("Problem Connecting to API")


@app.route('/api', methods = ['GET', 'POST'])

def query_model():
  req_data = request.get_json()
  hash_tag = req_data['hash_tag']
  number = req_data['number']
  location = req_data['location']

  places = api.geo_search(query=location)

  print(places[0])

  tweetsPerQry = 100  

  sinceId = None


  max_id = -1
  data = None

  dataset = []
  outputFile = 'test.data'
  fw = open(outputFile, 'wb')

  tweetCount = 0
  print("Downloading max {0} tweets".format(number))
  while tweetCount < number:
      try:
          if (max_id <= 0):
              if (not sinceId):
                  new_tweets = api.search(q=hash_tag, count=tweetsPerQry, tweet_mode='extended', lang='en')
                  tweetCount += len(new_tweets)
                  print("Downloaded {0} tweets".format(tweetCount))
              else:
                  new_tweets = api.search(q=hash_tag, count=tweetsPerQry,
                                          since_id=sinceId, tweet_mode='extended', lang='en')
                  print("here 2")
          else:
              if (not sinceId):
                  new_tweets = api.search(q=hash_tag, count=tweetsPerQry,
                                          max_id=str(max_id - 1), tweet_mode='extended', lang='en')
                  print("here 3")
              else:
                  new_tweets = api.search(q=hash_tag, count=tweetsPerQry,
                                          max_id=str(max_id - 1),
                                          since_id=sinceId, tweet_mode='extended', lang='en')
                  print("here 4")
              if not new_tweets:
                  print("No more tweets found")
                  break

          # print(new_tweets)

          tweets = new_tweets
          for tweet in tweets:
              dataset.append(tweet.full_text)
          #data += pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
          tweetCount += len(new_tweets)
          print("Downloaded {0} tweets".format(tweetCount))
          max_id = new_tweets[-1].id
      except tweepy.TweepError as e:
          print(str(e))
          break


  pickle.dump(dataset, fw)
  fw.close()
  import nltk
  inputFile = 'test.data'
  fd = open(inputFile, 'rb')
  dataset = pickle.load(fd)
  print(dataset)



  nltk.download('vader_lexicon')

  sid = SentimentIntensityAnalyzer()


  l = []
  counter = Counter()

  for data in dataset:
      ss = sid.polarity_scores(data)
      l.append(ss)
      k = ss['compound']
      if k >= 0.05:
          counter['positive'] += 1
      elif k <= -0.05:
          counter['negative'] += 1
      else:
          counter['neutral'] += 1

  positive = counter['positive']
  negative = counter['negative']
  neutral = counter['neutral']

  return positive,negative,neutral
if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)


