"""
Test script for the enhanced movie recommendation system.
Run this to verify all components are working before Saturday.
"""

import sys
import os
import json
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import multi_user_profiles
        print("✅ multi_user_profiles imported successfully")
    except ImportError as e:
        print(f"❌ multi_user_profiles import failed: {e}")
        return False
    
    try:
        import profile_enhanced_scoring
        print("✅ profile_enhanced_scoring imported successfully")
    except ImportError as e:
        print(f"❌ profile_enhanced_scoring import failed: {e}")
        return False
    
    try:
        import profile_tracking_sheets
        print("✅ profile_tracking_sheets imported successfully")
    except ImportError as e:
        print(f"❌ profile_tracking_sheets import failed: {e}")
        return False
    
    try:
        from src.movie_scoring import recommend_movies
        print("✅ src.movie_scoring imported successfully")
    except ImportError as e:
        print(f"❌ src.movie_scoring import failed: {e}")
        return False
    
    try:
        from src.feedback_system import initialize_feedback_csv
        print("✅ src.feedback_system imported successfully")
    except ImportError as e:
        print(f"❌ src.feedback_system import failed: {e}")
        return False
    
    return True

def test_user_authentication():
    """Test user authentication system."""
    print("\n🔐 Testing user authentication...")
    
    try:
        import multi_user_profiles
        
        # Test valid users
        valid_users = ['sajal', 'sneha', 'prasanna', 'neha', 'dilasha', 'shreish']
        for username in valid_users:
            if multi_user_profiles.authenticate_user(username, 'pass123'):
                print(f"✅ Authentication successful for {username}")
            else:
                print(f"❌ Authentication failed for {username}")
                return False
        
        # Test invalid user
        if not multi_user_profiles.authenticate_user('invalid_user', 'pass123'):
            print("✅ Invalid user correctly rejected")
        else:
            print("❌ Invalid user incorrectly accepted")
            return False
        
        # Test invalid password
        if not multi_user_profiles.authenticate_user('sajal', 'wrong_password'):
            print("✅ Invalid password correctly rejected")
        else:
            print("❌ Invalid password incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_profile_creation():
    """Test user profile creation and loading."""
    print("\n👤 Testing profile creation...")
    
    try:
        import multi_user_profiles
        
        # Test profile creation for a new user
        username = 'test_user'
        profile = multi_user_profiles.create_default_profile(username)
        
        if profile and 'user_id' in profile:
            print("✅ Profile creation successful")
        else:
            print("❌ Profile creation failed")
            return False
        
        # Test profile loading
        loaded_profile = multi_user_profiles.load_or_create_user_profile(username)
        if loaded_profile and loaded_profile['user_id'] == username:
            print("✅ Profile loading successful")
        else:
            print("❌ Profile loading failed")
            return False
        
        # Test profile saving
        if multi_user_profiles.save_user_profile(loaded_profile):
            print("✅ Profile saving successful")
        else:
            print("❌ Profile saving failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
        return False

def test_enhanced_scoring():
    """Test the enhanced scoring system."""
    print("\n🎯 Testing enhanced scoring...")
    
    try:
        import profile_enhanced_scoring
        
        # Test genre ID mapping
        genre_id = profile_enhanced_scoring.get_genre_id('drama')
        if genre_id == '18':
            print("✅ Genre ID mapping working")
        else:
            print(f"❌ Genre ID mapping failed: expected '18', got '{genre_id}'")
            return False
        
        # Test personalized score calculation
        mock_movie = type('MockMovie', (), {
            'title': 'Test Movie',
            'genres': [type('MockGenre', (), {'name': 'drama'})()],
            'popularity': 50,
            'vote_average': 7.5,
            'release_date': '2020-01-01'
        })()
        
        mock_genre_weights = {'drama': 0.8}
        mock_cast_preferences = {}
        mock_director_preferences = {}
        mock_mood_preferences = {}
        
        score = profile_enhanced_scoring.calculate_personalized_score(
            mock_movie, mock_genre_weights, mock_cast_preferences,
            mock_director_preferences, mock_mood_preferences,
            'established_professional', 'medium', set(), set(), set()
        )
        
        if isinstance(score, float) and 0 <= score <= 1:
            print(f"✅ Personalized scoring working (score: {score:.3f})")
        else:
            print(f"❌ Personalized scoring failed: {score}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced scoring test failed: {e}")
        return False

def test_profile_tracking():
    """Test profile tracking functionality."""
    print("\n📊 Testing profile tracking...")
    
    try:
        import profile_tracking_sheets
        
        # Test profile update function
        mock_profile = {
            'user_id': 'test_user',
            'taste_profile': {
                'genre_weights': {'drama': 0.5},
                'cast_preferences': {},
                'director_preferences': {}
            },
            'feedback_count': 0
        }
        
        mock_feedback = {
            'movie_obj': type('MockMovie', (), {'title': 'Test Movie', 'id': 123})(),
            'response': 'Yes',
            'liked': None
        }
        
        updated_profile = profile_tracking_sheets.enhanced_update_profile_from_feedback(
            mock_profile, mock_feedback
        )
        
        if updated_profile and updated_profile['feedback_count'] == 1:
            print("✅ Profile tracking working")
        else:
            print("❌ Profile tracking failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Profile tracking test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'main_app.py',
        'multi_user_profiles.py',
        'profile_enhanced_scoring.py',
        'profile_tracking_sheets.py',
        'requirements.txt',
        'src/movie_scoring.py',
        'src/feedback_system.py',
        'src/movie_search.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {missing_files}")
        return False
    
    return True

def test_user_profiles_directory():
    """Test user profiles directory creation."""
    print("\n📂 Testing user profiles directory...")
    
    try:
        import multi_user_profiles
        
        # This should create the directory
        profile = multi_user_profiles.create_default_profile('test_dir_user')
        multi_user_profiles.save_user_profile(profile)
        
        if os.path.exists('user_profiles'):
            print("✅ User profiles directory created")
            
            # Check if profile file was created
            profile_file = os.path.join('user_profiles', 'test_dir_user.json')
            if os.path.exists(profile_file):
                print("✅ Profile file created successfully")
                
                # Clean up test file
                os.remove(profile_file)
                print("✅ Test profile file cleaned up")
            else:
                print("❌ Profile file not created")
                return False
        else:
            print("❌ User profiles directory not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ User profiles directory test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Movie Recommendation System - Pre-Launch Tests")
    print("=" * 60)
    print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("User Authentication", test_user_authentication),
        ("Profile Creation", test_profile_creation),
        ("Enhanced Scoring", test_enhanced_scoring),
        ("Profile Tracking", test_profile_tracking),
        ("User Profiles Directory", test_user_profiles_directory)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for Saturday.")
        print("\n📋 Next Steps:")
        print("1. Run: streamlit run main_app.py")
        print("2. Test with demo users (sajal, sneha, etc.)")
        print("3. Verify UI responsiveness on mobile")
        print("4. Check Google Sheets integration (if configured)")
    else:
        print("⚠️ Some tests failed. Please fix issues before Saturday.")
        print(f"Failed tests: {total - passed}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 