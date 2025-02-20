import json
import requests
import sys
import os
import tweepy
from datetime import date,datetime
from dateutil.relativedelta import relativedelta


def is_feb_29(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.month == 2 and date_obj.day == 29
    except ValueError:
        return False


def todayto1yrs():
    tdate= date.today()-relativedelta(days=1)
    if(is_feb_29(str(tdate))):
        ldate=tdate-relativedelta(years=4)
        return([str(tdate),str(ldate)])
    else:
        ldate=tdate-relativedelta(years=1)
        return([str(tdate),str(ldate)])


def storedata(dateval,jsonData,x,lat,lon):
    date_obj = datetime.strptime(str(dateval), '%Y-%m-%d')
    formatted_date = date_obj.strftime('%b%Y')
    filename=f'{formatted_date}.json'
    path=filename
    check=os.path.isfile(path)

    if(x!=200):
        v={dateval:[{f'{lat},{lon}':x}]}
    else:
        v={dateval:[{f'{lat},{lon}':jsonData}]}

    if (check==True):

        with open(filename,'r') as file:
            data=json.load(file)

        if(x!=200):
            data[dateval].append({f'{lat},{lon}':x})
        else:
            if dateval in data.keys():
                data[dateval].append({f'{lat},{lon}':jsonData})
            else:
                data[dateval]=[{f'{lat},{lon}':jsonData}]

        with open(filename,'w') as file:
            data=json.dump(data,file)
    else:
        with open(filename,'w') as file:
            data=json.dump(v,file)


def store(dateval,jsonData,lat,lon):
    date_obj = datetime.strptime(str(dateval), '%Y-%m-%d')
    formatted_date = date_obj.strftime('%b%Y')
    filename=f'{formatted_date}.json'
    path=filename
    check=os.path.isfile(path)

    if (check==True):

        with open(filename,'r') as file:
            data=json.load(file)
            data[dateval]=jsonData[dateval]

        '''if(x!=200):
            data[dateval].append({f'{lat},{lon}':x})
        else:
            if dateval in data.keys():
                data[dateval].append({f'{lat},{lon}':jsonData})
            else:
                data[dateval]=[{f'{lat},{lon}':jsonData}]'''

        with open(filename,'w') as file:
            data=json.dump(data,file)
    else:
        with open(filename,'w') as file:
            data=json.dump(jsonData,file)

def findmean(dateval):
    date_obj = datetime.strptime(str(dateval), '%Y-%m-%d')
    formatted_date = date_obj.strftime('%b%Y')
    with open(f'{formatted_date}.json', 'r') as result:
        jsonData = json.load(result)

    temp = []
    
    for i in range(len(jsonData[dateval])):
        for key in jsonData[dateval][i]:
            # Check if the value is a dictionary (valid API response)
            if isinstance(jsonData[dateval][i][key], dict) and 'days' in jsonData[dateval][i][key]:
                t = jsonData[dateval][i][key]['days'][0]['temp']
                temp.append(t)
    
    # Ensure temp list is not empty before calculating mean
    if len(temp) == 0:
        raise ValueError(f"No valid temperature data found for {dateval}")

    return sum(temp) / len(temp)

'''def findmean(dateval):
    date_obj = datetime.strptime(str(dateval), '%Y-%m-%d')
    formatted_date = date_obj.strftime('%b%Y')
    with open(f'{formatted_date}.json','r') as result:
        jsonData = json.load(result)
    temp=[]
    t=0
    for i in range(len(jsonData[dateval])):
        for key in jsonData[dateval][i]:
            t=jsonData[dateval][i][key]['days'][0]['temp']
            temp.append(t)
        #print(temp)
    m=0
    for i in range(len(temp)):
        m=m+temp[i]
    return(m/len(temp))'''

print('Bot has been Activated')
datelist=todayto1yrs()
print(f"Today's date = {datelist[0]}")
filename='Earthgrid432.json'
with open(filename,'r') as file:
    datao=json.load(file)
   # print(data)
visualcrossingapi=os.getenv('visualcrossingapi')
lat,lon=None,None
for dat in datelist:
    dateval=dat
    datasa={}
    mol=0
    for key in datao:
        mol=mol+1
        #print(data[key])
        lat=datao[key][0]
        lon=datao[key][1]
        response = requests.request("GET", f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat}%2C{lon}%20/{dateval}/{dateval}?unitGroup=metric&include=days&key={visualcrossingapi}&contentType=json')
        if response.status_code!=200:
            #storedata(dateval,None,response.status_code,lat,lon)
            if mol==1:
                datasa[dateval]=[{f'{lat},{lon}':response.status_code}]
            else:
                datasa[dateval].append({f'{lat},{lon}':response.status_code})
        else:
            #Parse the results as JSON
            jsonData = response.json()
            #storedata(dateval,jsonData,response.status_code,lat,lon)
            if mol==1:
                datasa[dateval]=[{f'{lat},{lon}':jsonData}]
            else:
                datasa[dateval].append({f'{lat},{lon}':jsonData})
    store(dateval,datasa,lat,lon)
    print(f'Weather data for {dateval} stored')


tempdiff=round(findmean(datelist[0])-findmean(datelist[1]),2)
print(f'Temperature difference calculate is {tempdiff}')

# Access environment variables
bearer_token = os.getenv('bearer_token')

# Define your API keys and tokens
consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

# Create a client object
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key = consumer_key,
    consumer_secret = consumer_secret,
    access_token = access_token,
    access_token_secret = access_token_secret,
)

def post_tweet(tweet_text):
    try:
        response = client.create_tweet(text=tweet_text)
        print("Tweet posted successfully!")
        #print(response)
    except tweepy.TweepyException as e:
        print("Error occurred:", e)
tweet_text='error'
if __name__ == "__main__":
    if(tempdiff>0):
        tweet_text = f"Breaking: 🌍 Today Earth's average temperature has increased by {tempdiff}°C compared to last year."
    elif(tempdiff<0):
        tempdiff=tempdiff*-1
        tweet_text = f"Breaking: 🌍 Today Earth's average temperature is down by {tempdiff}°C compared to last year."
    else:
        tweet_text = "Today Earth's temperature is the same as last year"
    print('Posting.........')
    post_tweet(tweet_text)

print(f'{tweet_text} - posted successfully!')
