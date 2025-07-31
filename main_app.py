"""
Enhanced main_app.py with Netflix-style carousel and modal recommendations
Streamlined user experience: Login → Horizontal Carousel → Click for Modal Details
"""

import streamlit as st
import uuid
import requests
from tmdbv3api import TMDb, Movie

# Import our enhanced components
from multi_user_profiles import authenticate_user, load_or_create_user_profile, save_user_profile, update_user_login, get_user_summary
from profile_enhanced_scoring import recommend_movies_with_profile, update_profile_from_feedback
from profile_tracking_sheets import initialize_profile_tracking, log_user_activity, enhanced_update_profile_from_feedback
from src.feedback_system import (
    initialize_feedback_csv, get_or_create_numeric_session_id,
    record_feedback_to_sheet, record_final_comments_to_sheet
)

# Pre-loaded favorite movies for all users
USER_FAVORITE_MOVIES = {
    'sajal': [
        "The Bourne Identity",
        "Knocked Up", 
        "Manchester by the Sea",
        "Miami Vice",
        "Gone Girl"
    ],
    'sneha': [
        "How to Train Your Dragon",
        "3 Idiots",
        "Good Boys", 
        "The Lion King",
        "A Cinderella Story"
    ],
    'prasanna': [
        "10 Things I Hate About You",
        "Shutter Island",
        "Guardians of the Galaxy",
        "The Grand Budapest Hotel", 
        "Thor: Love and Thunder"
    ],
    'neha': [
        "The Notebook",
        "Knives Out",
        "Zindagi Na Milegi Dobara",
        "Amélie",
        "The Invisible Guest"
    ],
    'dilasha': [
        "Shutter Island",
        "The Shawshank Redemption", 
        "Titanic",
        "Harry Potter and the Philosopher's Stone",
        "Crazy, Stupid, Love."
    ],
    'shreish': [
        "Home Alone 2: Lost in New York",
        "The Shawshank Redemption",
        "Harry Potter and the Prisoner of Azkaban", 
        "Harry Potter and the Deathly Hallows: Part 2",
        "Elf"
    ]
}

def setup_enhanced_ui():
    """Setup enhanced UI styling for Netflix-style carousel."""
    
    st.set_page_config(
        page_title="Screen or Skip - Movie Recommendations",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'About': "Personalized movie recommendations powered by AI"
        }
    )
    
    st.markdown("""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main app styling */
        .stApp {
            max-width: 1400px;
            margin: 0 auto;
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #141414;
            color: white;
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
        }
        
        /* Profile button */
        .profile-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            padding: 0.5rem 1rem;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .profile-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        
        /* Netflix-style carousel */
        .carousel-container {
            position: relative;
            margin: 2rem 0;
            padding: 0 2rem;
        }
        
        .carousel-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: white;
        }
        
        .movie-carousel {
            display: flex;
            overflow-x: auto;
            scroll-behavior: smooth;
            gap: 1rem;
            padding: 1rem 0;
            scrollbar-width: thin;
            scrollbar-color: #667eea #141414;
            cursor: grab;
        }
        
        .movie-carousel:active {
            cursor: grabbing;
        }
        
        .movie-carousel::-webkit-scrollbar {
            height: 8px;
        }
        
        .movie-carousel::-webkit-scrollbar-track {
            background: #141414;
            border-radius: 4px;
        }
        
        .movie-carousel::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        
        .movie-carousel::-webkit-scrollbar-thumb:hover {
            background: #5a6fd8;
        }
        
        .movie-tile {
            flex: 0 0 auto;
            width: 160px;
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
        }
        
        .movie-tile:hover {
            transform: scale(1.05);
            z-index: 2;
        }
        
        .movie-tile img {
            width: 100%;
            height: 240px;
            object-fit: cover;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .movie-title {
            padding: 0.5rem 0;
            font-size: 0.9rem;
            font-weight: 600;
            text-align: center;
            color: white;
            line-height: 1.2;
            transition: all 0.3s ease;
        }
        
        /* Modal styling */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            background: #1a1a1a;
            border-radius: 15px;
            max-width: 800px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            border: 1px solid #333;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #333;
        }
        
        .close-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: background 0.3s ease;
        }
        
        .close-btn:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .modal-body {
            padding: 1.5rem;
        }
        
        .movie-details {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .movie-poster-modal {
            flex: 0 0 200px;
        }
        
        .movie-poster-modal img {
            width: 100%;
            border-radius: 10px;
        }
        
        .movie-info {
            flex: 1;
        }
        
        .movie-info h2 {
            margin: 0 0 0.5rem 0;
            font-size: 1.8rem;
            color: white;
        }
        
        .movie-meta {
            color: #ccc;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        
        .movie-plot {
            color: #e0e0e0;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        
        .recommendation-reason {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
        }
        
        .recommendation-reason h3 {
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
        }
        
        .modal-navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-top: 1px solid #333;
        }
        
        .nav-btn {
            background: #667eea;
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-btn:hover {
            background: #5a6fd8;
            transform: translateY(-1px);
        }
        
        .nav-btn:disabled {
            background: #555;
            cursor: not-allowed;
            transform: none;
        }
        
        .movie-counter {
            color: #ccc;
            font-size: 0.9rem;
        }
        
        /* Login form styling */
        .login-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background: #1a1a1a;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            background: #2a2a2a;
            border: 2px solid #444;
            border-radius: 10px;
            color: white;
            padding: 0.75rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Success messages */
        .success-message {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .movie-tile {
                width: 120px;
            }
            
            .movie-tile img {
                height: 180px;
            }
            
            .modal-content {
                width: 95%;
                margin: 1rem;
            }
            
            .movie-details {
                flex-direction: column;
            }
            
            .movie-poster-modal {
                align-self: center;
                flex: 0 0 auto;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def show_login_page():
    """Display enhanced login page."""
    
    st.markdown("""
    <div class="main-header">
        <h1>🎬 Screen or Skip</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: white;">🎬 Welcome</h2>
        <p style="text-align: center; color: #ccc; margin-bottom: 2rem;">Sign in to get personalized movie recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return False
            
            if authenticate_user(username.lower().strip(), password):
                # Successful login
                st.session_state.authenticated = True
                st.session_state.current_user = username.lower().strip()
                
                # Load user profile
                user_profile = load_or_create_user_profile(username.lower().strip())
                st.session_state.user_profile = user_profile
                
                # Auto-load favorite movies
                user_favorites = USER_FAVORITE_MOVIES.get(username.lower().strip(), [])
                st.session_state.favorite_movies = [{"title": title} for title in user_favorites]
                
                # Update login stats
                update_user_login(username.lower().strip())
                
                # Log activity
                log_user_activity(username.lower().strip(), user_profile['demographics']['name'], 'login')
                
                st.markdown(f"""
                <div class="success-message">
                    <h4 style="margin: 0;">✅ Welcome back, {user_profile['demographics']['name']}!</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.rerun()
                
            else:
                st.error("Invalid username or password. Please try again.")
                return False
    
    # Demo credentials
    with st.expander("🔑 Available Users (Demo)"):
        st.write("**Usernames:** sajal, sneha, prasanna, neha, dilasha, shreish")
        st.write("**Password:** pass123")
    
    return False

def show_profile_page():
    """Display user profile page with favorite movies."""
    
    if not st.session_state.get('user_profile'):
        return
    
    user_profile = st.session_state.user_profile
    user_name = user_profile['demographics']['name']
    username = st.session_state.current_user
    
    # Profile header
    st.markdown(f"""
    <div class="main-header">
        <h1>👤 {user_name}'s Profile</h1>
        <div>Your movie preferences and profile information</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Recommendations", type="secondary"):
        st.session_state.show_profile = False
        st.rerun()
    
    st.markdown("---")
    
    # User Information
    st.markdown("### 📋 Profile Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {user_profile['demographics']['name']}")
        st.write(f"**Career Stage:** {user_profile['life_context']['career_stage'].replace('_', ' ').title()}")
        st.write(f"**Stress Level:** {user_profile['life_context']['stress_level'].title()}")
    
    with col2:
        usage_stats = user_profile.get('usage_stats', {})
        st.write(f"**Total Logins:** {usage_stats.get('total_logins', 0)}")
        st.write(f"**Movies Rated:** {user_profile.get('feedback_count', 0)}")
        st.write(f"**Profile Created:** {user_profile.get('created_at', 'Unknown')[:10]}")
    
    st.markdown("---")
    
    # Favorite Movies Section
    st.markdown("### 🎬 Your Favorite Movies")
    
    # Get user's favorite movie titles
    user_favorites = USER_FAVORITE_MOVIES.get(username, [])
    
    if user_favorites:
        # Display movies in grid
        cols = st.columns(5)
        for i, title in enumerate(user_favorites):
            with cols[i]:
                try:
                    # Try to get poster from cache or API
                    if title in st.session_state.get('favorite_movie_posters', {}):
                        poster_path = st.session_state.favorite_movie_posters[title]
                        if poster_path:
                            poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}"
                            st.image(poster_url, use_column_width=True)
                        else:
                            st.write("🎬 No poster")
                    else:
                        st.write("🎬 Loading...")
                    
                    st.write(f"**{title}**")
                except Exception as e:
                    st.write("🎬 No poster")
                    st.write(f"**{title}**")
    
    else:
        st.info("No favorite movies found for this user.")
    
    # Logout button
    st.markdown("---")
    if st.button("🚪 Logout", type="primary"):
        # Log logout activity
        log_user_activity(st.session_state.current_user, user_name, 'logout')
        
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_profile = None
        st.session_state.show_profile = False
        st.rerun()

def generate_recommendation_reason(movie_obj, user_favorites, user_profile):
    """Generate detailed recommendation reasoning."""
    
    try:
        movie_title = movie_obj.title
        movie_genres = []
        
        # Extract movie genres
        genres_list = getattr(movie_obj, 'genres', [])
        for g in genres_list:
            if isinstance(g, dict):
                name = g.get('name', '')
            else:
                name = getattr(g, 'name', '')
            if name:
                movie_genres.append(name)
        
        # Find similar favorite movie
        similar_favorite = None
        favorite_titles = [movie["title"] for movie in st.session_state.favorite_movies]
        
        # Simple similarity check based on genres and themes
        for fav_title in favorite_titles:
            if any(keyword in movie_title.lower() for keyword in ['action', 'thriller', 'mystery']) and \
               any(keyword in fav_title.lower() for keyword in ['action', 'thriller', 'mystery']):
                similar_favorite = fav_title
                break
            elif any(genre.lower() in ['comedy', 'romantic'] for genre in movie_genres) and \
                 any(keyword in fav_title.lower() for keyword in ['comedy', 'romantic', 'love']):
                similar_favorite = fav_title
                break
        
        # Fallback to first favorite
        if not similar_favorite and favorite_titles:
            similar_favorite = favorite_titles[0]
        
        # Generate reason based on profile and similarities
        career_stage = user_profile['life_context']['career_stage']
        
        if similar_favorite:
            if any(genre.lower() in ['thriller', 'mystery', 'crime'] for genre in movie_genres):
                reason = f"Based on your love for thrillers like '{similar_favorite}', this combines {', '.join(movie_genres[:2]).lower()} with psychological elements that match your taste for complex narratives."
            elif any(genre.lower() in ['comedy', 'romance'] for genre in movie_genres):
                reason = f"Since you enjoyed '{similar_favorite}', this {', '.join(movie_genres[:2]).lower()} offers similar emotional depth and character development."
            elif any(genre.lower() in ['action', 'adventure'] for genre in movie_genres):
                reason = f"Like '{similar_favorite}', this delivers high-energy {', '.join(movie_genres[:2]).lower()} with compelling storytelling."
            else:
                reason = f"Based on your appreciation for '{similar_favorite}', this {', '.join(movie_genres[:2]).lower()} shares similar themes and storytelling quality."
        else:
            # Generic reason based on career stage
            if career_stage == 'entrepreneurial_transition':
                reason = f"This {', '.join(movie_genres[:2]).lower()} resonates with your entrepreneurial mindset, offering themes of ambition and resilience."
            elif career_stage == 'creative_professional':
                reason = f"As a creative professional, you'll appreciate the artistic vision and {', '.join(movie_genres[:2]).lower()} storytelling in this film."
            else:
                reason = f"This {', '.join(movie_genres[:2]).lower()} aligns with your sophisticated taste and preference for quality cinema."
        
        return reason
    
    except Exception as e:
        return f"Recommended based on your viewing preferences and taste profile."

def auto_generate_recommendations():
    """Auto-generate recommendations based on pre-loaded favorites."""
    
    if not st.session_state.get('favorite_movies') or not st.session_state.get('user_profile'):
        return
    
    # Check if recommendations already generated
    if st.session_state.get('recommendations') and st.session_state.get('candidates'):
        return
    
    favorite_titles = [movie["title"] for movie in st.session_state.favorite_movies]
    
    try:
        # Use profile-enhanced recommendation system
        user_profile = st.session_state.user_profile
        recs, candidate_movies = recommend_movies_with_profile(favorite_titles, user_profile)
        
        st.session_state.recommendations = recs
        st.session_state.candidates = candidate_movies
        st.session_state.recommend_triggered = True
        
        # Log recommendation activity
        log_user_activity(
            st.session_state.current_user, 
            user_profile['demographics']['name'], 
            'get_recommendations',
            {'recommendations_count': len(recs)}
        )
        
    except Exception as e:
        st.error(f"❌ Failed to generate recommendations: {e}")
        import traceback
        st.error(traceback.format_exc())

def check_authentication():
    """Check if user is authenticated."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'show_modal' not in st.session_state:
        st.session_state.show_modal = False
    if 'selected_movie_index' not in st.session_state:
        st.session_state.selected_movie_index = 0
    
    # Show login if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True

def initialize_session_state():
    """Initialize session state variables."""
    session_vars = {
        "favorite_movies": [],
        "selected_movie": None,
        "recommendations": None,
        "candidates": None,
        "recommend_triggered": False,
        "favorite_movie_posters": {},
        "movie_details_cache": {},
        "movie_credits_cache": {},
        "fetch_cache": {},
        "recommendation_cache": {},
        "session_id": str(uuid.uuid4()),
        "search_done": False,
        "previous_query": ""
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

def main():
    """Main application function with Netflix-style carousel."""
    
    # Setup enhanced styling
    setup_enhanced_ui()
    
    # Initialize profile tracking
    initialize_profile_tracking()
    
    # Check authentication first
    if not check_authentication():
        return
    
    # Initialize session state
    initialize_session_state()
    initialize_feedback_csv()
    numeric_id, session_uuid = get_or_create_numeric_session_id()
    st.session_state.numeric_session_id = numeric_id
    
    # Initialize TMDb
    tmdb = TMDb()
    tmdb.api_key = st.secrets["TMDB_API_KEY"]
    tmdb.language = 'en'
    tmdb.debug = True
    
    # Show profile page or main recommendations
    if st.session_state.get('show_profile', False):
        show_profile_page()
    else:
        # Main page header with profile button
        user_name = st.session_state.user_profile['demographics']['name'].split()[0]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            <div class="main-header">
                <h1>🎬 Your Movie Recommendations</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("👤 Profile", key="profile_btn"):
                st.session_state.show_profile = True
                st.rerun()
        
        # Auto-generate recommendations on first load
        auto_generate_recommendations()
        
        # Show Netflix-style movie carousel
        if st.session_state.get('recommend_triggered'):
            if st.session_state.get('recommendations'):
                st.markdown("### 🌟 Your Personalized Recommendations")
                
                # Create horizontal scrollable layout using Streamlit columns
                # Display movies in two rows of 5 each for better compatibility
                recommendations = st.session_state.recommendations[:10]
                
                # First row (movies 0-4)
                if len(recommendations) > 0:
                    cols1 = st.columns(5)
                    for i in range(min(5, len(recommendations))):
                        title, score = recommendations[i]
                        
                        # Find movie object
                        movie_obj = None
                        for m, _ in st.session_state.candidates.values():
                            if m and getattr(m, 'title', '') == title:
                                movie_obj = m
                                break
                        
                        with cols1[i]:
                            # Display poster
                            if movie_obj and movie_obj.poster_path:
                                poster_url = f"https://image.tmdb.org/t/p/w300{movie_obj.poster_path}"
                                st.image(poster_url, use_container_width=True)
                            else:
                                st.write("🎬 No Poster")
                            
                            # Movie title
                            st.write(f"**{title}**")
                            
                            # View details button
                            if st.button("👁️ View Details", key=f"movie_{i}", use_container_width=True):
                                st.session_state.selected_movie_index = i
                                st.session_state.show_modal = True
                                st.rerun()
                
                # Second row (movies 5-9)
                if len(recommendations) > 5:
                    cols2 = st.columns(5)
                    for i in range(5, min(10, len(recommendations))):
                        title, score = recommendations[i]
                        
                        # Find movie object
                        movie_obj = None
                        for m, _ in st.session_state.candidates.values():
                            if m and getattr(m, 'title', '') == title:
                                movie_obj = m
                                break
                        
                        with cols2[i-5]:
                            # Display poster
                            if movie_obj and movie_obj.poster_path:
                                poster_url = f"https://image.tmdb.org/t/p/w300{movie_obj.poster_path}"
                                st.image(poster_url, use_container_width=True)
                            else:
                                st.write("🎬 No Poster")
                            
                            # Movie title
                            st.write(f"**{title}**")
                            
                            # View details button
                            if st.button("👁️ View Details", key=f"movie_{i}", use_container_width=True):
                                st.session_state.selected_movie_index = i
                                st.session_state.show_modal = True
                                st.rerun()
                
                # Show modal if movie selected
                if st.session_state.get('show_modal', False):
                    st.markdown("---")
                    
                    # Movie details section
                    idx = st.session_state.selected_movie_index
                    title, score = st.session_state.recommendations[idx]
                    
                    # Find movie object
                    movie_obj = None
                    for m, _ in st.session_state.candidates.values():
                        if m and getattr(m, 'title', '') == title:
                            movie_obj = m
                            break
                    
                    if movie_obj:
                        # Close button
                        if st.button("❌ Close Details", key="close_modal"):
                            st.session_state.show_modal = False
                            st.rerun()
                        
                        # Movie details
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if movie_obj.poster_path:
                                st.image(f"https://image.tmdb.org/t/p/w300{movie_obj.poster_path}", width=200)
                            else:
                                st.write("🎬 No poster")
                        
                        with col2:
                            st.markdown(f"## {movie_obj.title}")
                            
                            # Year
                            release_year = "N/A"
                            try:
                                if hasattr(movie_obj, 'release_date') and movie_obj.release_date:
                                    release_year = movie_obj.release_date[:4]
                            except:
                                pass
                            st.write(f"**Year:** {release_year}")
                            
                            # Plot
                            overview = getattr(movie_obj, 'overview', None) or "No description available."
                            st.write(f"**Plot:** {overview}")
                            
                            # Recommendation reason
                            reason = generate_recommendation_reason(movie_obj, st.session_state.favorite_movies, st.session_state.user_profile)
                            st.info(f"🎯 **Why We Recommended This:** {reason}")
                        
                        # Navigation
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col1:
                            if idx > 0 and st.button("← Previous Movie"):
                                st.session_state.selected_movie_index = idx - 1
                                st.rerun()
                        
                        with col2:
                            st.write(f"**{idx + 1} of {len(st.session_state.recommendations)}**")
                        
                        with col3:
                            if idx < len(st.session_state.recommendations) - 1 and st.button("Next Movie →"):
                                st.session_state.selected_movie_index = idx + 1
                                st.rerun()
        else:
            st.info("🤖 Generating your personalized recommendations...")
            st.rerun()

if __name__ == "__main__":
    main()