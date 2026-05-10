import csv
import os
from app import app, db, Place

def import_top_places(csv_path):
    print(f"Importing from {csv_path}...")
    count = 0
    with app.app_context():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Name')
                if not name:
                    continue
                    
                city = row.get('City', '')
                state = row.get('State', '')
                country = f"{city}, {state}" if city else state
                
                type_val = row.get('Type', '').lower()
                category = 'activity'
                if 'beach' in type_val or 'park' in type_val or 'fort' in type_val or 'temple' in type_val or 'museum' in type_val or 'historical' in type_val:
                    category = 'activity'
                elif 'restaurant' in type_val or 'food' in type_val:
                    category = 'food'
                elif 'hotel' in type_val or 'stay' in type_val:
                    category = 'hotel'
                
                try:
                    popularity = float(row.get('Google review rating', 0))
                except ValueError:
                    popularity = 0.0
                    
                try:
                    price = float(row.get('Entrance Fee in INR', 0))
                except ValueError:
                    price = 0.0
                    
                desc = row.get('Significance', '')
                
                # Check if exists to avoid duplicates
                if not Place.query.filter_by(name=name).first():
                    place = Place(
                        name=name,
                        category=category,
                        country=country,
                        cost_index="$" if price < 100 else "$$" if price < 500 else "$$$",
                        popularity=popularity,
                        price_per_unit=price,
                        description=desc,
                        image_url="https://images.unsplash.com/photo-1518998053401-a4149019651c?w=200&auto=format&fit=crop"
                    )
                    db.session.add(place)
                    count += 1
                    
        db.session.commit()
        print(f"Successfully imported {count} new places into the database!")

if __name__ == '__main__':
    dataset_path = os.path.join(os.path.dirname(__file__), 'Datasets', 'Top Indian Places to Visit.csv')
    if os.path.exists(dataset_path):
        import_top_places(dataset_path)
    else:
        print("Dataset not found at:", dataset_path)
