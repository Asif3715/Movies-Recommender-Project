import streamlit as st
import pickle
import pandas as pd
import requests

# TMDB API configuration
TMDB_API_KEY = "b125d03c974a67e144dcfc61d3ccdc31"  # Replace with your actual TMDB API key
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"  # w500 for medium quality posters


# Page configuration
def get_movie_poster(movie_id):
    """Fetch movie poster URL from TMDB API"""
    try:
        if pd.isna(movie_id) or movie_id == "":
            return None

        # Convert to int if it's not already
        movie_id = int(float(movie_id))

        url = f"{TMDB_BASE_URL}{movie_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
        return None
    except Exception as e:
        return None


st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)


@st.cache_data
def load_data():
    """Load the preprocessed data"""
    try:
        # Load movies list
        with open('movies_list.pkl', 'rb') as f:
            movies_list = pickle.load(f)

        # Load similarity matrix
        with open('similarity_matrix.pkl', 'rb') as f:
            similarity_matrix = pickle.load(f)

        # Load full dataframe
        with open('movies_df.pkl', 'rb') as f:
            movies_df = pickle.load(f)

        return movies_list, similarity_matrix, movies_df

    except FileNotFoundError as e:
        print(f"Error: Data files not found! {e}")
        print("Please run prepare_data.py first to generate the required pickle files.")
        return None, None, None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None


def get_movie_recommendations(movie_title, movies_df, similarity_matrix):
    """Get movie recommendations based on cosine similarity"""
    try:
        # Find the index of the selected movie
        movie_index = movies_df[movies_df['title'] == movie_title].index[0]

        # Get similarity scores for this movie
        distances = similarity_matrix[movie_index]

        # Create list of (index, similarity_score) tuples
        indexed_tuples = list(enumerate(distances))

        # Sort by similarity score in descending order
        sorted_tuples = sorted(indexed_tuples, reverse=True, key=lambda x: x[1])

        # Get top 6 movies (including the movie itself)
        recommendations = []
        counter = 0

        for i, similarity_score in sorted_tuples:
            if counter > 5:
                break
            if counter == 1:  # Skip the selected movie itself
                counter += 1
                continue

            movie_data = movies_df.iloc[i]
            movie_id = movie_data.get('id', None)
            if pd.isna(movie_id):
                movie_id = movie_data.get('movie_id', None)  # Try alternative column name

            recommendations.append({
                'title': movie_data['title'],
                'similarity_score': similarity_score,
                'movie_id': movie_id
            })
            counter += 1

        return recommendations[:5]

    except IndexError:
        return []


def main():
    # Check if running in Streamlit context
    try:
        # This will work only when running with streamlit run
        st.title("🎬 Movie Recommender System")
    except:
        print("Please run this app using: streamlit run app.py")
        return

    # App title and description
    st.markdown("### Discover movies similar to your favorites!")
    st.markdown(
        "Select a movie from the dropdown below to get 5 similar movie recommendations based on content similarity.")

    # Load data
    movies_list, similarity_matrix, movies_df = load_data()

    # Check if data loaded successfully
    if movies_list is None or similarity_matrix is None or movies_df is None:
        st.error("❌ Data files not found!")
        st.markdown("""
        **To fix this issue:**
        1. Make sure you have run `prepare_data.py` first
        2. Check that these files exist in your current directory:
           - `movies_list.pkl`
           - `similarity_matrix.pkl` 
           - `movies_df.pkl`
        3. Make sure you're running the app from the correct directory
        """)
        st.stop()
        return

    # Create two columns for better layout
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("🎯 Select a Movie")

        # Movie selection dropdown
        selected_movie = st.selectbox(
            "Choose a movie:",
            options=sorted(movies_list),
            index=0,
            help="Select a movie to get recommendations based on similar content"
        )

        # Add some movie info if available
        if selected_movie:
            # Get selected movie details
            selected_movie_data = movies_df[movies_df['title'] == selected_movie].iloc[0]
            selected_movie_id = selected_movie_data.get('id', None)
            if pd.isna(selected_movie_id):
                selected_movie_id = selected_movie_data.get('movie_id', None)  # Try alternative column name

            # Display selected movie poster
            if selected_movie_id and not pd.isna(selected_movie_id):
                poster_url = get_movie_poster(selected_movie_id)
                if poster_url:
                    st.image(poster_url, width=200, caption=selected_movie)
                    st.success(f"**Selected:** {selected_movie}")
                else:
                    st.info(f"**Selected Movie:** {selected_movie}")
                    st.caption("🎬 Poster not available")
            else:
                st.info(f"**Selected Movie:** {selected_movie}")
                st.caption("🎬 No movie ID found")

            # Add a recommend button for better UX
            if st.button("🔍 Get Recommendations", type="primary"):
                st.session_state.show_recommendations = True

    with col2:
        st.subheader("📽️ Recommended Movies")

        # Show recommendations
        if selected_movie and (st.button or getattr(st.session_state, 'show_recommendations', False)):
            with st.spinner("Finding similar movies..."):
                recommendations = get_movie_recommendations(selected_movie, movies_df, similarity_matrix)

            if recommendations:
                st.success(f"Movies similar to **{selected_movie}**:")

                # Display recommendations in a nice format with posters
                for i, movie in enumerate(recommendations, 1):
                    with st.container():
                        # Create columns for poster and movie info
                        poster_col, info_col = st.columns([1, 3])

                        with poster_col:
                            # Display movie poster
                            movie_id = movie.get('movie_id')
                            if movie_id and not pd.isna(movie_id):
                                poster_url = get_movie_poster(movie_id)
                                if poster_url:
                                    st.image(poster_url, width=120)
                                else:
                                    st.write("🎬")  # Fallback emoji
                                    st.caption("No poster")
                            else:
                                st.write("🎬")  # Fallback emoji
                                st.caption("No ID")

                        with info_col:
                            st.markdown(f"**{i}. {movie['title']}**")
                            # Create a progress bar to show similarity score
                            similarity_percentage = movie['similarity_score'] * 100
                            st.progress(movie['similarity_score'])
                            st.caption(f"Similarity: {similarity_percentage:.1f}%")

                        st.markdown("---")
            else:
                st.error("No recommendations found for this movie. Please try another selection.")

    # Add some additional information in the sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This movie recommender system uses **cosine similarity** to find movies 
        with similar content based on their features.

        **How it works:**
        1. Select a movie from the dropdown
        2. The system calculates similarity scores with all other movies
        3. Returns the top 5 most similar movies

        **Features:**
        - Content-based filtering
        - Cosine similarity algorithm
        - Interactive movie selection
        """)

        st.header("📊 Statistics")
        st.metric("Total Movies", len(movies_list))

        if selected_movie:
            st.metric("Selected Movie", "✓")
        else:
            st.metric("Selected Movie", "None")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Built with Streamlit 🚀 | Movie Recommendation System"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    # Check if running with streamlit
    import sys

    if 'streamlit' not in sys.modules:
        print("⚠️  This is a Streamlit app!")
        print("Please run it using: streamlit run app.py")
        print("Don't run it directly with python app.py")
    else:
        main()