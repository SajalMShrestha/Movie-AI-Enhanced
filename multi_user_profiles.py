"""
Multi-user profile management system for personalized movie recommendations.
Handles user authentication, profile creation, and data persistence.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import streamlit as st

# User credentials (in production, this would be in a secure database)
DEMO_USERS = {
    'sajal': {
        'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
        'name': 'Sajal Shrestha',
        'email': 'sajal.shrestha99@gmail.com'
    },
    'sneha': {
        'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
        'name': 'Sneha Pradhan',
        'email': 'sneha91pradhan@gmail.com'
    },
    'prasanna': {
        'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
        'name': 'Prasanna Shrestha',
        'email': 'prasanna.shrestha@gmail.com'
    },
    'neha': {
        'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
        'name': 'Neha Shrestha',
        'email': 'neha.shrestha@gmail.com'
    },
    'dilasha': {
        'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
        'name': 'Dilasha Shrestha',
        'email': 'dilasha.shrestha@gmail.com'
    },
    'shreish': {
        'password_hash': hashlib.sha256('pass123'.encode()).hexdigest(),
        'name': 'Shreish Shrestha',
        'email': 'shreish.shrestha@gmail.com'
    }
}

# Profile templates for different user types
PROFILE_TEMPLATES = {
    'entrepreneurial_transition': {
        'demographics': {
            'age_range': '25-35',
            'location': 'Urban',
            'interests': ['innovation', 'business', 'technology', 'startups']
        },
        'life_context': {
            'career_stage': 'entrepreneurial_transition',
            'stress_level': 'high',
            'free_time': 'limited',
            'viewing_preferences': ['motivational', 'business_insights', 'escape_from_reality']
        },
        'taste_profile': {
            'genre_weights': {
                'drama': 0.8,
                'thriller': 0.7,
                'comedy': 0.6,
                'documentary': 0.5,
                'action': 0.4
            },
            'cast_preferences': {},
            'director_preferences': {},
            'mood_preferences': {
                'motivational': 0.8,
                'thought_provoking': 0.7,
                'entertaining': 0.6
            }
        }
    },
    'creative_professional': {
        'demographics': {
            'age_range': '25-40',
            'location': 'Urban/Suburban',
            'interests': ['arts', 'design', 'creativity', 'culture']
        },
        'life_context': {
            'career_stage': 'creative_professional',
            'stress_level': 'medium',
            'free_time': 'moderate',
            'viewing_preferences': ['artistic', 'visually_stunning', 'narrative_rich']
        },
        'taste_profile': {
            'genre_weights': {
                'drama': 0.9,
                'comedy': 0.7,
                'romance': 0.6,
                'foreign': 0.5,
                'indie': 0.8
            },
            'cast_preferences': {},
            'director_preferences': {},
            'mood_preferences': {
                'artistic': 0.9,
                'emotional': 0.7,
                'inspiring': 0.6
            }
        }
    },
    'business_owner': {
        'demographics': {
            'age_range': '30-50',
            'location': 'Urban',
            'interests': ['business', 'leadership', 'success', 'networking']
        },
        'life_context': {
            'career_stage': 'business_owner',
            'stress_level': 'high',
            'free_time': 'limited',
            'viewing_preferences': ['leadership_lessons', 'success_stories', 'entertainment']
        },
        'taste_profile': {
            'genre_weights': {
                'drama': 0.7,
                'thriller': 0.8,
                'comedy': 0.6,
                'biography': 0.7,
                'action': 0.5
            },
            'cast_preferences': {},
            'director_preferences': {},
            'mood_preferences': {
                'motivational': 0.8,
                'entertaining': 0.7,
                'thought_provoking': 0.6
            }
        }
    },
    'established_professional': {
        'demographics': {
            'age_range': '35-55',
            'location': 'Suburban/Urban',
            'interests': ['career_growth', 'family', 'work_life_balance']
        },
        'life_context': {
            'career_stage': 'established_professional',
            'stress_level': 'medium',
            'free_time': 'moderate',
            'viewing_preferences': ['quality_entertainment', 'family_friendly', 'intellectual']
        },
        'taste_profile': {
            'genre_weights': {
                'drama': 0.8,
                'comedy': 0.7,
                'thriller': 0.6,
                'romance': 0.5,
                'family': 0.6
            },
            'cast_preferences': {},
            'director_preferences': {},
            'mood_preferences': {
                'entertaining': 0.8,
                'emotional': 0.6,
                'relaxing': 0.7
            }
        }
    },
    'early_mid_career': {
        'demographics': {
            'age_range': '25-35',
            'location': 'Urban',
            'interests': ['career_development', 'social_life', 'exploration']
        },
        'life_context': {
            'career_stage': 'early_mid_career',
            'stress_level': 'medium_high',
            'free_time': 'moderate',
            'viewing_preferences': ['trendy', 'social', 'entertaining']
        },
        'taste_profile': {
            'genre_weights': {
                'comedy': 0.8,
                'action': 0.7,
                'drama': 0.6,
                'romance': 0.7,
                'adventure': 0.6
            },
            'cast_preferences': {},
            'director_preferences': {},
            'mood_preferences': {
                'entertaining': 0.9,
                'social': 0.7,
                'exciting': 0.6
            }
        }
    },
    'mid_career': {
        'demographics': {
            'age_range': '35-45',
            'location': 'Suburban/Urban',
            'interests': ['stability', 'family', 'career_advancement']
        },
        'life_context': {
            'career_stage': 'mid_career',
            'stress_level': 'medium',
            'free_time': 'moderate',
            'viewing_preferences': ['quality_content', 'family_appropriate', 'entertaining']
        },
        'taste_profile': {
            'genre_weights': {
                'drama': 0.7,
                'comedy': 0.8,
                'thriller': 0.6,
                'family': 0.7,
                'romance': 0.6
            },
            'cast_preferences': {},
            'director_preferences': {},
            'mood_preferences': {
                'entertaining': 0.8,
                'relaxing': 0.7,
                'emotional': 0.6
            }
        }
    }
}

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user with username and password."""
    if username not in DEMO_USERS:
        return False
    
    user_data = DEMO_USERS[username]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    return password_hash == user_data['password_hash']

def get_user_demographics(username: str) -> Dict[str, Any]:
    """Get user demographics from credentials."""
    if username not in DEMO_USERS:
        return {}
    
    user_data = DEMO_USERS[username]
    return {
        'name': user_data['name'],
        'email': user_data['email'],
        'username': username
    }

def create_default_profile(username: str) -> Dict[str, Any]:
    """Create a default profile for a new user."""
    demographics = get_user_demographics(username)
    
    # Determine career stage based on name (for demo purposes)
    career_stage = 'established_professional'  # Default
    if 'sajal' in username.lower():
        career_stage = 'entrepreneurial_transition'
    elif 'sneha' in username.lower():
        career_stage = 'creative_professional'
    elif 'prasanna' in username.lower():
        career_stage = 'business_owner'
    elif 'neha' in username.lower():
        career_stage = 'early_mid_career'
    elif 'dilasha' in username.lower():
        career_stage = 'creative_professional'
    elif 'shreish' in username.lower():
        career_stage = 'mid_career'
    
    # Get template for career stage
    template = PROFILE_TEMPLATES.get(career_stage, PROFILE_TEMPLATES['established_professional'])
    
    profile = {
        'user_id': username,
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat(),
        'demographics': {
            'name': demographics.get('name', 'User'),
            'email': demographics.get('email', ''),
            'username': username,
            **template['demographics']
        },
        'life_context': template['life_context'],
        'taste_profile': template['taste_profile'],
        'usage_stats': {
            'total_logins': 0,
            'last_login': None,
            'total_sessions': 0,
            'total_recommendations_requested': 0
        },
        'feedback_count': 0,
        'learning_history': []
    }
    
    return profile

def load_or_create_user_profile(username: str) -> Dict[str, Any]:
    """Load existing user profile or create a new one."""
    profiles_dir = 'user_profiles'
    os.makedirs(profiles_dir, exist_ok=True)
    
    profile_file = os.path.join(profiles_dir, f'{username}.json')
    
    if os.path.exists(profile_file):
        try:
            with open(profile_file, 'r') as f:
                profile = json.load(f)
            
            # Update last login
            profile['usage_stats']['total_logins'] += 1
            profile['usage_stats']['last_login'] = datetime.now().isoformat()
            
            return profile
        except Exception as e:
            print(f"Error loading profile for {username}: {e}")
    
    # Create new profile
    profile = create_default_profile(username)
    save_user_profile(profile)
    return profile

def save_user_profile(profile: Dict[str, Any]) -> bool:
    """Save user profile to file."""
    try:
        profiles_dir = 'user_profiles'
        os.makedirs(profiles_dir, exist_ok=True)
        
        profile['last_updated'] = datetime.now().isoformat()
        
        profile_file = os.path.join(profiles_dir, f'{profile["user_id"]}.json')
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

def update_user_login(username: str) -> bool:
    """Update user login statistics."""
    try:
        profile = load_or_create_user_profile(username)
        profile['usage_stats']['total_logins'] += 1
        profile['usage_stats']['last_login'] = datetime.now().isoformat()
        profile['usage_stats']['total_sessions'] += 1
        
        return save_user_profile(profile)
    except Exception as e:
        print(f"Error updating login stats: {e}")
        return False

def get_user_summary(username: str) -> Dict[str, Any]:
    """Get a summary of user profile and activity."""
    try:
        profile = load_or_create_user_profile(username)
        
        return {
            'name': profile['demographics']['name'],
            'career_stage': profile['life_context']['career_stage'],
            'total_logins': profile['usage_stats']['total_logins'],
            'feedback_count': profile.get('feedback_count', 0),
            'top_genres': list(profile['taste_profile']['genre_weights'].keys())[:3],
            'last_login': profile['usage_stats'].get('last_login'),
            'profile_completeness': min(profile.get('feedback_count', 0) / 20, 1.0)
        }
    except Exception as e:
        print(f"Error getting user summary: {e}")
        return {}

def get_all_user_summaries() -> Dict[str, Dict[str, Any]]:
    """Get summaries for all users."""
    summaries = {}
    
    for username in DEMO_USERS.keys():
        summaries[username] = get_user_summary(username)
    
    return summaries

def update_profile_activity(username: str, activity_type: str, data: Dict[str, Any] = None) -> bool:
    """Update user profile with activity data."""
    try:
        profile = load_or_create_user_profile(username)
        
        if activity_type == 'feedback_given':
            profile['feedback_count'] = profile.get('feedback_count', 0) + 1
        elif activity_type == 'recommendations_requested':
            profile['usage_stats']['total_recommendations_requested'] += 1
        
        # Add to learning history
        if data:
            learning_entry = {
                'timestamp': datetime.now().isoformat(),
                'activity_type': activity_type,
                'data': data
            }
            profile['learning_history'].append(learning_entry)
            
            # Keep only last 100 entries
            if len(profile['learning_history']) > 100:
                profile['learning_history'] = profile['learning_history'][-100:]
        
        return save_user_profile(profile)
    except Exception as e:
        print(f"Error updating profile activity: {e}")
        return False 