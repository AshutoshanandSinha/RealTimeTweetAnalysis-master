##Project Summary

This Project implements two features:

1) Clean and extract the text from the raw JSON tweets that come from the Twitter Streaming API, and track the number of tweets that contain unicode.

2) Calculate the average degree of a vertex in a Twitter hashtag graph for the last 60 seconds, and update this each time a new tweet appears.

##Solution:
The solution has been designed using python language and redis in memeory DS Structure. There are three files.

Source Files:

tweets_cleaned.py - This file cleans the json tweets and prints it. It also tracks number of lines conatining unicode (takes input from a file)

average_degree.py - Calculate the average degree of a vertex in a Twitter hashtag graph for the last 60 seconds (takes input from a file)

runnning_tweets.py - Calculate the average degree of a vertex in a Twitter hashtag graph for the tweet stream (needs twitter credentials)

 Considerations:
    This Solution uses tweepy, redis and python interface to redis (redis.py). 
    Script run.sh assumes that redis will be running on port 6379. if it is running 
    at some port other than 6379, modify the second command in run.sh to add port 
    number in the end.
    
    python src/average_degree.py tweet_input/tweets.txt tweet_output/ft2.txt <redis_port_num>
    
    File stream.sh works on running twitter stream. For it to work place .twitter credential 
    file in data-gen directory. This programs  also assumes that redis will be running 
    on port 6379 if it is running  at some port other than 6379, modify the command in stream.sh 
    to add port number in the end.
    

##  Technologies Used:
    Python, Redis in-memory DS store, tweepy, redis.py (Python interface to Redis key-value)
    Redis has been used because it runs in memeory. we can crate master slave replication to
    provide high availability. It can also provide persistence based on config settings.
    It can be furthe used to store tweets list based on timing.
    Used Pip to install dependencies.
    
    sudo apt-get install python-pip
    sudo pip install tweepy - tweepy
    sudo pip install redis - redis.py 
    redis install - http://redis.io/topics/quickstart
    
    redis.py - (https://github.com/andymccurdy/redis-py) 
    
    tweepy -  (https://github.com/tweepy/tweepy) 
    
    redis - (http://redis.io/topics/quickstart or http://redis.io/download)  
        

## Structure of this repo

            |--------- README.md
            |
            |--------- run.sh
            |
            |--------- stream.sh
            |
            |
            |--------- src
            |           |
            |         average_degree.py           
            |         runnning_tweets.py
            |         tweets_cleaned.py
            |
            |---------tweet_input
            |          |
            |         tweets.txt
            |         jsontweets.txt (for running streams)
            |
            |----------tweet_output
            |           |
            |          ft1.txt
            |          ft2.txt
            |          cleantweets.txt (for running streams)
            |          degree.txt (for running streams)
            |

    
    ft1.txt and ft2.txt are genrated from from already given tweet set in problem. although
    they can be fed any imput. whereas  jsontweets.txt, cleantweets.txt and degree.txt are 
    generated for running twitter stream. I have directed the stream to the two functions
    who do the processing of data along with writing tweets  to tweet_input/jsontweets.txt 
    file. This is done by source file runnning_tweets.py
    
    commands in run.sh can be modified to take any input/output files.
    



##Feature 1:

 Considerations:
        cleaned tweets which turned out empty also have been written (but code is present
        to remove them if needed)

- File: src/tweets_cleaned.py

        This file cleans the json tweets and prints it. It also tracks number of 
        lines containing unicode.
    

- Technologies:

        Python Libraries Used:
    
        codecs
        
        json
        
        sys

- usage: 

        python src/tweets_cleaned.py tweet_input/tweets.txt tweet_output/ft1.txt

- output File

        tweet_output/ft1.txt


- Algorithm: 

    1) Read the json tweet from source file one by one (parse_tweets_for_text function)
    
    2) Extract partially cleaned tweets (tweet_text) and timestamps (tweet_gmttime)
       using parse_json_tweet function
    
    3) Convert to ascii and calculate unicode_count
    
    4) Write to the file "tweet_output/ft1.txt"
    
    5) cleaned tweets which turned out empty also have been written (but code is present
       to remove them if needed)
    
    6) rate limit tweets or tweets without properly formatted timestamps have not been printed


##Feature 2:

 Considerations:
    Make sure redis is running at port 6379 on localhost. option has been give 
    to run on other ports at. See usage.

- File: src/average_degree.py

        This file calculates the average degree of a vertex in a Twitter hashtag graph for the 
        last 60 seconds 

- Technologies:
        Python Libraries Used:
    
        codecs
        
        json
        
        sys
        
        itertools
        
        redis
        
        time
        
        redis.py library  (https://github.com/andymccurdy/redis-py)
        
        Redis in memory DS  (https://pypi.python.org/pypi/redis or http://redis.io/download) 
  
     
- usage: 

        python src/average_degree.py tweet_input/tweets.txt tweet_output/ft2.txt

- output File


        tweet_output/ft2.txt

- optional param redis port:

        python src/average_degree.py tweet_input/tweets.txt tweet_output/ft2.txt  <redis_port if anything other than 6379>
 
- Algorithm: 

        This algorithm doesnt create nodes and vertices of graph. It takes a simplistic approach of
        storing unique pairwsie hashatg tuples for last 60 seconds, and unique hastags for last 60 seconds.
        To get the average degree of graph it just divides the number of unique paiwise hashtag tuple to 
        unique hastags.
        
    1) Read the json tweet from source file one by one (parse_tweets_for_text function).
    
    2) Extract hashtags (hashtags)  and timestamps  (tweet_gmttime) using parse_json_tweet function.
    
    3) Convert timestamps to unix timestamps
    
    4) clean the hashtags (cleantags) (cleanhashtags function)
    
    5) If after cleaning hashtag set becomes empty or if it has  just 1 hashtag then we dont need 
       to change graph just update the degree of graph for (current time - 60 sec) 
       using (avggraphdegree function)
        
    6) if there are more than 1 hashtag in a tweet then insert the new hashtags in redis 
       (redis_add and redis_add_pair function )and update to degree  of graph
       using (avggraphdegree function)
    
    7) Logic for calculating graphdegree and inserting in redis 
        
        Redis sorted set data structure have been used.  Redis Sorted Sets are non repeating
        collections of Strings. Each member of Sorted Set is associated with score (in this 
        case timestamp), that is used in order to make set ordered, from the smallest
        to the greatest score. In my sorted set  hashtags and hashtag pairs 
        (basically graph edges) will be stored in  two diffrenet sorted set (redishash,
        redispairahash) in increasing order of timestamps.
        
        item 1) hashtags = individual hashtags from tweet  
        
        item 2) hashtagpairs = combination of two hashtags from hashtags (item 1)
        
        item 3) redishash  = redis sorted set storing non duplicate 
                            hashtags (item 1) in increasing order of timestamp 
                            
        item 4) redispairahash = redis sorted set storing non duplicate
                            hashtagpairs (item 2) in increasing order of timestamp

        If a tweets contains  one or less hashtag after cleaning,  that tweets doesnt affect 
        either of the two sorted data set (redishash, redispairahash). it just updates 
        average graph degree. 

        If a  tweet contains two or more hashtags after cleaning:
        insert the hashtag and hastag pairs in corresponding dbs (redishash, 
        redispairahash) with the timestamps
       
        If 
                hashtag or hashtagpairs are already there in their sorted sets then sets will 
                automatically put it in sorted order using new timestamp. (basically 
                remove previous occurrnce and add new ones)
        else   
              just insert with new timestamp  
        
        hashtagpairs_in_last_60_sec = get number of entries from redispairahash for 
                                    (current_tweet_time - 60 sec) 
        
        hashtag_in_last_60 = get number of entries from
                            redishash for (current_tweet_time - 60 sec) 
        
        calculating degree = (hashtagpairs_in_last_60_sec  * 2.0) / hashtag_in_last_60
        
        e.g lets say we have two hastags in tweets 
        #apache #hadoop
        
        instead of storing both (apache hadoop) and (hadoop apache), store only one of them.
        This is done to conserve memory. The pairs are stored themselves in sorted order.
        so It will always be  stored as (apache hadoop) and not (hadoop apache). 
        Any future tweets containing the two words will store it as (apache hadoop) 
        and if it is already there in redispairahash they will update the timestamp. 
        since only one pair is being stored we need to  multiple by two to calculate
        the degree.
        
    
    8) rate limit tweets or tweets without properly formatted timestamps have not used
    9) some tweets do not arrive in correct which degree might seem out of place from degree of previous tweets


##Feature 3:

    put .twitter credential file in data-gen directory for this test to run.
    Make sure redis is running at port 6379 on localhost. another option has 
    been give to run on other ports. see usage
    same content as above two files but uses incoming twitter stream. 

- File: src/running-tweets.py
        This file calculates the average degree of a vertex in a Twitter hashtag graph twitter stream
        same content as above two files but uses incoming twitter stream. 

Technologies:

    - Python Libraries Used:
    
        codecs
        
        json
        
        sys
        
        itertools
        
        redis
        
        time
        
        redis.py library - https://github.com/andymccurdy/redis-py
        
        tweepy - https://github.com/tweepy/tweepy
        
    - Redis in memory DS     


- usage: 

        python src/runnning_tweets.py tweet_input/jsontweets.txt tweet_output/cleantweets.txt tweet_output/degree.txt

output File

        tweet_input/jsontweets.txt 
        
        tweet_output/cleantweets.txt 
        
        tweet_output/degree.txt    

optional param redis port:
    python src/runnning_tweets.py tweet_input/jsontweets.txt tweet_output/cleantweets.txt tweet_output/degree.txt <redis_port_if_other_than 6379>
 
Algorithm: 
    
    1) start twitter stream and log the json tweets  to a file.  after pass it for furthe tweet
        and graph processing 

    2) After step 1 functionality is borrowed from previous two features. So skipping.