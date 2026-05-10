import os
import requests
from app import app, db, Place
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_pexels_image(query):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['photos']:
                return data['photos'][0]['src']['large']
        else:
            print(f"Error fetching image for {query}: {response.status_code}")
    except Exception as e:
        print(f"Exception for {query}: {e}")
    return None

def sync_images():
    with app.app_context():
        places = Place.query.all()
        print(f"Starting Pexels sync for {len(places)} places...")
        
        updated_count = 0
        for p in places:
            # Create a specific search query
            search_query = f"{p.name} {p.country or 'India'}"
            print(f"Searching for: {search_query}")
            
            image_url = fetch_pexels_image(search_query)
            if image_url:
                p.image_url = image_url
                updated_count += 1
                print(f"  [OK] Updated {p.name}")
            else:
                print(f"  [FAIL] No image found for {p.name}")
        
        db.session.commit()
        print(f"\nFinished! Updated {updated_count} places with actual Pexels images.")

if __name__ == "__main__":
    if not PEXELS_API_KEY or "sk-" in PEXELS_API_KEY: # Simple check
        print("Please set a valid PEXELS_API_KEY in your .env file.")
    else:
        sync_images()
