import re, requests, os
from textblob import TextBlob
from groq import Groq

API_KEY = os.environ.get("Youtube_Api")
url = input("Paste Youtube URL > ")

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_comments(video_id, api_key, max_results=10):
    comments = []
    url = f'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={api_key}&maxResults={max_results}'
    response = requests.get(url)
    data = response.json()

    for item in data['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

        if len(comments) >= max_results:
            break

    return comments

def analyze_sentiment(comments):
    sentiment_data = {'positive': 0, 'neutral': 0, 'negative': 0}
    positive = []
    negative = []

    for comment in comments:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            sentiment_data['positive'] += 1
            positive.append(comment)
        elif polarity == 0:
            sentiment_data['neutral'] += 1
        else:
            sentiment_data['negative'] += 1
            negative.append(comment)

    total_comments = len(comments)
    for key in sentiment_data:
        sentiment_data[key] = (sentiment_data[key] / total_comments) * 100

    return sentiment_data, positive, negative

video_id = extract_video_id(url)
if video_id:
    comments = get_comments(video_id, API_KEY, max_results=10)
    sentiment_data, positive, negative = analyze_sentiment(comments)

    print("Sentiment Analysis:")
    print(sentiment_data)

    prompt = f"Summarise the comments and in bullent point and provide constructive feedback. f{negative}"
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    print("\nNegative Comments:")
    print(response.choices[0].message.content)
    prompt = f"Summarise the comments and in bullent point provide constructive feedback. f{positive}"

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    print("\nPositive Comments:")
    print(response.choices[0].message.content)

else:
    print("Invalid YouTube URL")
