import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

x_api_key = os.getenv('x_api_key')
x_api_key_secret = os.getenv('x_api_secret')
x_access_token = os.getenv('x_access_token')
x_token_secret = os.getenv('x_token_secret')

# Create client instead of api
client = tweepy.Client(
    consumer_key=x_api_key,
    consumer_secret=x_api_key_secret,
    access_token=x_access_token,
    access_token_secret=x_token_secret
)

def authentication():
    try:
        # Verify credentials by attempting to get your own user info
        me = client.get_me()
        print("successful authentication")
        return me
    except Exception as e:
        print("error during authentication:", str(e))
        return None

def postTweet(text):
    try:
        # Get user info first
        me = authentication()
        if not me:
            return None
            
        # Add a unique timestamp to prevent duplicate tweets
        
        tweet_text = text
        
        # Post the tweet
        response = client.create_tweet(text=tweet_text)
        
        # Generate the URL using the tweet ID and username
        tweet_id = response.data['id']
        username = me.data.username
        url = f"https://x.com/{username}/status/{tweet_id}"
        
        print(f"Tweet posted: {url}")
        return url
    except Exception as e:
        print("error posting tweet:", str(e))
        return None

def test_credentials():
    try:
        me = client.get_me()
        print(f"Successfully authenticated as: @{me.data.username}")
        print("User ID:", me.data.id)
        return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_credentials()

