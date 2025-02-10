import os

import bot
# Remove this line since we won't use dotenv
# from dotenv import load_dotenv
from flask import Flask, request, render_template
from openai import OpenAI
from functools import lru_cache
from dotenv import load_dotenv
import hashlib

app = Flask(__name__)

#for devlopment purposes, REMOVE BEFORE PROD
load_dotenv()

# Add this line
cached_responses = {}

conversation_history=[]

# Remove these lines since we're not using .env



# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

def validate_api_key():
    if not api_key:
        return "API key not found. Please check your .env file."
    return True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/new_search')
def new_search():
    # Clear or reinitialize the conversation history for a new thread.
    global conversation_history
    conversation_history = []
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    post_to_twitter = request.form.get('post_to_twitter') == 'on'
    validation_result = validate_api_key()
    
    if validation_result is True:
        try:
            html_message, tweet_text = prompt(query)
            conversation_history.append({'sender':'user', 'message': query})
            conversation_history.append({'sender':'eli5', 'message': html_message})
            
            # Only post to Twitter if user consented
            tweet_url = None
            if post_to_twitter:
                tweet_url = bot.postTweet(tweet_text)
            
            return render_template('response.html', 
                                conversation=conversation_history, 
                                tweet_url=tweet_url)
        except Exception as e:
            print(f"Error in search route: {str(e)}")
            return render_template('index.html', 
                                error="An error occurred while processing your request.")
    else:
        return render_template('index.html', error=validation_result)

@app.route("/continue", methods=['POST'])
def continueConvo():
    query = request.form.get('query')
    post_to_twitter = request.form.get('post_to_twitter') == 'on'
    
    if query:
        conversation_history.append({'sender':'user', 'message':query})

        try:
            html_message, tweet_text = prompt(query)
            conversation_history.append({'sender':'eli5', 'message':html_message})
            
            # Only post to Twitter if user consented
            tweet_url = None
            if post_to_twitter:
                tweet_url = bot.postTweet(tweet_text)
            
            return render_template('response.html', 
                                conversation=conversation_history,
                                tweet_url=tweet_url)
        except Exception as e:
            conversation_history.append({'sender':'user', 'message':'An error occurred'})
        return render_template('response.html', conversation=conversation_history)

@lru_cache(maxsize=100)
def get_cached_response(query_hash):
    return cached_responses.get(query_hash)

def prompt(query):
    query_hash = hashlib.md5(query.encode()).hexdigest()
    
    cached_response = get_cached_response(query_hash)
    if cached_response:
        return cached_response['html'], cached_response['tweet']
    
    client = OpenAI(api_key=api_key)
    
    # First, get a tweet-friendly response
    tweet_prompt = """Explain this topic like I'm 5 years old, but don't address me as a 5 year old. Keep it under 280 characters: {query}"""
    
    tweet_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": tweet_prompt.format(query=query)}],
        max_tokens=150
    )
    
    tweet_text = tweet_response.choices[0].message.content
    
    # Then, get the formatted HTML response
    html_prompt = """Explain this topic like I'm 5 years old, but don't address me as a 5 year old:
{query}

Your response MUST include at least:
1. One <div class="key-point">Important takeaway: [your key point here]</div>
2. One <div class="example">Example: [your example here]</div>

Also use these for emphasis:
- <strong> for important terms
- <em> for emphasis
- Bullet points or numbers for lists where appropriate"""

    html_response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": html_prompt.format(query=query)}],
        max_tokens=500
    )
    
    html_text = html_response.choices[0].message.content
    
    # Cache both responses
    cached_responses[query_hash] = {
        'html': html_text,
        'tweet': tweet_text
    }
    
    return html_text, tweet_text

if __name__ == '__main__':
    app.run(debug=True)

"""
Some portions of this code are adapted from:
Repository: [ELI5]
Author: [Sujan30]

Link: [https://github.com/Sujan30/Eli5]
""" 