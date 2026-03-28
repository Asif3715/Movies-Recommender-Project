# 🎬 Movie Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)](https://streamlit.io/)
[![Deployment](https://img.shields.io/badge/Deployed_on-Render-black)](https://movies-recommender-project-1.onrender.com/)

> A machine learning-powered web app that delivers personalized movie recommendations using Content-Based Filtering.

**[🚀 View Live Application](https://movies-recommender-e9in.onrender.com/)**

---

## 📖 Overview

This project analyzes movie metadata — including overviews, genres, cast, and crew — to recommend films that share similar core attributes to the user's selection. Built with Python and deployed via Streamlit, it features real-time movie poster fetching through the TMDB API.

---

## ⚙️ Methodology

The recommendation engine uses NLP and vector mathematics to determine similarity:

1. **Data Preprocessing** — Extracted and merged relevant features from the TMDB 5000 Movies & Credits dataset. Tags were cleaned, lowercased, tokenized, and stemmed using NLTK's `PorterStemmer` to reduce vocabulary redundancy.
2. **Vectorization** — Textual tags for each movie were converted into numerical vectors using `CountVectorizer` (up to 5,000 max features, with English stop words ignored).
3. **Similarity Calculation** — Computed vector distances using **Cosine Similarity**, producing a robust similarity matrix that maps the relationship between any two movies in multidimensional vector space.

---

## 🏗️ Technical Architecture

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning & NLP | Scikit-Learn, NLTK |
| External API | TMDB (movie poster rendering) |
| Deployment | Render (with gzip-compressed similarity matrix) |

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Asif3715/Movies-Recommender-Project.git
cd Movies-Recommender-Project
```

### 2. Set Up a Virtual Environment

**Using Conda (recommended):**
```bash
conda create --name recommender-env python=3.10 -y
conda activate recommender-env
```

**Using venv:**
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

---

## 📁 File Structure
```
Movies-Recommender-Project/
├── app.py                      # Main Streamlit app (frontend logic & API calls)
├── requirements.txt            # Production dependencies
├── movies_df.pkl               # Serialized DataFrame with cleaned movie metadata
├── similarity_matrix.pkl.gz    # GZIP-compressed cosine similarity matrix
└── .gitignore                  # Excludes raw CSVs, notebooks, and uncompressed binaries
```

---

## 🙏 Acknowledgments

- **Dataset:** [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) via Kaggle
- **Poster API:** [The Movie Database (TMDB)](https://www.themoviedb.org/)
