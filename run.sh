#!/usr/bin/env bash

# I'll execute my programs, with the input directory tweet_input and output the files in the directory tweet_output
# These command can be modified to used any input file and output files.

python src/tweets_cleaned.py tweet_input/tweets.txt tweet_output/ft1.txt

python src/average_degree.py tweet_input/tweets.txt tweet_output/ft2.txt

