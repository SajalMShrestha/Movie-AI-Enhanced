"""
Profile tracking and Google Sheets integration for user activity monitoring.
Handles logging user activities and enhanced profile learning from feedback.
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import streamlit as st
import json

# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Sheet names - these should match your actual Google Sheets names
ACTIVITY_SHEET_NAME = "User Activity Tracking"
LEARNING_SHEET_NAME = "Profile Learning Tracking"

def initialize_profile_tracking():
    """Initialize Google Sheets connection for profile tracking."""
    try:
        # Check if Google Sheets is enabled
        if not st.secrets.get("GOOGLE_SHEETS", {}).get("enabled", False):
            print("⚠️ Google Sheets tracking disabled")
            return False
            
        # Get credentials from Streamlit secrets
        service_account_info = {
            "type": st.secrets["GOOGLE_SHEETS"]["type"],
            "project_id": st.secrets["GOOGLE_SHEETS"]["project_id"],
            "private_key_id": st.secrets["GOOGLE_SHEETS"]["private_key_id"],
            "private_key": st.secrets["GOOGLE_SHEETS"]["private_key"],
            "client_email": st.secrets["GOOGLE_SHEETS"]["client_email"],
            "client_id": st.secrets["GOOGLE_SHEETS"]["client_id"],
            "auth_uri": st.secrets["GOOGLE_SHEETS"]["auth_uri"],
            "token_uri": st.secrets["GOOGLE_SHEETS"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["GOOGLE_SHEETS"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["GOOGLE_SHEETS"]["client_x509_cert_url"]
        }
        
        credentials = Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        
        gc = gspread.authorize(credentials)
        
        # Store in session state for reuse
        st.session_state.gc = gc
        
        return True
    except Exception as e:
        print(f"⚠️ Google Sheets not configured - running without analytics: {e}")
        return False

def get_sheet_connection():
    """Get Google Sheets connection."""
    if not hasattr(st.session_state, 'gc'):
        initialize_profile_tracking()
    
    return st.session_state.get('gc')

def log_user_activity(username: str, user_name: str, activity_type: str, data: Dict[str, Any] = None):
    """Log user activity to Google Sheets."""
    try:
        gc = get_sheet_connection()
        if not gc:
            # Google Sheets not available - log locally instead
            print(f"📝 Local activity log: {username} - {activity_type}")
            return True
        
        # Open the activity tracking sheet
        try:
            sheet = gc.open(ACTIVITY_SHEET_NAME)
        except:
            # Create new sheet if it doesn't exist
            sheet = gc.create(ACTIVITY_SHEET_NAME)
        
        # Get or create the activity worksheet
        try:
            worksheet = sheet.worksheet("Activity Log")
        except:
            worksheet = sheet.add_worksheet("Activity Log", 1000, 10)
            # Add headers
            headers = [
                "Timestamp", "Username", "User Name", "Activity Type", 
                "Data", "Session ID", "Career Stage", "Feedback Count"
            ]
            worksheet.append_row(headers)
        
        # Prepare data for logging
        row_data = [
            datetime.now().isoformat(),
            username,
            user_name,
            activity_type,
            json.dumps(data) if data else "",
            st.session_state.get('session_id', ''),
            data.get('career_stage', '') if data else '',
            data.get('feedback_count', 0) if data else 0
        ]
        
        # Append to sheet
        worksheet.append_row(row_data)
        
        return True
    except Exception as e:
        print(f"Error logging user activity: {e}")
        return False

def log_profile_learning(username: str, user_name: str, learning_data: Dict[str, Any]):
    """Log profile learning events to Google Sheets."""
    try:
        gc = get_sheet_connection()
        if not gc:
            # Google Sheets not available - log locally instead
            print(f"📝 Local learning log: {username} - {learning_data.get('movie_title', 'Unknown')}")
            return True
        
        # Open the profile learning sheet
        try:
            sheet = gc.open(LEARNING_SHEET_NAME)
        except:
            sheet = gc.create(LEARNING_SHEET_NAME)
        
        # Get or create the learning worksheet
        try:
            worksheet = sheet.worksheet("Learning Events")
        except:
            worksheet = sheet.add_worksheet("Learning Events", 1000, 15)
            # Add headers
            headers = [
                "Timestamp", "Username", "User Name", "Movie Title", "Movie ID",
                "User Response", "Liked", "Genre Updates", "Cast Updates", 
                "Director Updates", "Learning Rate", "Career Stage", 
                "Feedback Count", "Session ID"
            ]
            worksheet.append_row(headers)
        
        # Prepare learning data
        row_data = [
            datetime.now().isoformat(),
            username,
            user_name,
            learning_data.get('movie_title', ''),
            learning_data.get('movie_id', ''),
            learning_data.get('response', ''),
            learning_data.get('liked', ''),
            json.dumps(learning_data.get('genre_updates', {})),
            json.dumps(learning_data.get('cast_updates', {})),
            json.dumps(learning_data.get('director_updates', {})),
            learning_data.get('learning_rate', 0),
            learning_data.get('career_stage', ''),
            learning_data.get('feedback_count', 0),
            st.session_state.get('session_id', '')
        ]
        
        # Append to sheet
        worksheet.append_row(row_data)
        
        return True
    except Exception as e:
        print(f"Error logging profile learning: {e}")
        return False

def enhanced_update_profile_from_feedback(user_profile: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced profile update with detailed learning tracking and Google Sheets logging.
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
    
    # Track changes for logging
    genre_updates = {}
    cast_updates = {}
    director_updates = {}
    
    # Update genre preferences
    if hasattr(movie_obj, 'genres') and movie_obj.genres:
        for genre in movie_obj.genres:
            if hasattr(genre, 'name'):
                genre_name = genre.name.lower()
                
                if genre_name not in user_profile['taste_profile']['genre_weights']:
                    user_profile['taste_profile']['genre_weights'][genre_name] = 0.5
                
                old_weight = user_profile['taste_profile']['genre_weights'][genre_name]
                
                if user_liked:
                    user_profile['taste_profile']['genre_weights'][genre_name] += learning_rate * 0.1
                else:
                    user_profile['taste_profile']['genre_weights'][genre_name] -= learning_rate * 0.05
                
                # Keep weights between 0 and 1
                user_profile['taste_profile']['genre_weights'][genre_name] = max(0, min(1, user_profile['taste_profile']['genre_weights'][genre_name]))
                
                # Track changes
                new_weight = user_profile['taste_profile']['genre_weights'][genre_name]
                if abs(new_weight - old_weight) > 0.001:  # Only log significant changes
                    genre_updates[genre_name] = {
                        'old_weight': old_weight,
                        'new_weight': new_weight,
                        'change': new_weight - old_weight
                    }
    
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
                    
                    old_weight = user_profile['taste_profile']['cast_preferences'][actor_name]
                    
                    if user_liked:
                        user_profile['taste_profile']['cast_preferences'][actor_name] += learning_rate * 0.15
                    else:
                        user_profile['taste_profile']['cast_preferences'][actor_name] -= learning_rate * 0.1
                    
                    # Keep weights between 0 and 1
                    user_profile['taste_profile']['cast_preferences'][actor_name] = max(0, min(1, user_profile['taste_profile']['cast_preferences'][actor_name]))
                    
                    # Track changes
                    new_weight = user_profile['taste_profile']['cast_preferences'][actor_name]
                    if abs(new_weight - old_weight) > 0.001:
                        cast_updates[actor_name] = {
                            'old_weight': old_weight,
                            'new_weight': new_weight,
                            'change': new_weight - old_weight
                        }
    
    except Exception as e:
        print(f"Error updating cast preferences: {e}")
    
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
                        
                        old_weight = user_profile['taste_profile']['director_preferences'][director_name]
                        
                        if user_liked:
                            user_profile['taste_profile']['director_preferences'][director_name] += learning_rate * 0.2
                        else:
                            user_profile['taste_profile']['director_preferences'][director_name] -= learning_rate * 0.15
                        
                        # Keep weights between 0 and 1
                        user_profile['taste_profile']['director_preferences'][director_name] = max(0, min(1, user_profile['taste_profile']['director_preferences'][director_name]))
                        
                        # Track changes
                        new_weight = user_profile['taste_profile']['director_preferences'][director_name]
                        if abs(new_weight - old_weight) > 0.001:
                            director_updates[director_name] = {
                                'old_weight': old_weight,
                                'new_weight': new_weight,
                                'change': new_weight - old_weight
                            }
                    break
    
    except Exception as e:
        print(f"Error updating director preferences: {e}")
    
    # Update feedback count
    user_profile['feedback_count'] = user_profile.get('feedback_count', 0) + 1
    
    # Log learning event to Google Sheets
    learning_data = {
        'movie_title': movie_obj.title,
        'movie_id': movie_obj.id,
        'response': response,
        'liked': liked,
        'genre_updates': genre_updates,
        'cast_updates': cast_updates,
        'director_updates': director_updates,
        'learning_rate': learning_rate,
        'career_stage': user_profile['life_context']['career_stage'],
        'feedback_count': user_profile['feedback_count']
    }
    
    # Log to Google Sheets if user is authenticated
    if st.session_state.get('current_user'):
        log_profile_learning(
            st.session_state.current_user,
            user_profile['demographics']['name'],
            learning_data
        )
    
    return user_profile

def get_user_activity_summary(username: str, days: int = 30) -> Dict[str, Any]:
    """Get summary of user activity from Google Sheets."""
    try:
        gc = get_sheet_connection()
        if not gc:
            return {}
        
        # Open the activity tracking sheet
        try:
            sheet = gc.open(ACTIVITY_SHEET_NAME)
            worksheet = sheet.worksheet("Activity Log")
        except:
            return {}
        
        # Get all data
        all_data = worksheet.get_all_records()
        
        # Filter for user and date range
        cutoff_date = datetime.now() - timedelta(days=days)
        user_activities = []
        
        for row in all_data:
            if row.get('Username') == username:
                try:
                    activity_date = datetime.fromisoformat(row.get('Timestamp', ''))
                    if activity_date >= cutoff_date:
                        user_activities.append(row)
                except:
                    continue
        
        # Calculate summary
        activity_counts = {}
        for activity in user_activities:
            activity_type = activity.get('Activity Type', '')
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        return {
            'total_activities': len(user_activities),
            'activity_breakdown': activity_counts,
            'last_activity': user_activities[-1].get('Timestamp') if user_activities else None,
            'period_days': days
        }
        
    except Exception as e:
        print(f"Error getting user activity summary: {e}")
        return {}

def export_profile_data(username: str) -> Dict[str, Any]:
    """Export user profile data for analysis."""
    try:
        from multi_user_profiles import load_or_create_user_profile
        
        # Get user profile
        profile = load_or_create_user_profile(username)
        
        # Get activity summary
        activity_summary = get_user_activity_summary(username)
        
        # Combine data
        export_data = {
            'profile': profile,
            'activity_summary': activity_summary,
            'export_timestamp': datetime.now().isoformat(),
            'export_version': '1.0'
        }
        
        return export_data
        
    except Exception as e:
        print(f"Error exporting profile data: {e}")
        return {} 