import feedparser
import requests
from bs4 import BeautifulSoup
import mysql.connector
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

db_params = {
    "host": "localhost",
    "user": "root",
    "password": "akshat#289",
    "database": "newscategorydb",
}

conn = mysql.connector.connect(**db_params)
cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS news_articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    link VARCHAR(255),
    text_content TEXT,
    category VARCHAR(50)
)
"""
cursor.execute(create_table_query)
conn.commit()

rss_feeds = [
    "http://feeds.abcnews.com/abcnews/usheadlines"
]

stop_words = set(stopwords.words('english'))

terrorism_keywords = [
    "terrorism", "terrorist", "attack", "extremism", "insurgency", "radicalization",
    "violent extremism", "suicide bombing", "jihad", "counterterrorism", "homeland security",
    "radical ideology", "domestic terrorism", "international terrorism", "security threat",
    "terror cell", "terror financing", "radical groups", "extremist propaganda",
    "cyberterrorism", "lone wolf", "bioterrorism", "chemical attack", "nuclear terrorism",
    "asymmetric warfare", "threat assessment", "terror watchlist", "radical recruitment",
    "terrorist financing", "homeland defense", "counterinsurgency", "terrorist ideology",
    "radical movements", "counter-radicalization", "counter-extremism", "terror plot",
    "terrorist network", "radicalized individuals", "domestic security", "counterintelligence",
    "intelligence gathering", "radical sympathizers", "terrorist sleeper cell",
    "counter-terrorism measures", "terrorist recruitment", "homegrown terrorism",
    "radicalization process", "terrorism prevention", "counter-terrorism strategy",
    "radicalization factors", "counter-terrorism operations", "security intelligence",
    "counter-terrorism efforts", "anti-terrorism laws", "terrorist tactics",
    "counter-terrorism policy", "radicalization programs", "terrorist training camps",
    "terrorist hotspots", "counter-terrorism initiatives", "terrorist propaganda",
    "counter-terrorism agencies", "cybersecurity threats", "terrorist sympathizers",
    "terrorist profiling", "counter-terrorism unit", "radicalization awareness",
    "counter-terrorism coordination", "terrorist havens", "counter-terrorism partnerships",
    "radicalization studies", "terrorism response", "counter-terrorism intelligence",
    "terrorist ideology", "counter-terrorism legislation", "radicalization education",
    "terrorism investigation", "counter-terrorism training", "terrorist tactics",
    "counter-terrorism experts", "radicalization prevention", "terrorist financing",
    "counter-terrorism research", "terrorism analysis", "counter-terrorism measures",
    "radicalization intervention", "terrorist recruitment tactics", "homeland resilience",
    "counter-terrorism assessment", "radicalization indicators", "terrorist threat assessment"
]

positive_keywords = [
    "positive", "uplifting", "joyful", "inspiring", "optimistic", "hopeful",
    "encouraging", "motivational", "heartwarming", "cheerful", "happy", "delightful",
    "contentment", "gratitude", "blissful", "radiant", "satisfying", "fulfilling",
    "pleasant", "smiling", "celebratory", "elated", "thriving", "empowering",
    "life-affirming", "upbeat", "vibrant", "enchanting", "serene", "tranquil",
    "peaceful", "wholesome", "charming", "upward", "celebration", "jovial",
    "sunshine", "gleeful", "lighthearted", "benevolent", "kind-hearted", "merry",
    "exuberant", "radiant", "grateful", "optimism", "positivity", "inspiration",
    "upliftment", "joyfulness", "heartening", "motivation", "euphoria", "happiness",
    "positiveness", "comforting", "inspirational", "uplifting", "hopefulness",
    "positivity boost", "positive vibes", "contentedness", "optimistic outlook",
    "positive energy", "smiles", "good vibes", "joyous", "uplifting spirit",
    "positive attitude", "good-hearted", "beaming", "high-spirited", "laughter",
    "blissfulness", "positive impact", "sunny disposition", "enriching", "inspiring words",
    "positive reinforcement", "bright side", "affirmation", "radiate happiness",
    "inspiring quotes", "positive influence", "positivity movement", "hopeful future",
    "optimistic mindset", "positive change", "encouragement", "radiant soul",
    "positive affirmations", "smile-inducing", "inspiring stories", "positivity wave",
    "joyous moments", "uplifting thoughts", "positive mindset", "positive psychology",
    "uplifting messages", "joyful living", "optimistic spirit", "positivity in life"
]

natural_disaster_keywords = [
    "natural", "disaster", "catastrophe", "calamity", "emergency", "earthquake",
    "flood", "hurricane", "tornado", "tsunami", "typhoon", "wildfire", "volcano",
    "landslide", "drought", "avalanche", "storm surge", "cyclone", "blizzard",
    "heatwave", "mudslide", "sinkhole", "natural hazard", "geological disaster",
    "meteorological disaster", "climatic event", "seismic activity", "severe weather",
    "extreme event", "emergency response", "disaster management", "evacuation",
    "shelter-in-place", "emergency preparedness", "recovery efforts", "humanitarian aid",
    "disaster relief", "emergency shelter", "damage assessment", "search and rescue",
    "natural disaster impact", "early warning system", "disaster resilience",
    "crisis management", "natural disaster recovery", "rescue operations",
    "emergency services", "disaster risk reduction", "resilient communities",
    "natural disaster response", "reconstruction efforts", "community resilience",
    "emergency relief", "disaster-prone areas", "environmental devastation",
    "natural disaster preparedness", "emergency management", "humanitarian assistance",
    "disaster recovery plan", "disaster mitigation", "emergency supplies",
    "community recovery", "natural disaster aftermath", "crisis intervention",
    "emergency support", "disaster assistance", "disaster recovery assistance",
    "recovery and reconstruction", "humanitarian response", "disaster recovery efforts",
    "emergency aid", "disaster recovery funding", "humanitarian relief",
    "disaster-stricken areas", "disaster declaration", "emergency relief efforts",
    "natural disaster statistics", "climate-related disaster", "disaster resilience plan",
    "humanitarian organizations", "vulnerability assessment", "emergency evacuation",
    "disaster risk management", "resilience building", "community preparedness",
    "natural disaster impacts", "disaster recovery projects", "emergency planning",
    "disaster response team", "emergency relief organizations", "crisis intervention",
    "natural disaster scenarios", "disaster assistance programs", "crisis response",
    "humanitarian crisis", "natural disaster recovery timeline", "disaster response plan",
    "environmental emergencies", "disaster relief agencies", "emergency response teams"
]

def categorize_text(text_content):
    words = word_tokenize(text_content)
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]

    terrorism_match = any(keyword in filtered_words for keyword in terrorism_keywords)
    positive_match = any(keyword in filtered_words for keyword in positive_keywords)
    natural_disaster_match = any(keyword in filtered_words for keyword in natural_disaster_keywords)

    if terrorism_match:
        return "Terrorism/Protest/Political Unrest/Riot"
    elif positive_match:
        return "Positive/Uplifting"
    elif natural_disaster_match:
        return "Natural Disasters"
    else:
        return "Others"

for feed_url in rss_feeds:
    feed = feedparser.parse(feed_url)
    
    for entry in feed.entries:
        title = entry.title
        link = entry.link

        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = ' '.join([p.text for p in soup.find_all('p')])

        category = categorize_text(text_content)

        insert_query = """
        INSERT INTO news_articles (title, link, text_content, category)
        VALUES (%s, %s, %s, %s)
        """
        data = (title, link, text_content, category)
        cursor.execute(insert_query, data)
        conn.commit()

cursor.close()
conn.close()



