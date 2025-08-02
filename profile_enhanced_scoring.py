"""
Profile-enhanced movie scoring and recommendation system.
Provides personalized recommendations based on user profiles and learning from feedback.
"""

import requests
from tmdbv3api import TMDb, Movie
from typing import List, Tuple, Dict, Any
import streamlit as st
from datetime import datetime
import time  # Add this line

def get_tmdb_keyword_ids(keyword_text: str, tmdb_api_key: str) -> List[int]:
    """Get TMDb keyword IDs from text search."""
    try:
        url = "https://api.themoviedb.org/3/search/keyword"
        params = {
            "api_key": tmdb_api_key,
            "query": keyword_text
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            keywords = response.json().get("results", [])
            print(f"🔑 DEBUG: Found {len(keywords)} keywords for '{keyword_text}': {[kw['name'] for kw in keywords[:3]]}")
            # Return first 3 most relevant keyword IDs
            return [kw["id"] for kw in keywords[:3]]
        else:
            print(f"❌ DEBUG: Keyword search failed for '{keyword_text}': {response.status_code}")
        
        return []
    except Exception as e:
        print(f"❌ DEBUG: Error searching keywords for '{keyword_text}': {e}")
        return []

def get_contextual_keywords_for_user(username: str, tmdb_api_key: str) -> str:
    """Get comma-separated keyword IDs for user's personality/mood."""
    user_keywords = {
        'sajal': ['business', 'leadership', 'entrepreneur'],
        'sneha': ['family', 'children', 'creative'],
        'prasanna': ['entrepreneur', 'adventure', 'outdoors'],
        'neha': ['mystery', 'investigation', 'analysis'],
        'dilasha': ['career', 'ambition', 'professional'],
        'shreish': ['nostalgia', 'childhood', 'classic']
    }
    
    keyword_ids = []
    user_keyword_list = user_keywords.get(username, [])
    
    print(f"🔑 DEBUG: Getting keywords for {username}: {user_keyword_list}")
    
    for keyword_text in user_keyword_list:
        ids = get_tmdb_keyword_ids(keyword_text, tmdb_api_key)
        keyword_ids.extend(ids)
        
        # Add small delay to avoid rate limiting
        import time
        time.sleep(0.1)
    
    # Remove duplicates and limit to 5 keywords
    unique_keyword_ids = list(set(keyword_ids))[:5]
    result = ",".join(str(id) for id in unique_keyword_ids)
    
    print(f"🔑 DEBUG: Final keyword IDs for {username}: {result}")
    return result

def get_user_contextual_mapping(username: str) -> Dict[str, str]:
    """Get contextual genre mapping for specific users (keywords handled separately)."""
    
    contextual_mappings = {
        'sajal': {
            'genres': '18,99,36',  # Drama, Documentary, History
        },
        'sneha': {
            'genres': '10751,16,18',  # Family, Animation, Drama
        },
        'prasanna': {
            'genres': '12,28,18',  # Adventure, Action, Biography
        },
        'neha': {
            'genres': '9648,53,99',  # Mystery, Thriller, Documentary
        },
        'dilasha': {
            'genres': '18,53,80',  # Drama, Thriller, Crime
        },
        'shreish': {
            'genres': '10751,35,12',  # Family, Comedy, Adventure
        }
    }
    
    return contextual_mappings.get(username, {})

def recommend_movies_with_profile(favorite_titles: List[str], user_profile: Dict[str, Any]) -> Tuple[List[Tuple[str, float]], Dict[str, Tuple[Any, float]]]:
    """Generate personalized movie recommendations based on user profile."""
    
    # DEBUG TRACE
    print("🎯 DEBUG: profile_enhanced_scoring.recommend_movies_with_profile() CALLED")
    print(f"   - Career Stage: {user_profile['life_context']['career_stage']}")
    print(f"   - Genre Weights: {user_profile['taste_profile']['genre_weights']}")
    
    # Initialize TMDb
    tmdb = TMDb()
    tmdb.api_key = st.secrets["TMDB_API_KEY"]
    tmdb.language = 'en'
    tmdb.debug = True
    
    movie_api = Movie()
    
    # Get user preferences
    genre_weights = user_profile['taste_profile']['genre_weights']
    cast_preferences = user_profile['taste_profile']['cast_preferences']
    director_preferences = user_profile['taste_profile']['director_preferences']
    mood_preferences = user_profile['taste_profile']['mood_preferences']
    career_stage = user_profile['life_context']['career_stage']
    stress_level = user_profile['life_context']['stress_level']
    
    # Get movie details for favorite movies
    favorite_movies = []
    for title in favorite_titles:
        try:
            # Search for movie
            search_results = movie_api.search(title)
            if search_results:
                movie = search_results[0]
                
                # Get detailed movie info
                detailed_movie = movie_api.details(movie.id)
                favorite_movies.append(detailed_movie)
        except Exception as e:
            print(f"Error getting details for {title}: {e}")
            continue
    
    # Extract genres, cast, and directors from favorite movies
    favorite_genres = set()
    favorite_cast = set()
    favorite_directors = set()
    
    for movie in favorite_movies:
        # Extract genres
        if hasattr(movie, 'genres') and movie.genres:
            for genre in movie.genres:
                if hasattr(genre, 'name'):
                    favorite_genres.add(genre.name.lower())
        
        # Extract cast (first 5 actors)
        try:
            credits = movie_api.credits(movie.id)
            if hasattr(credits, 'cast') and credits.cast:
                for actor in credits.cast[:5]:
                    if hasattr(actor, 'name'):
                        favorite_cast.add(actor.name.lower())
        except:
            pass
        
        # Extract director
        try:
            credits = movie_api.credits(movie.id)
            if hasattr(credits, 'crew') and credits.crew:
                for crew_member in credits.crew:
                    if hasattr(crew_member, 'job') and crew_member.job == 'Director':
                        if hasattr(crew_member, 'name'):
                            favorite_directors.add(crew_member.name.lower())
                        break
        except:
            pass
    
    # Get recommendations based on favorite movies
    candidate_movies = {}
    recommendations = []
    
    # TEMPORARILY DISABLE - TEST GENRE/CAST/DIRECTOR ONLY
    # for movie in favorite_movies:
    #     try:
    #         print(f"🔍 DEBUG: Getting similar movies for {movie.title}")
    #         similar_movies = movie_api.similar(movie.id)
    #         print(f"✅ DEBUG: Found {len(similar_movies) if similar_movies else 0} similar movies")
    #         
    #         # FIX: Convert to list before slicing
    #         similar_movies_list = list(similar_movies) if similar_movies else []
    #         
    #         for similar_movie in similar_movies_list[:10]:  # Now this will work!
    #             if similar_movie.title in candidate_movies:
    #                 continue
    #             
    #             print(f"   📝 Similar movie found: {similar_movie.title}")
    #             
    #             # Calculate personalized score
    #             score = calculate_personalized_score(
    #                 similar_movie, 
    #                 genre_weights, 
    #                 cast_preferences, 
    #                 director_preferences,
    #                 mood_preferences,
    #                 career_stage,
    #                 stress_level,
    #                 favorite_genres,
    #                 favorite_cast,
    #                 favorite_directors
    #             )
    #             
    #             candidate_movies[similar_movie.title] = (similar_movie, score)
    #             
    #     except Exception as e:
    #         print(f"❌ DEBUG: Error for {movie.title}: {e}")
    #         continue
    
    # Also search for popular movies in user's preferred genres
    for genre_name in list(favorite_genres)[:3]:  # Top 3 favorite genres
        try:
            # Strategy 1: Genre-based discovery
            url = f"https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": st.secrets["TMDB_API_KEY"],
                "with_genres": get_genre_id(genre_name),
                "sort_by": "popularity.desc",
                "vote_count.gte": 100,        # NEW: Quality threshold
                "include_adult": False,       # NEW: Block adult content
                "page": 1
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            for movie_data in data.get("results", [])[:10]:
                try:
                    movie = movie_api.details(movie_data["id"])
                    
                    if movie.title in candidate_movies:
                        continue
                    
                    # Skip if this movie is in user's favorites
                    if movie.title not in favorite_titles:
                        # Calculate personalized score
                        score = calculate_personalized_score(
                            movie, 
                            genre_weights, 
                            cast_preferences, 
                            director_preferences,
                            mood_preferences,
                            career_stage,
                            stress_level,
                            favorite_genres,
                            favorite_cast,
                            favorite_directors
                        )

                        candidate_movies[movie.title] = (movie, score)
                    
                    # Log when Se7en is found
                    if movie.title == "Se7en":
                        print(f"🎯 DEBUG: Se7en found! This is what we want more of.")
                    
                except Exception as e:
                    print(f"Error processing movie {movie_data.get('title', 'Unknown')}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting popular movies for genre {genre_name}: {e}")
            continue
    
    # Add after genre discovery strategy
    print(f"🎨 DEBUG: After genre discovery: {len(candidate_movies)} total candidates")
    
    # Extract cast and director IDs from favorite movies
    print(f"🎭 DEBUG: Extracting cast and directors from {len(favorite_movies)} favorite movies")

    favorite_cast_ids = set()
    favorite_director_ids = set()

    for movie in favorite_movies:
        try:
            print(f"🎭 DEBUG: Processing cast/crew for {movie.title}")
            
            # Get movie credits
            credits = movie_api.credits(movie.id)
            
            # Extract cast (top 5 actors)
            if hasattr(credits, 'cast') and credits.cast:
                cast_list = list(credits.cast) if credits.cast else []
                for actor in cast_list[:5]:  # Top 5 actors
                    if hasattr(actor, 'id') and hasattr(actor, 'name'):
                        favorite_cast_ids.add(actor.id)
                        favorite_cast.add(actor.name.lower())
                        print(f"   🎭 Added actor: {actor.name} (ID: {actor.id})")
            
            # Extract directors
            if hasattr(credits, 'crew') and credits.crew:
                crew_list = list(credits.crew) if credits.crew else []
                for crew_member in crew_list:
                    if hasattr(crew_member, 'job') and crew_member.job == 'Director':
                        if hasattr(crew_member, 'id') and hasattr(crew_member, 'name'):
                            favorite_director_ids.add(crew_member.id)
                            favorite_directors.add(crew_member.name.lower())
                            print(f"   🎬 Added director: {crew_member.name} (ID: {crew_member.id})")
                            break  # Usually only one director
            
        except Exception as e:
            print(f"❌ DEBUG: Error extracting cast/crew for {movie.title}: {e}")
            continue

    print(f"🎭 DEBUG: Found {len(favorite_cast_ids)} unique actors")
    print(f"🎬 DEBUG: Found {len(favorite_director_ids)} unique directors")

    # Strategy 2: Cast-Based Discovery
    print(f"\n🎭 DEBUG: STARTING cast discovery with {len(favorite_cast_ids)} actors")
    print(f"🎭 DEBUG: Cast discovery will search for movies with these actors")

    cast_discovery_count = 0
    for person_id in list(favorite_cast_ids)[:5]:  # Top 5 actors to avoid too many API calls
        try:
            print(f"🎭 DEBUG: Searching movies for actor ID {person_id}")
            
            url = f"https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": tmdb.api_key,
                "with_cast": str(person_id),
                "sort_by": "popularity.desc",
                "vote_count.gte": 100,        # Quality threshold
                "include_adult": False,       # Block adult content
                "page": 1
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                movies = response.json().get("results", [])
                print(f"🎭 DEBUG: Found {len(movies)} movies for actor {person_id}")
                
                for movie_data in movies[:8]:  # Top 8 movies per actor
                    try:
                        movie = movie_api.details(movie_data["id"])
                        
                        if movie.title in candidate_movies:
                            continue
                        
                        # Skip if this movie is in user's favorites
                        if movie.title not in favorite_titles:
                            print(f"   🎭 Cast discovery found: {movie.title}")
                            cast_discovery_count += 1
                            
                            # Calculate personalized score
                            score = calculate_personalized_score(
                                movie, 
                                genre_weights, 
                                cast_preferences, 
                                director_preferences,
                                mood_preferences,
                                career_stage,
                                stress_level,
                                favorite_genres,
                                favorite_cast,
                                favorite_directors
                            )

                            candidate_movies[movie.title] = (movie, score)
                        
                    except Exception as e:
                        print(f"   ❌ Error processing cast movie {movie_data.get('title', 'Unknown')}: {e}")
                        continue
            else:
                print(f"❌ DEBUG: Cast API call failed for actor {person_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ DEBUG: Error in cast discovery for actor {person_id}: {e}")
            continue

    print(f"🎭 DEBUG: Cast discovery added {cast_discovery_count} new movies")
    print(f"🎭 DEBUG: After cast discovery: {len(candidate_movies)} total candidates")

    # Strategy 3: Director-Based Discovery  
    print(f"\n🎬 DEBUG: STARTING director discovery with {len(favorite_director_ids)} directors")
    print(f"🎬 DEBUG: Director discovery will search for movies by these directors")

    director_discovery_count = 0
    for person_id in list(favorite_director_ids)[:3]:  # Top 3 directors
        try:
            print(f"🎬 DEBUG: Searching movies for director ID {person_id}")
            
            url = f"https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": tmdb.api_key,
                "with_crew": str(person_id),
                "sort_by": "popularity.desc", 
                "vote_count.gte": 100,        # Quality threshold
                "include_adult": False,       # Block adult content
                "page": 1
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                movies = response.json().get("results", [])
                print(f"🎬 DEBUG: Found {len(movies)} movies for director {person_id}")
                
                for movie_data in movies[:10]:  # Top 10 movies per director
                    try:
                        movie = movie_api.details(movie_data["id"])
                        
                        if movie.title in candidate_movies:
                            continue
                        
                        # Skip if this movie is in user's favorites
                        if movie.title not in favorite_titles:
                            print(f"   🎬 Director discovery found: {movie.title}")
                            director_discovery_count += 1
                            
                            # Calculate personalized score
                            score = calculate_personalized_score(
                                movie, 
                                genre_weights, 
                                cast_preferences, 
                                director_preferences,
                                mood_preferences,
                                career_stage,
                                stress_level,
                                favorite_genres,
                                favorite_cast,
                                favorite_directors
                            )

                            candidate_movies[movie.title] = (movie, score)
                        
                    except Exception as e:
                        print(f"   ❌ Error processing director movie {movie_data.get('title', 'Unknown')}: {e}")
                        continue
            else:
                print(f"❌ DEBUG: Director API call failed for director {person_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ DEBUG: Error in director discovery for director {person_id}: {e}")
            continue

    print(f"🎬 DEBUG: Director discovery added {director_discovery_count} new movies")
    print(f"🎬 DEBUG: After director discovery: {len(candidate_movies)} total candidates")

    # Strategy 4: Contextual Discovery (Personality + Mood)
    print(f"\n🎭 DEBUG: STARTING contextual discovery")

    contextual_discovery_count = 0
    user_contextual_config = get_user_contextual_mapping(st.session_state.current_user)

    if user_contextual_config:
        try:
            print(f"🎭 DEBUG: Contextual config for {st.session_state.current_user}: {user_contextual_config}")
            
            # Get dynamic keyword IDs
            keyword_ids = get_contextual_keywords_for_user(st.session_state.current_user, tmdb.api_key)
            
            url = f"https://api.themoviedb.org/3/discover/movie"
            
            # Try keywords-only and genres-only separately
            all_movies = []

            # Keywords-only search
            if keyword_ids:
                params_keywords = {
                    "api_key": tmdb.api_key,
                    "with_keywords": keyword_ids,
                    "sort_by": "popularity.desc",
                    "vote_count.gte": 50,
                    "include_adult": False,
                    "page": 1
                }
                
                print(f"🔑 DEBUG: Trying keywords-only: {keyword_ids}")
                response = requests.get(url, params=params_keywords)
                
                print(f"🔍 DEBUG: Keywords-only API URL: {url}")
                print(f"🔍 DEBUG: Keywords-only params: {params_keywords}")
                print(f"🔍 DEBUG: Keywords response: {response.json()}")
                
                if response.status_code == 200:
                    keyword_movies = response.json().get("results", [])
                    print(f"🎭 DEBUG: Found {len(keyword_movies)} movies with keywords-only")
                    all_movies.extend(keyword_movies[:8])

            # Genres-only search
            params_genres = {
                "api_key": tmdb.api_key,
                "with_genres": user_contextual_config['genres'],
                "sort_by": "popularity.desc",
                "vote_count.gte": 50,
                "include_adult": False,
                "page": 1
            }

            print(f"🎭 DEBUG: Trying genres-only: {user_contextual_config['genres']}")
            response = requests.get(url, params=params_genres)

            if response.status_code == 200:
                genre_movies = response.json().get("results", [])
                print(f"🎭 DEBUG: Found {len(genre_movies)} movies with genres-only")
                all_movies.extend(genre_movies[:7])

            # Remove duplicates and use combined results
            unique_movies = []
            seen_ids = set()
            for movie_data in all_movies:
                if movie_data["id"] not in seen_ids:
                    unique_movies.append(movie_data)
                    seen_ids.add(movie_data["id"])

            movies = unique_movies
            print(f"🎭 DEBUG: Total unique contextual movies: {len(movies)}")
            
            # Process the movies
            for movie_data in movies[:15]:  # 15 contextual recommendations
                try:
                    movie = movie_api.details(movie_data["id"])
                    
                    if movie.title in candidate_movies:
                        continue
                    
                    if movie.title not in favorite_titles:
                        print(f"   🎭 Contextual discovery found: {movie.title}")
                        contextual_discovery_count += 1
                        
                        score = calculate_personalized_score(
                            movie, 
                            genre_weights, 
                            cast_preferences, 
                            director_preferences,
                            mood_preferences,
                            career_stage,
                            stress_level,
                            favorite_genres,
                            favorite_cast,
                            favorite_directors
                        )

                        candidate_movies[movie.title] = (movie, score)
                    
                except Exception as e:
                    print(f"   ❌ Error processing contextual movie {movie_data.get('title', 'Unknown')}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ DEBUG: Error in contextual discovery: {e}")

    print(f"🎭 DEBUG: Contextual discovery added {contextual_discovery_count} new movies")
    print(f"🎭 DEBUG: After contextual discovery: {len(candidate_movies)} total candidates")

    # Final summary
    print(f"\n🏆 DEBUG: DISCOVERY SUMMARY:")
    print(f"   Genre discovery: 26 candidates (from previous debug)")
    print(f"   Cast discovery: +{cast_discovery_count} candidates")
    print(f"   Director discovery: +{director_discovery_count} candidates")
    print(f"   Contextual discovery: +{contextual_discovery_count} candidates")
    print(f"   Total final candidates: {len(candidate_movies)}")

    # Sample high-quality candidates
    sample_quality = [title for title in list(candidate_movies.keys())[:10]]
    print(f"🏆 DEBUG: Sample final candidates: {sample_quality}")

    # Check for expected high-quality matches
    expected_matches = ["The Martian", "Zodiac", "Fight Club", "The Social Network", "Good Will Hunting"]
    found_matches = [movie for movie in expected_matches if movie in candidate_movies]
    if found_matches:
        print(f"🎯 DEBUG: EXCELLENT! Found expected matches: {found_matches}")
    else:
        print(f"⚠️ DEBUG: No expected high-quality matches found yet")
    
    # Sort by score and return top recommendations
    sorted_candidates = sorted(candidate_movies.items(), key=lambda x: x[1][1], reverse=True)
    
    # Return top 10 recommendations
    recommendations = [(title, score) for title, (movie, score) in sorted_candidates[:10]]
    
    return recommendations, candidate_movies

def calculate_personalized_score(
    movie: Any, 
    genre_weights: Dict[str, float], 
    cast_preferences: Dict[str, float],
    director_preferences: Dict[str, float],
    mood_preferences: Dict[str, float],
    career_stage: str,
    stress_level: str,
    favorite_genres: set,
    favorite_cast: set,
    favorite_directors: set
) -> float:
    """Calculate personalized score for a movie based on user profile."""
    
    # DEBUG TRACE (add this at the beginning)
    print(f"🧮 DEBUG: calculate_personalized_score() called for: {getattr(movie, 'title', 'Unknown')}")
    print(f"   - Career Stage: {career_stage}")
    print(f"   - Genre Weights: {list(genre_weights.keys())[:3]}")
    
    score = 0.0
    max_score = 0.0
    
    # Genre matching (40% weight)
    genre_score = 0.0
    movie_genres = []
    
    if hasattr(movie, 'genres') and movie.genres:
        for genre in movie.genres:
            if hasattr(genre, 'name'):
                genre_name = genre.name.lower()
                movie_genres.append(genre_name)
                
                # Check against user's genre weights
                if genre_name in genre_weights:
                    genre_score += genre_weights[genre_name]
                
                # Bonus for favorite genres
                if genre_name in favorite_genres:
                    genre_score += 0.3
    
    if movie_genres:
        genre_score = genre_score / len(movie_genres)
    
    # Boost profile-driven scoring
    profile_weight = 0.6  # 60% of total score from profile
    favorites_weight = 0.4  # 40% from favorites matching
    
    # Genre scoring with much higher profile influence
    genre_profile_score = 0
    genre_similarity_score = 0
    
    for genre in movie_genres:
        # Profile-based scoring (60% weight)
        if genre.lower() in genre_weights:
            genre_profile_score += genre_weights[genre.lower()]
        
        # Favorites similarity scoring (40% weight)
        if genre.lower() in favorite_genres:
            genre_similarity_score += 0.3
    
    # Combine profile and favorites scoring
    total_genre_weight = sum(genre_weights.values()) / len(genre_weights) if genre_weights else 0.4
    final_genre_score = (genre_profile_score * profile_weight) + (genre_similarity_score * favorites_weight)
    score += final_genre_score * total_genre_weight
    max_score += total_genre_weight
    
    # Cast matching (25% weight)
    cast_score = 0.0
    cast_count = 0
    
    try:
        from tmdbv3api import Movie
        movie_api = Movie()
        credits = movie_api.credits(movie.id)
        
        if hasattr(credits, 'cast') and credits.cast:
            for actor in credits.cast[:5]:  # Check top 5 actors
                if hasattr(actor, 'name'):
                    actor_name = actor.name.lower()
                    cast_count += 1
                    
                    # Check against user's cast preferences
                    if actor_name in cast_preferences:
                        cast_score += cast_preferences[actor_name]
                    
                    # Bonus for favorite actors
                    if actor_name in favorite_cast:
                        cast_score += 0.2
        
        if cast_count > 0:
            cast_score = cast_score / cast_count
    
    except:
        pass
    
    # Cast scoring with profile-driven approach
    cast_profile_score = 0
    cast_similarity_score = 0
    
    if cast_count > 0:
        # Profile-based cast scoring (60% weight)
        cast_profile_score = cast_score * profile_weight
        
        # Favorites similarity scoring (40% weight)
        cast_similarity_score = cast_score * favorites_weight
    
    # Dynamic cast weight - higher if user has strong cast preferences
    cast_weight = 0.4 if cast_preferences else 0.15  # More weight if user has learned preferences
    final_cast_score = cast_profile_score + cast_similarity_score
    score += final_cast_score * cast_weight
    max_score += cast_weight
    
    # Director matching (15% weight)
    director_score = 0.0
    
    try:
        from tmdbv3api import Movie
        movie_api = Movie()
        credits = movie_api.credits(movie.id)
        
        if hasattr(credits, 'crew') and credits.crew:
            for crew_member in credits.crew:
                if hasattr(crew_member, 'job') and crew_member.job == 'Director':
                    if hasattr(crew_member, 'name'):
                        director_name = crew_member.name.lower()
                        
                        # Check against user's director preferences
                        if director_name in director_preferences:
                            director_score += director_preferences[director_name]
                        
                        # Bonus for favorite directors
                        if director_name in favorite_directors:
                            director_score += 0.3
                    break
    
    except:
        pass
    
    # Director scoring with profile-driven approach
    director_profile_score = director_score * profile_weight
    director_similarity_score = director_score * favorites_weight
    final_director_score = director_profile_score + director_similarity_score
    
    score += final_director_score * 0.15
    max_score += 0.15
    
    # Popularity and rating (10% weight)
    popularity_score = 0.0
    
    if hasattr(movie, 'popularity'):
        # Normalize popularity (typically 0-1000+)
        popularity_score = min(movie.popularity / 100, 1.0)
    
    if hasattr(movie, 'vote_average'):
        # Normalize rating (0-10 scale)
        rating_score = movie.vote_average / 10
        popularity_score = (popularity_score + rating_score) / 2
    
    score += popularity_score * 0.1
    max_score += 0.1
    
    # NEW: Mood preference scoring based on user profile
    mood_score = 0.0
    if mood_preferences and movie_genres:
        # Check if movie genres match user's mood preferences
        for genre in movie_genres:
            if genre.lower() in ['drama', 'thriller'] and 'motivational' in mood_preferences:
                mood_score += mood_preferences.get('motivational', 0)
            elif genre.lower() in ['comedy'] and 'entertaining' in mood_preferences:
                mood_score += mood_preferences.get('entertaining', 0)
            elif genre.lower() in ['romance', 'comedy'] and 'romantic' in mood_preferences:
                mood_score += mood_preferences.get('romantic', 0)
            elif genre.lower() in ['action', 'adventure'] and 'exciting' in mood_preferences:
                mood_score += mood_preferences.get('exciting', 0)
            elif genre.lower() in ['documentary', 'biography'] and 'educational' in mood_preferences:
                mood_score += mood_preferences.get('educational', 0)
            elif genre.lower() in ['horror', 'thriller'] and 'intense' in mood_preferences:
                mood_score += mood_preferences.get('intense', 0)
            # Add more mood mappings as needed
    
    mood_weight = 0.2  # Give mood preferences significant weight
    score += mood_score * mood_weight
    max_score += mood_weight
    
    # NEW: Contextual discovery bonus (15% weight)
    contextual_score = 0.0
    username = st.session_state.get('current_user', '')
    user_contextual = get_user_contextual_mapping(username)

    if user_contextual and movie_genres:
        contextual_genres = user_contextual.get('genres', '').split(',')
        contextual_keywords = user_contextual.get('keywords', '').split(',')
        
        # Check genre matches
        for genre in movie_genres:
            genre_id = get_genre_id(genre)
            if genre_id in contextual_genres:
                contextual_score += 0.3
        
        # Normalize contextual score
        if contextual_score > 0:
            contextual_score = min(contextual_score / len(movie_genres), 1.0)

    contextual_weight = 0.15  # 15% weight for contextual discovery
    score += contextual_score * contextual_weight
    max_score += contextual_weight
    
    # Career stage and stress level adjustments (10% weight)
    context_score = 0.0
    
    # Adjust based on career stage and stress level
    if career_stage == 'entrepreneurial_transition' and stress_level == 'high':
        # Prefer motivational and escape movies
        if any(genre in movie_genres for genre in ['drama', 'comedy', 'documentary']):
            context_score += 0.3
    elif career_stage == 'creative_professional':
        # Prefer artistic and visually stunning movies
        if any(genre in movie_genres for genre in ['drama', 'foreign', 'indie']):
            context_score += 0.3
    elif career_stage == 'business_owner':
        # Prefer leadership and success stories
        if any(genre in movie_genres for genre in ['drama', 'biography', 'thriller']):
            context_score += 0.3
    elif career_stage == 'early_mid_career':
        # Prefer trendy and social movies
        if any(genre in movie_genres for genre in ['comedy', 'romance', 'action']):
            context_score += 0.3
    
    # Different career stages get different context importance
    career_weight_map = {
        'entrepreneurial_transition': 0.3,  # High importance for Sajal
        'creative_professional': 0.2,      # Medium for Sneha/Dilasha  
        'business_owner': 0.25,            # High for Prasanna
        'early_mid_career': 0.15,          # Lower for Neha
        'mid_career': 0.1                  # Lowest for Shreish
    }
    career_weight = career_weight_map.get(career_stage, 0.1)
    score += context_score * career_weight
    max_score += career_weight
    
    # Normalize score
    if max_score > 0:
        score = score / max_score
    
    return min(score, 1.0)

def get_genre_id(genre_name: str) -> str:
    """Get TMDb genre ID for a genre name."""
    genre_map = {
        'action': '28',
        'adventure': '12',
        'animation': '16',
        'comedy': '35',
        'crime': '80',
        'documentary': '99',
        'drama': '18',
        'family': '10751',
        'fantasy': '14',
        'foreign': '10769',
        'history': '36',
        'horror': '27',
        'music': '10402',
        'mystery': '9648',
        'romance': '10749',
        'science fiction': '878',
        'tv movie': '10770',
        'thriller': '53',
        'war': '10752',
        'western': '37'
    }
    
    return genre_map.get(genre_name.lower(), '18')  # Default to drama

def update_profile_from_feedback(user_profile: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user profile based on feedback given for a movie.
    """
    
    if not feedback.get('movie_obj') or not feedback.get('response'):
        return user_profile
    
    movie_obj = feedback['movie_obj']
    response = feedback['response']
    liked = feedback.get('liked')
    
    # Determine if user liked the movie
    user_liked = False
    if response == "Yes":
        user_liked = True
    elif response == "Already watched" and liked == "Yes":
        user_liked = True
    elif response == "No":
        user_liked = False
    else:
        return user_profile  # Skip if unclear
    
    # Learning rate based on user's feedback count
    learning_rate = max(0.1, 1.0 / (user_profile.get('feedback_count', 0) + 1))
    
    # Update genre preferences
    if hasattr(movie_obj, 'genres') and movie_obj.genres:
        for genre in movie_obj.genres:
            if hasattr(genre, 'name'):
                genre_name = genre.name.lower()
                
                if genre_name not in user_profile['taste_profile']['genre_weights']:
                    user_profile['taste_profile']['genre_weights'][genre_name] = 0.5
                
                if user_liked:
                    user_profile['taste_profile']['genre_weights'][genre_name] += learning_rate * 0.1
                else:
                    user_profile['taste_profile']['genre_weights'][genre_name] -= learning_rate * 0.05
                
                # Keep weights between 0 and 1
                user_profile['taste_profile']['genre_weights'][genre_name] = max(0, min(1, user_profile['taste_profile']['genre_weights'][genre_name]))
    
    # Update cast preferences
    try:
        from tmdbv3api import Movie
        movie_api = Movie()
        credits = movie_api.credits(movie_obj.id)
        
        if hasattr(credits, 'cast') and credits.cast:
            for actor in credits.cast[:3]:  # Top 3 actors
                if hasattr(actor, 'name'):
                    actor_name = actor.name.lower()
                    
                    if actor_name not in user_profile['taste_profile']['cast_preferences']:
                        user_profile['taste_profile']['cast_preferences'][actor_name] = 0.5
                    
                    if user_liked:
                        user_profile['taste_profile']['cast_preferences'][actor_name] += learning_rate * 0.15
                    else:
                        user_profile['taste_profile']['cast_preferences'][actor_name] -= learning_rate * 0.1
                    
                    # Keep weights between 0 and 1
                    user_profile['taste_profile']['cast_preferences'][actor_name] = max(0, min(1, user_profile['taste_profile']['cast_preferences'][actor_name]))
    
    except:
        pass
    
    # Update director preferences
    try:
        from tmdbv3api import Movie
        movie_api = Movie()
        credits = movie_api.credits(movie_obj.id)
        
        if hasattr(credits, 'crew') and credits.crew:
            for crew_member in credits.crew:
                if hasattr(crew_member, 'job') and crew_member.job == 'Director':
                    if hasattr(crew_member, 'name'):
                        director_name = crew_member.name.lower()
                        
                        if director_name not in user_profile['taste_profile']['director_preferences']:
                            user_profile['taste_profile']['director_preferences'][director_name] = 0.5
                        
                        if user_liked:
                            user_profile['taste_profile']['director_preferences'][director_name] += learning_rate * 0.2
                        else:
                            user_profile['taste_profile']['director_preferences'][director_name] -= learning_rate * 0.15
                        
                        # Keep weights between 0 and 1
                        user_profile['taste_profile']['director_preferences'][director_name] = max(0, min(1, user_profile['taste_profile']['director_preferences'][director_name]))
                    break
    
    except:
        pass
    
    # Update feedback count
    user_profile['feedback_count'] = user_profile.get('feedback_count', 0) + 1
    
    return user_profile 