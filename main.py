import praw
from gtts import gTTS
import os
import json
from dotenv import load_dotenv


load_dotenv()

# Reddit API Bilgileri
reddit = praw.Reddit(
    client_id= os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT')
)

# Hedef subreddit'ler
subreddits = ['story', 'betrayal', 'cheating_stories']

# Ses dosyalarını kaydedeceğimiz klasör
audio_folder = 'reddit_audio_stories'
os.makedirs(audio_folder, exist_ok=True)

# Yeni hikayeleri depolamak için liste
stories = []

# Anahtar kelimeler
keywords = ['cheat', 'betrayal', 'affair', 'lie', 'secret']

# Minimum upvote filtresi
MIN_UPVOTES = 500

# Subreddit'lerden hikayeleri çek ve ses dosyasına çevir
for subreddit_name in subreddits:
    subreddit = reddit.subreddit(subreddit_name)
    print(f"🔍 {subreddit_name} subreddit'inden gönderiler alınıyor...")

    for post in subreddit.top(limit=10, time_filter='all'):
        if not post.stickied and len(post.selftext) > 100 and post.score >= MIN_UPVOTES:
            if any(kw in post.title.lower() for kw in keywords):
                # Hikaye verisi
                story = {
                    'title': post.title,
                    'author': post.author.name if post.author else 'deleted',
                    'subreddit': subreddit_name,
                    'score': post.score,
                    'url': post.url,
                    'content': post.selftext
                }
                stories.append(story)

                # TTS ile ses dosyasını oluştur
                text_to_convert = f"Title: {post.title}. Story: {post.selftext}"
                tts = gTTS(text=text_to_convert, lang='en', slow=False)

                # Dosya adını oluştur
                safe_title = ''.join(c for c in post.title if c.isalnum() or c in (' ', '_')).rstrip()
                filename = f"{audio_folder}/{safe_title[:50]}.mp3"

                # Ses dosyasını kaydet
                tts.save(filename)
                print(f"✅ Ses dosyası kaydedildi: {filename}")

# JSON dosyasına hikayeleri kaydet
with open('reddit_stories.json', 'w', encoding='utf-8') as f:
    json.dump(stories, f, ensure_ascii=False, indent=4)

print(f"\n🎉 {len(stories)} hikaye kaydedildi ve ses dosyaları oluşturuldu.")
