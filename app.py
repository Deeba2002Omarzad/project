import pandas as pd
import streamlit as st

# Load datasets
video_df = pd.read_csv("updated_video_dataset.csv")
user_df = pd.read_csv("user_dataset.csv")

# Helper function to fetch user watch history and preferences
def get_user_watch_history(user_id):
    user_history = user_df[user_df["user_id"] == user_id]
    if user_history.empty:
        return None
    avg_rating = user_history["rating"].mean()
    most_watched_genre = user_history["video_id"].map(
        video_df.set_index("video_id")["video_genre"]
    ).mode()[0]
    return {
        "avg_rating": avg_rating,
        "most_watched_genre": most_watched_genre,
        "watch_history": user_history["watch_history"].tolist(),
    }

# Recommendation function
def recommend_videos_by_age_location(age, location):
    # Filter by location
    recommended_videos = video_df[video_df["country"] == location]
    # Filter by age group (e.g., children, teens, adults)
    if age < 13:
        recommended_videos = recommended_videos[recommended_videos["video_genre"].isin(["Animation", "Family"])]
    elif age < 18:
        recommended_videos = recommended_videos[recommended_videos["video_genre"].isin(["Comedy", "Adventure", "Action"])]
    else:
        recommended_videos = recommended_videos
    return recommended_videos.head(10)

def recommend_videos_by_user_data(user_id, additional_filters=None):
    # Fetch user preferences
    user_data = get_user_watch_history(user_id)
    if not user_data:
        st.warning("No watch history found for this user ID.")
        return pd.DataFrame()

    # Base recommendations: Use watch history preferences
    recommended_videos = video_df[
        (video_df["video_genre"] == user_data["most_watched_genre"]) |
        (video_df["video_rating"] >= user_data["avg_rating"])
    ]

    # Apply additional filters
    if additional_filters:
        if "genre" in additional_filters:
            recommended_videos = recommended_videos[recommended_videos["video_genre"] == additional_filters["genre"]]
        if "resolution" in additional_filters:
            recommended_videos = recommended_videos[recommended_videos["resolution"] == additional_filters["resolution"]]
        if "title" in additional_filters:
            recommended_videos = recommended_videos[
                recommended_videos["video_name"].str.contains(additional_filters["title"], case=False)
            ]

    return recommended_videos.head(10)

# Streamlit App
st.title("Hybrid Video Recommendation System")

# Step 1: Initial Recommendations Based on Age and Location
st.header("Step 1: Recommendations Based on Age and Location")
location = st.text_input("Enter your Location (e.g., India, USA)")
age = st.number_input("Enter your Age", min_value=0, max_value=120, step=1)

if st.button("Get Initial Recommendations"):
    if not location:
        st.error("Please enter your location.")
    else:
        st.success("Fetching recommendations based on your age and location...")
        initial_recommendations = recommend_videos_by_age_location(age, location)
        if initial_recommendations.empty:
            st.warning("No recommendations found. Try adjusting your inputs.")
        else:
            st.subheader("Initial Recommendations")
            st.table(initial_recommendations[["video_id", "video_name", "video_genre", "video_rating", "resolution", "country"]])

# Step 2: Refine Recommendations Based on User ID and Past Data
st.header("Step 2: Refined Recommendations Based on User ID and Preferences")
user_id = st.number_input("Enter your User ID", min_value=1, step=1)

genre = st.selectbox("Preferred Genre", ["", "Comedy", "Drama", "Action", "Thriller", "Horror", "Documentary", "Romance"])
resolution = st.selectbox("Preferred Resolution", ["", "480p", "720p", "1080p", "4K"])
title = st.text_input("Keyword in Video Title")

if st.button("Refine Recommendations"):
    additional_filters = {}
    if genre:
        additional_filters["genre"] = genre
    if resolution:
        additional_filters["resolution"] = resolution
    if title:
        additional_filters["title"] = title

    refined_recommendations = recommend_videos_by_user_data(user_id, additional_filters)
    if refined_recommendations.empty:
        st.warning("No refined recommendations found. Try adjusting your preferences.")
    else:
        st.subheader("Refined Recommendations (Based on Your Watch History and Preferences)")
        st.table(refined_recommendations[["video_id", "video_name", "video_genre", "video_rating", "resolution", "country"]])
