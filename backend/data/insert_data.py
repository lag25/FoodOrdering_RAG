import pandas as pd
from sqlalchemy.orm import Session

from database import SessionLocal
from DataClass import Restaurant, Foods

def add_restaurant(db: Session, name: str, description: str, address: str, google_maps_link: str):
    restaurant = Restaurant(name=name, description=description,address=address, google_maps_link=google_maps_link)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

def add_food(db: Session, restaurant_id: int, name: str, description: str,price):
    food = Foods(restaurant_id=restaurant_id, name=name, description=description,price=price)
    db.add(food)
    db.commit()
    db.refresh(food)
    return food



def main():
    db = SessionLocal()
    restaurants = [
        {"name": "Rajbhog Chaupati", "description": "Amazing Indian street food with a variety of delicious chaat, vada pav, and more.", "address": "Ganj Basoda, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8523,77.9278,21z?entry=ttu"},
        {"name": "Burger Land", "description": "Mouthwatering tasty burgers with fresh ingredients and unique flavors.", "address": "Civil Lines, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8528,77.9282,21z?entry=ttu"},
        {"name": "Divine Food Lounge and Restaurant", "description": "A variety of different delicacies with an ambiance to match.", "address": "Subhash Ganj, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8532,77.9286,21z?entry=ttu"},
        {"name": "Sagar Gaire Fast Food Corner", "description": "Fast food that is quick, tasty, and satisfying.", "address": "Baripura, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8536,77.9290,21z?entry=ttu"},
        {"name": "Mezbaan Restaurant", "description": "Spicy Mughlai meals that will tantalize your taste buds.", "address": "Kiri Mohalla, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8540,77.9294,21z?entry=ttu"},
        {"name": "The Foodie", "description": "A casual dining experience with a wide range of cuisines.", "address": "Madhav Ganj, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8544,77.9298,21z?entry=ttu"},
        {"name": "Taste of India", "description": "Traditional Indian food with authentic flavors.", "address": "Shastri Nagar, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8548,77.9302,21z?entry=ttu"},
        {"name": "Spice Route", "description": "A journey through India's finest spices and culinary traditions.", "address": "Saraswati Colony, Vidisha, MP, India", "google_maps_link": "https://www.google.com/maps/@23.8552,77.9306,21z?entry=ttu"}
    ]

    foods = [
        # Rajbhog Chaupati items
        {"restaurant_id": 1, "name": "Dahi Papdi Chaat", "description": "A savory and tangy dish made with crispy papdis, aloo, chickpeas, and a generous dollop of creamy dahi, garnished with sev and chutneys.", "price": 50},
        {"restaurant_id": 1, "name": "Vada Pav", "description": "A spicy potato fritter (vada) sandwiched between a soft bread roll (pav), served with chutneys and fried green chilies.", "price": 30},
        {"restaurant_id": 1, "name": "Pani Puri", "description": "Crispy puris filled with tangy tamarind water, spicy mashed potatoes, and chickpeas.", "price": 40},

        # Burger Land Items
        {"restaurant_id": 2, "name": "Classic Burger", "description": "A juicy potato patty burger topped with fresh lettuce, tomato, and a special house sauce.", "price": 120},
        {"restaurant_id": 2, "name": "Cheesy Veg Stack Burger", "description": "A triple-layer burger with two veg patties, extra cheese, and a mix of fresh veggies.", "price": 180},
        {"restaurant_id": 2, "name": "Spicy Paneer Burger", "description": "A burger with a spicy paneer patty, cheese, and a zesty sauce.", "price": 150},

        # Divine Food Lounge and Restaurant Items
        {"restaurant_id": 3, "name": "Kadhai Paneer", "description": "Spicy paneer curry with a tomato base, bell peppers, and onions, served with butter naan.", "price": 200},
        {"restaurant_id": 3, "name": "Veg Manchurian", "description": "A Chinese delicacy made with deep-fried vegetable balls in a tangy, spicy sauce.", "price": 150},
        {"restaurant_id": 3, "name": "Dal Makhani", "description": "Creamy and rich lentil curry made with black lentils and kidney beans, cooked with butter and cream.", "price": 180},

        # Sagar Gaire Fast Food Corner Items
        {"restaurant_id": 4, "name": "Chole Kulcha", "description": "Spicy chickpea chole curry served with soft and fluffy leavened bread kulcha.", "price": 80},
        {"restaurant_id": 4, "name": "Veg Biryani", "description": "A tasty vegetarian rice dish cooked with aromatic spices, vegetables, and saffron.", "price": 120},
        {"restaurant_id": 4, "name": "Paneer Tikka", "description": "Grilled paneer cubes marinated in a spicy yogurt mixture, served with mint chutney.", "price": 150},

        # Mezbaan Restaurant Items
        {"restaurant_id": 5, "name": "Chicken Lollipop", "description": "A spicy appetizer made from chicken wings, coated in a flavorful batter and deep-fried.", "price": 200},
        {"restaurant_id": 5, "name": "Anda Curry", "description": "Indian egg curry dish made with boiled eggs simmered in a spicy tomato gravy.", "price": 120},
        {"restaurant_id": 5, "name": "Mutton Biryani", "description": "Aromatic rice dish cooked with tender pieces of mutton and a blend of spices.", "price": 300},

        # The Foodie Items
        {"restaurant_id": 6, "name": "Paneer Butter Masala", "description": "Soft paneer cubes cooked in a rich and creamy tomato-based gravy, flavored with butter and spices.", "price": 220},
        {"restaurant_id": 6, "name": "Veg Spring Rolls", "description": "Crispy rolls stuffed with a mix of fresh vegetables, served with a tangy dipping sauce.", "price": 100},
        {"restaurant_id": 6, "name": "Mushroom Masala", "description": "Mushrooms cooked in a spicy and tangy tomato gravy, served with steamed rice.", "price": 180},

        # Taste of India Items
        {"restaurant_id": 7, "name": "Butter Chicken", "description": "Tender chicken pieces cooked in a creamy tomato-based gravy, flavored with butter and a blend of spices.", "price": 250},
        {"restaurant_id": 7, "name": "Aloo Paratha", "description": "Stuffed flatbread with a spiced potato filling, served with yogurt and pickle.", "price": 70},
        {"restaurant_id": 7, "name": "Gulab Jamun", "description": "Soft and spongy milk-based dumplings soaked in a sweet sugar syrup.", "price": 50},

        # Spice Route Items
        {"restaurant_id": 8, "name": "Hyderabadi Biryani", "description": "Aromatic rice dish cooked with marinated meat, basmati rice, and a blend of spices, served with raita.", "price": 280},
        {"restaurant_id": 8, "name": "Palak Paneer", "description": "Paneer cubes cooked in a creamy spinach gravy, flavored with garlic and spices.", "price": 200},
        {"restaurant_id": 8, "name": "Masala Dosa", "description": "Crispy rice and lentil crepe filled with a spiced potato mixture, served with coconut chutney and sambar.", "price": 100}
    ]

    for restaurant in restaurants:
        print(restaurant)
        add_restaurant(db, restaurant["name"], restaurant["description"], restaurant["address"], restaurant["google_maps_link"])

    # Populate foods table
    for food in foods:
        add_food(db, food["restaurant_id"], food["name"], food["description"], food["price"])

    print("Data populated successfully!")


if __name__ == "__main__":
    main()
