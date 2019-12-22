#! /usr/bin/env python
__author__ = 'chandra Shekhar'

# It extracts text and subset of the JSON object fields from Twitter stream in JSON format,  (e.g., date, id, hashtags, urls, text)
# Then it calculates the average degree of hastags in last 60 seconds of tweet messages
# How to run:
#  python #cur_file.py  src/file/path dest/file/path

import codecs
import json
import sys
import itertools
import redis
import time


'''parse json tweets and return tweet, time and hastags'''

def parse_json_tweet(line):
    tweet = json.loads(line)

    date = tweet['created_at']
    id = tweet['id']
    nfollowers = tweet['user']['followers_count']
    nfriends = tweet['user']['friends_count']

    # get tweet tex
    if 'retweeted_status' in tweet:
        tweet_text = tweet['retweeted_status']['text']
    else:
        tweet_text = tweet['text']
    tweet_text = tweet_text.replace('\r', ' ')
    tweet_text = tweet_text.replace('\n', ' ')

    #get hashtags

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


'''Add hastags tuples  in redis db'''

def redis_add_pair(r,cleantags, tweet_unixtime, hashpair):
    for subset in itertools.combinations(cleantags, 2):
        tags = sorted(subset)
        tags2 =  str(tags[0]) + ' ' + str(tags[1])
        if (tags[0] == tags[1]):
            continue;
        r.zadd(hashpair, tweet_unixtime, tags2)

'''in redis db'''

def hashtaggraphdegree():
    if len(sys.argv) < 4:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
    else:
        redisport = int(sys.argv[3])
        r = redis.StrictRedis(host='localhost', port=redisport, db=0)
    json_tweets = codecs.open(sys.argv[1], 'r', 'utf-8')
    fout = codecs.open(sys.argv[2], 'w', 'utf-8')
    multihashcount = 0
    singlehash = 'redishash'
    hashpair = 'redispairahash'

    #efficient line-by-line read of big files
    for line in json_tweets:
        try:
            [tweet_gmttime, tweet_id, text, hashtags, nfollowers, nfriends] = parse_json_tweet(line)

            if not tweet_gmttime: continue # no timestamp, no degree calculation
            try:
                c = time.strptime(tweet_gmttime.replace("+0000",''), '%a %b %d %H:%M:%S %Y')
            except:
                print (tweet_gmttime)
                continue
            tweet_unixtime = int(time.mktime(c)) # get current unix timestamo
            tweet_unixtime_prev = tweet_unixtime - 60; # get current - 60 second timestamp

            cleantags = []
            cleanhashtags(hashtags, cleantags)  # get clean hashtag list


            #Less than 2 hashtags, just update degree
            if ((len(cleantags)<=1) or (not cleantags)):
                fout.write( str(avggraphdegree(r,singlehash, hashpair, tweet_unixtime_prev, tweet_unixtime )) + "\n");
                continue


            multihashcount+=1
            # More than 1 hashtags, account this new tweet in into graph degree calculation
            redis_add(r,cleantags, tweet_unixtime, singlehash )
            redis_add_pair(r,cleantags, tweet_unixtime,  hashpair )

            fout.write(str(avggraphdegree(r,singlehash, hashpair, tweet_unixtime_prev, tweet_unixtime )) + "\n");

        except:
           #escape rate limit messages
            pass
    r.delete(hashpair)
    r.delete(singlehash)
    fout.close()

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print ("Error: Params missing")
        print (str("Usage: python " +  __file__ + " src/file/path dest/file/path  optional_param_port"))
        sys.exit(0)
    else:
        try:
            open(sys.argv[1], 'r')
        except:
            print "Source File doesnt exists ", sys.argv[1]
            sys.exit(0)

    hashtaggraphdegree()
