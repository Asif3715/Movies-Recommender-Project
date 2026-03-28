import streamlit as st
import pickle
import pandas as pd
import requests
import gzip

# Page configuration
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🍿",
    layout="wide"
)

# TMDB API configuration
TMDB_API_KEY = "b125d03c974a67e144dcfc61d3ccdc31"  
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500" 

def get_movie_poster(movie_id):
    """Fetch movie poster URL from TMDB API"""
    try:
        if pd.isna(movie_id) or movie_id == "":
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"

        url = f"{TMDB_BASE_URL}{movie_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"

@st.cache_resource
def load_data():
    """Load the preprocessed data from pickle files"""
    try:
        movies_df = pickle.load(open('movies_df.pkl', 'rb'))
        similarity_matrix = pickle.load(gzip.open('similarity_matrix.pkl.gz', 'rb'))
        movies_list = movies_df['title'].values
        return movies_list, similarity_matrix, movies_df

    except FileNotFoundError:
        st.error("Error: Data files not found! Please ensure 'movies_df.pkl' and 'similarity_matrix.pkl.gz' are in the directory.")
        return None, None, None

def get_movie_recommendations(movie_title, movies_df, similarity_matrix):
    """Get top 5 movie recommendations based on cosine similarity, excluding the movie itself"""
    try:
        movie_index = movies_df[movies_df['title'] == movie_title].index[0]
        distances = similarity_matrix[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])

        recommendations = []
        for i in movies_list[1:6]:
            idx = i[0]
            sim_score = i[1]
            movie_id = movies_df.iloc[idx].get('id', None)
            if pd.isna(movie_id):
                movie_id = movies_df.iloc[idx].get('movie_id', None)

            recommendations.append({
                'title': movies_df.iloc[idx]['title'],
                'similarity_score': sim_score,
                'movie_id': movie_id
            })

        return recommendations

    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return []

def main():
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
        }
        .recommendation-title {
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
        }
        .recommendation-caption {
            text-align: center;
            color: gray;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'>🍿 Movie Recommender System</div>", unsafe_allow_html=True)
    st.markdown("Discover movies similar to your favorites! Select a movie from the dropdown below to get 5 customized recommendations.")
    st.markdown("---")

    movies_list, similarity_matrix, movies_df = load_data()

    if movies_df is None:
        st.stop()

    # Initialize button state
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

    # Function to turn the button ON
    def click_button():
        st.session_state.button_clicked = True

    # Function to turn the button OFF (resets the view)
    def reset_state():
        st.session_state.button_clicked = False

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Select a Movie")
        
        # ADDED on_change here so picking a new movie hides the old recommendations
        selected_movie = st.selectbox(
            "Type or select a movie from the dropdown",
            movies_list,
            on_change=reset_state 
        )

        st.button('🔍 Show Recommendations', on_click=click_button, type="primary")

    with col2:
        if st.session_state.button_clicked:
            st.subheader(f"Because you liked *{selected_movie}*...")
            with st.spinner("Finding the best matches..."):
                recommendations = get_movie_recommendations(selected_movie, movies_df, similarity_matrix)

            if recommendations:
                cols = st.columns(5)
                for i, col in enumerate(cols):
                    movie = recommendations[i]
                    with col:
                        poster_url = get_movie_poster(movie['movie_id'])
                        st.image(poster_url, use_container_width=True)
                        st.markdown(f"<div class='recommendation-title'>{movie['title']}</div>", unsafe_allow_html=True)
                        similarity_percentage = movie['similarity_score'] * 100
                        st.markdown(f"<div class='recommendation-caption'>Match: {similarity_percentage:.0f}%</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This movie recommender system uses **Content-Based Filtering**. 
        
        It calculates the **Cosine Similarity** between movies based on their tags, cast, crew, and overview to find the closest matches.
        """)
        st.markdown("---")
        st.metric("Total Movies in Database", len(movies_list))

    st.markdown("---")

if __name__ == "__main__":
    main()
