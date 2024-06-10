import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database import SessionLocal
from DataClass import User, Restaurant, Foods
import plotly.express as px


# Function to fetch users from the database
def get_users(db: Session):
    return db.query(User).all()


def get_restaurants(db: Session):
    return db.query(Restaurant).all()


def get_foods(db: Session):
    return db.query(Foods).all()


# Streamlit app
def main():
    st.title("FoodNEST Dashboard")

    # Sidebar
    st.sidebar.title("Filters")
    filter_name = st.sidebar.text_input("Search Users by Name")
    filter_restaurant = st.sidebar.text_input("Search Restaurants by Name")

    # Initialize the database session
    db = SessionLocal()

    # Fetch data from the database
    users = get_users(db)
    restro = get_restaurants(db)
    foods = get_foods(db)

    # Convert the data to pandas DataFrames
    user_data = [
        {"id": r.id, "name": r.first_name + " " + r.last_name, "email": r.email, "phone": r.phone, "address": r.address}
        for r in users]
    user_df = pd.DataFrame(user_data)

    restro_data = [{"id": r.id, "name": r.name, "description": r.description, "address":r.address, "google maps":r.google_maps_link} for r in restro]
    restro_df = pd.DataFrame(restro_data)

    food_data = [{"id": r.id, "restro_id": r.restaurant_id, "name": r.name, "description": r.description, "price":r.price} for r in
                 foods]
    food_df = pd.DataFrame(food_data)

    # Apply filters
    if filter_name:
        user_df = user_df[user_df['name'].str.contains(filter_name, case=False)]

    if filter_restaurant:
        restro_df = restro_df[restro_df['name'].str.contains(filter_restaurant, case=False)]

    # Display dataframes
    st.header("Users Table")
    st.dataframe(user_df)

    st.header("Restaurants Table")
    st.dataframe(restro_df)

    st.header("Foods Table")
    st.dataframe(food_df)

    # Visualizations
    st.header("Data Visualizations")

    if not food_df.empty:
        food_count = food_df.groupby('name').size().reset_index(name='count')
        fig_food = px.bar(food_count, x='name', y='count', title="Foods Count")
        st.plotly_chart(fig_food)

        # Frequency plot for dish prices
        if not food_df.empty:
            food_count = food_df.groupby('name').size().reset_index(name='count')
            fig_food = px.bar(food_count, x='name', y='count', title="Foods Count")
            st.plotly_chart(fig_food)

            # Frequency plot for dish prices
            fig_price = px.histogram(
                food_df,
                x='price',
                nbins=20,
                title="Price Distribution of Dishes",
                labels={'price': 'Price', 'count': 'Frequency'},
                template='plotly_white',
                color_discrete_sequence=['#636EFA'],
                opacity=0.8,  # Adjust the opacity of the bars
                barmode='overlay',  # Overlay bars on top of each other
            )
            fig_price.update_traces(marker_line_color='black', marker_line_width=1.5)  # Add dark edge between bars
            fig_price.update_layout(
                xaxis_title="Price",
                yaxis_title="Frequency",
                title_x=0.5
            )
            st.plotly_chart(fig_price)


    # Close the database session
    db.close()


if __name__ == "__main__":
    main()
