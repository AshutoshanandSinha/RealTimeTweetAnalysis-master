#!/usr/bin/env python
__author__ = 'chandra Shekhar'

# It extracts text and subset of the JSON object fields from  running Twitter stream in JSON format,  (e.g., date, id, hashtags, urls, text)
# Then it calculates the average degree of hastags in last 60 seconds of tweet messages
# How to run:
# python #cur_file.py  json/tweet/store/path tweet/store/path avg/degree/path


# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import os
import itertools
import redis
import time
import sys

# loads Twitter credentials from .twitter file that is in the same directory as this script
file_dir = os.path.dirname(os.path.realpath(__file__)) 

try:
    with open(file_dir + '/../data-gen/.twitter') as twitter_file:
        twitter_cred = json.load(twitter_file)
except:
    print("issue in loading .twitter file"+ file_dir + '/../data-gen/.twitter')
    sys.exit(0)

if len(sys.argv) < 5:
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
else:
    redisport = int(sys.argv[3])
    print redisport
    r = redis.StrictRedis(host='localhost', port=redisport, db=0)


# authentication from the credentials file above
access_token = twitter_cred["access_token"]
access_token_secret = twitter_cred["access_token_secret"]
consumer_key = twitter_cred["consumer_key"]
consumer_secret = twitter_cred["consumer_secret"]


'''parse json tweets and return tweet, time and hastags'''


def parse_json_tweet(line):
    tweet = json.loads(line)

    date = tweet['created_at']
    id = tweet['id']
    nfollowers = tweet['user']['followers_count']
    nfriends = tweet['user']['friends_count']


    if 'retweeted_status' in tweet:
        tweet_text = tweet['retweeted_status']['text']
    else:
        tweet_text = tweet['text']
    tweet_text = tweet_text.replace('\r', ' ')
    tweet_text = tweet_text.replace('\n', ' ')

    hashtags = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]

    return [date, id, tweet_text, hashtags, nfollowers, nfriends]


'''Avergae graph degree calculation Logic in Readme file'''


def avggraphdegree(r,hash, hashpair, tweet_unixtime_prev, tweet_unixtime ):
    edgecount = r.zcount(hashpair,tweet_unixtime_prev,tweet_unixtime)
    if edgecount <= 0:
        return 0
    nodecount = r.zcount(hash,tweet_unixtime_prev,tweet_unixtime)
    return round(float(edgecount) *2.0/ nodecount,2)

'''clean the hastags and return valid hashtag list'''


def cleanhashtags(hashtags, cleantags):
    for i in range(len(hashtags)):
        hashtags[i] = hashtags[i].encode('ascii','ignore')
        hashtags[i] = hashtags[i].lower().strip()
        if(hashtags[i] == ''):
            continue
        cleantags.append(hashtags[i])

'''Add hastags in redis db'''

def redis_add(r,cleantags, tweet_unixtime, hash):
    for i in range(len(cleantags)):
        r.zadd(hash,tweet_unixtime, cleantags[i])


'''Add hastags tuples in redis db'''

def redis_add_pair(r,cleantags, tweet_unixtime, hashpair):
    for subset in itertools.combinations(cleantags, 2):
        tags = sorted(subset)
        tags2 =  str(tags[0]) + ' ' + str(tags[1])
        if (tags[0] == tags[1]):
            continue;
        r.zadd(hashpair, tweet_unixtime, tags2)


def hashtaggraphdegree(json_tweets, runninghash, runninghashpair):

    try:
        [tweet_gmttime, tweet_id, tweet_text, hashtags,  nfollowers, nfriends] = parse_json_tweet(json_tweets)
        if not tweet_gmttime: return  # no timestamp, no degree calculation

        # text crunching
        if tweet_text:
            tweet_ascii = tweet_text.encode('ascii','ignore')
            text = ' '.join(tweet_ascii.split())
            print(text)
            with open(sys.argv[2], 'a') as output_file:
                output_file.write(text + " (timestamp: " + str(tweet_gmttime) + ")\n");

        # time crunching
        try:
            c = time.strptime(tweet_gmttime.replace("+0000",''), '%a %b %d %H:%M:%S %Y')
        except:
            print (tweet_gmttime)
            return
        tweet_unixtime = int(time.mktime(c))
        tweet_unixtime_prev = tweet_unixtime - 60;

        # get tags
        cleantags = []
        cleanhashtags(hashtags, cleantags)

        #get degree
        if ((len(cleantags)<=1) or (not cleantags)):
            with open(sys.argv[3], 'a') as output_file:
                output_file.write(str(avggraphdegree(r,runninghash, runninghashpair, tweet_unixtime_prev, tweet_unixtime )) + "\n");
            return

        redis_add(r,cleantags, tweet_unixtime, runninghash )
        redis_add_pair(r,cleantags, tweet_unixtime,  runninghashpair )

        with open(sys.argv[3], 'a') as output_file:
            output_file.write(str(avggraphdegree(r,runninghash, runninghashpair, tweet_unixtime_prev, tweet_unixtime )) + "\n");

    except:
    #escape rate limit messages
        pass

def callhashtaggraphdegree(data):
    hashtaggraphdegree(data, 'runninghash', 'runninghashpair')


class StdOutListener(StreamListener):
    """ A listener handles tweets that are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, filename):
        self.filename = filename

    # this is the event handler for new data
    def on_data(self, data):
        if not os.path.isfile(self.filename):    # check if file doesn't exist
            f = file(self.filename, 'w')
            f.close()
        with open(self.filename, 'ab') as f:
            #print "writing to {}".format(self.filename)
            f.write(data)
            callhashtaggraphdegree(data)

        f.closed
        
    # this is the event handler for errors    
    def on_error(self, status):
        print(status)

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print ("Error: Params missing")
        print (str("Usage: python " +  __file__ + " /path/to/store/json/tweet path/to/store/tweet path/to/store/degree optional_param_port"))
        sys.exit(0)
    else:
        try:
            open(sys.argv[0], 'r')
        except:
            print "Source File doesnt exists ", sys.argv[0]
            sys.exit(0)

    r.delete('runninghash')
    r.delete('runninghashpair')

    with open(sys.argv[2], 'w') as f:
        pass
    with open(sys.argv[3], 'w') as f:
        pass


    listener = StdOutListener(sys.argv[1])
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print "Use CTRL + C to exit at any time.\n"
    stream = Stream(auth, listener)
    stream.filter(locations=[-180,-90,180,90]) # this is the entire world, any tweet with geo-location enabled
