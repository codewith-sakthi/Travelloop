from app import app, db, Place
import sys

mapping = {
    'Golden Temple': 'https://images.unsplash.com/photo-1514222134-b57cbb8ce073',
    'Taj Mahal': 'https://images.unsplash.com/photo-1564507592333-c60657eea523',
    'Qutub Minar': 'https://images.unsplash.com/photo-1581010866468-385af67ad536',
    'India Gate': 'https://images.unsplash.com/photo-1587474260584-136574528ed5',
    'Gateway of India': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da',
    'Hawa Mahal': 'https://images.unsplash.com/photo-1599661046289-e31887846eac',
    'Amber Fort': 'https://images.unsplash.com/photo-1590593162211-f1f3a9fc49f4',
    'City Palace': 'https://images.unsplash.com/photo-1629130761690-349f280a5661',
    'Victoria Memorial': 'https://images.unsplash.com/photo-1558431382-27e39cbef4bc',
    'Meenakshi Temple': 'https://images.unsplash.com/photo-1582510003544-2d095ca5011a',
    'Amer Fort': 'https://images.unsplash.com/photo-1590593162211-f1f3a9fc49f4',
    'Mysore Palace': 'https://images.unsplash.com/photo-1613098522619-322a36b320d3',
    'Marina Beach': 'https://images.unsplash.com/photo-1582510003544-2d095ca5011a',
    'Ooty': 'https://images.unsplash.com/photo-1583267746897-2cf415888172',
    'Shimla': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23',
    'Manali': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23',
    'Jaipur': 'https://images.unsplash.com/photo-1599661046289-e31887846eac',
    'Udaipur': 'https://images.unsplash.com/photo-1629130761690-349f280a5661',
    'Goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2',
    'Munnar': 'https://images.unsplash.com/photo-1593693397690-362cb9666fc2',
    'Kerala': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944',
    'Agra': 'https://images.unsplash.com/photo-1564507592333-c60657eea523',
    'Delhi': 'https://images.unsplash.com/photo-1587474260584-136574528ed5',
    'Mumbai': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da',
    'Varanasi': 'https://images.unsplash.com/photo-1561359313-0639aad49ca6',
    'Hampi': 'https://images.unsplash.com/photo-1616440268508-306429f63546',
    'Coorg': 'https://images.unsplash.com/photo-1590050752117-23a9dbc3003a',
    'Darjeeling': 'https://images.unsplash.com/photo-1612053073715-e4612e4438ce',
    'Gangtok': 'https://images.unsplash.com/photo-1611624632598-a32f0da64478',
    'Amritsar': 'https://images.unsplash.com/photo-1514222134-b57cbb8ce073',
    'Guwahati': 'https://images.unsplash.com/photo-1626014303757-6419221379f8',
    'Assam': 'https://images.unsplash.com/photo-1596422846543-75c6fc18a593',
    'Meghalaya': 'https://images.unsplash.com/photo-1505142468610-359e7d316be0',
    'Sikkim': 'https://images.unsplash.com/photo-1589133415834-0370830f3050'
}

def update_images():
    with app.app_context():
        places = Place.query.all()
        updated = 0
        for p in places:
            p_text = (p.name + " " + (p.country or "") + " " + (p.description or "")).lower()
            for city, url in mapping.items():
                if city.lower() in p_text:
                    p.image_url = url + "?w=600&q=80&fit=crop"
                    updated += 1
                    break
        db.session.commit()
        print(f"Successfully updated {updated} places with high-quality regional images.")

if __name__ == '__main__':
    update_images()
