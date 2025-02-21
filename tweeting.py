import json
import os
import tweepy
from datetime import datetime
from dateutil.relativedelta import relativedelta

def findmean(dateval):
    date_obj = datetime.strptime('2025-02-19', '%Y-%m-%d')
    formatted_date = date_obj.strftime('%b%Y')
    file_path = f'{formatted_date}.json'

    try:
        with open(file_path, 'r') as result:
            jsonData = json.load(result)
            print(jsonData)
    except FileNotFoundError:
        raise ValueError(f"File {file_path} not found! No data available for {dateval}")

    temp = []
    for i in range(len(jsonData.get(dateval, []))):
        for key in jsonData[dateval][i]:
            if isinstance(jsonData[dateval][i][key], dict) and 'days' in jsonData[dateval][i][key]:
                t = jsonData[dateval][i][key]['days'][0]['temp']
                temp.append(t)

    if len(temp) == 0:
        print(f"❌ No valid temperature data found for {dateval}")
        raise ValueError(f"No valid temperature data found for {dateval}")

    return sum(temp) / len(temp)

if __name__ == "__main__":
    print("Processing stored weather data...")

    datelist = [str(datetime.today().date() - relativedelta(days=2)), str(datetime.today().date() - relativedelta(years=1))]
    tempdiff = round(findmean(datelist[0]) - findmean(datelist[1]), 2)
    
    print(f'Temperature difference calculated: {tempdiff}')

    # Load Twitter API credentials from GitHub Secrets
    bearer_token = os.getenv('BEARER_TOKEN')
    consumer_key = os.getenv('CONSUMER_KEY')
    consumer_secret = os.getenv('CONSUMER_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    def post_tweet(tweet_text):
        try:
            response = client.create_tweet(text=tweet_text)
            print("✅ Tweet posted successfully!")
        except tweepy.TweepyException as e:
            print("❌ Error occurred:", e)

    tweet_text = 'error'
    if tempdiff > 0:
        tweet_text = f"Breaking: 🌍 Today's Earth's average temperature has increased by {tempdiff}°C compared to last year."
    elif tempdiff < 0:
        tempdiff = abs(tempdiff)
        tweet_text = f"Breaking: 🌍 Today's Earth's average temperature is down by {tempdiff}°C compared to last year."
    else:
        tweet_text = "Today Earth's temperature is the same as last year."

    print('Posting tweet...')
    post_tweet(tweet_text)
    print(f'{tweet_text} - posted successfully!')
