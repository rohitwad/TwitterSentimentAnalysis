from flask import Flask, request, jsonify, render_template
import pickle
from pickle import load
import pandas as pd
import numpy as np
import tweepy
import re
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import webbrowser


ApiKey='ZIzq9YljAtAbK8286pU59JhfA'
ApiKeySecret='hvwtuuEb8kJ9DGnx8ar86FyAS4G1SrJmHH1GMptWHpSFFGqare'
AccessToken='2588927641-L4WOSIg90LhBcmo4i4cVH7STU4zblaSSMWUk9pq'
AccessTokenSecret='rMK2IbDqov386ERvcsbQvJMPDKjek7IrmLfcyIS0x1yxm'

authenticate=tweepy.OAuthHandler(ApiKey,ApiKeySecret)
authenticate.set_access_token(AccessToken,AccessTokenSecret)
api=tweepy.API(authenticate, wait_on_rate_limit=True)


appFlask=Flask(__name__)
# load the model
# Sentiment_Analysis = load(open('Logistic_CCLP.pkl', 'rb')


@app.route('/')
def home():
    return render_template('index.html')


def cleanText(text):
    text=re.sub(r'@[A-Za-z0-9]+','',text) # Removing @mentions
    text=re.sub(r'#','',text) # Removing the # symbol
    text=re.sub(r'RT[\s]+','',text) # Removing RT & immediate space after it, RT symbolises Retweet
    text=re.sub(r'https?:\/\/','',text) # Removing the hyperlink
    return text

def getSubjectivity(text): # Create a function to get subjectivity
    return TextBlob(text).sentiment.subjectivity

def getPolarity(text): # Create a function to get Polarity
    return TextBlob(text).sentiment.polarity

# Creating function to find tweet reflects Negative/Neutral/Positive Sentiment
def getAnalysis(score):
    if score<0:
        return 'Negative'
    elif score==0:
        return 'Neutral'
    else :
        return 'Positive'
    
def generate_html(dataframe: pd.DataFrame):
    # get the table HTML from the dataframe
    table_html = dataframe.to_html(table_id="table")
    # construct the complete HTML with jQuery Data tables
    # You can disable paging or enable y scrolling on lines 20 and 21 respectively
    html = f"""
    <html>
    <header>
        <link rel="stylesheet" type="text/css" href="http://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css" />
    </header>
    <body>
    {table_html}
    <script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready( function () {{
            $('#table').DataTable({{
                // paging: false,    
                // scrollY: 400,
            }});
        }});
    </script>
    </body>
    </html>
    """
    return html

@app.route('/predict',methods=['POST'])
def predict():
      p_keyword=request.form["Keyword1"]
      p_noofTweets1=request.form["noofTweets1"]
      Tweets = tweepy.Cursor(api.search_tweets,q=p_keyword,result_type = "recent",lang = "en").items(int(p_noofTweets1))
      Tweets_List=[tweet.text for tweet in Tweets]
      df=pd.DataFrame(Tweets_List, columns=['Tweets'])
      df['Cleaning_Tweets']=df['Tweets']
      df['Cleaning_Tweets']=df['Cleaning_Tweets'].apply(cleanText)
      df['Subjectivity']=df['Cleaning_Tweets'].apply(getSubjectivity) # Creating column : Subjectivity
      df['Polarity']=df['Cleaning_Tweets'].apply(getPolarity) # Creating column : Polarity
      df['Analysis']=df['Polarity'].apply(getAnalysis) # Apply Analysis on 'Polarity' column values
      Displaydf=df.drop(['Cleaning_Tweets'], axis = 1)
      html = generate_html(Displaydf)
      # write the HTML content to an HTML file
      open("Results.html", "w", encoding="utf-8").write(html)
      # open the new HTML file with the default browser
      webbrowser.open("Results.html")
      return render_template('index.html',prediction_text="Result is displayed in next tab Results.page")

if __name__=="__main__":
    app.run(debug=True)
