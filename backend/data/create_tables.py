try:
    from database import Base, engine
    from DataClass import Restaurant, Foods, User, Order
except:
    from .database import Base, engine
    from .DataClass import Restaurant, Foods, User,Order

def main():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    main()