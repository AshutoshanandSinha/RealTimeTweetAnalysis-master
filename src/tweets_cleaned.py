#! /usr/bin/env python
__author__ = 'chandra shekhar'


# It extracts text and subset of the JSON object fields from Twitter stream in JSON format,  (e.g., date, id, hashtags, urls, text)
# Then it calculates the average degree of hastags in last 60 seconds of tweet messages
# How to run:
#  python #cur_file.py  src/file/path dest/file/path

import codecs
import json
import sys



'''parse json tweets and return tweet, time and hastags'''

def parse_json_tweet(line):
    tweet = json.loads(line)

    date = tweet['created_at']

	#get tweet text
    if 'retweeted_status' in tweet:
        tweet_text = tweet['retweeted_status']['text']
    else:
        tweet_text = tweet['text']

    tweet_text = tweet_text.replace('\r', ' ')
    tweet_text = tweet_text.replace('\n', ' ')

	#get hashtags
    hashtags = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]

    return [date, tweet_text, hashtags]


'''clean tweet and find unicode tweets'''

def parse_tweets_for_text():
    json_tweets = codecs.open(sys.argv[1], 'r', 'utf-8')
    fout = codecs.open(sys.argv[2], 'w', 'utf-8')
    unicode_count = 0;
    #efficient line-by-line read of big files
    for line in json_tweets:
        try:
            [tweet_gmttime, tweet_text, hashtags] = parse_json_tweet(line)

            if not tweet_gmttime: continue #no timstamp, To add or not to add, No
            if not tweet_text: continue # No tweet from json, What would you print

            tweet_ascii = tweet_text.encode('ascii','ignore')
            if (len(tweet_text) != len(tweet_ascii)): #track unicde count
                unicode_count += 1;
#           Uncomment if empty tweets not to be printed
#           For empty tweets
#			text = tweet_ascii.strip()
# 			if not text: continue

            text = ' '.join(tweet_ascii.split())
            text = text.replace('# ', ' ')
            fout.write(str(text ) + " (timestamp: " + str(tweet_gmttime) + ")\n");
        except:
            # escape rate limit messages and other non json
            pass
    fout.write("\n" + str(unicode_count) + " tweets contained unicode.")
    fout.flush()
    fout.close()

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print ("Error: Params missing")
        print (str("Usage: python " +  __file__ + " src/file/path dest/file/path"))
        sys.exit(0)
    else:
        try:
            open(sys.argv[1], 'r')
        except:
            print "Source File doesnt exists ", sys.argv[1]
            sys.exit(0)
	parse_tweets_for_text()
