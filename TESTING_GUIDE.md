# 🧪 Enhanced Movie Recommendation System - Testing Guide

## 🚀 Quick Start

### 1. Run Automated Tests
```bash
python test_enhanced_system.py
```

### 2. Start the Application
```bash
streamlit run main_app.py
```

## 📋 Manual Testing Checklist

### ✅ **1. Authentication Test**
- [ ] Try logging in as each user:
  - **sajal** (password: pass123)
  - **sneha** (password: pass123)
  - **prasanna** (password: pass123)
  - **neha** (password: pass123)
  - **dilasha** (password: pass123)
  - **shreish** (password: pass123)
- [ ] Verify profile loads correctly for each user
- [ ] Check that invalid credentials are rejected

### ✅ **2. Movie Search Test**
- [ ] Search for a movie (e.g., "Inception", "The Dark Knight")
- [ ] Verify search results appear with posters
- [ ] Add a movie to favorites
- [ ] Verify it appears in "Your Selected Movies" section
- [ ] Test removing movies from favorites

### ✅ **3. Recommendation Test**
- [ ] Add exactly 5 favorite movies
- [ ] Click "🎬 Get My Recommendations"
- [ ] Verify personalized recommendations appear
- [ ] Check that different users get different recommendations
- [ ] Verify recommendation scores are displayed

### ✅ **4. Profile Learning Test**
- [ ] Rate some movies (Yes/No/Already watched)
- [ ] Check sidebar stats update (Movies Rated, Actors Learned, etc.)
- [ ] Verify profile learning is working
- [ ] Test the "🧠 Show My Profile" button in sidebar

### ✅ **5. Mobile Test**
- [ ] Test on phone browser
- [ ] Check if UI is responsive
- [ ] Verify touch interactions work
- [ ] Test login form on mobile

### ✅ **6. Multi-User Test**
- [ ] Login as different users
- [ ] Verify each gets different recommendations
- [ ] Check that profiles don't interfere with each other
- [ ] Test logout functionality

## 🎯 **Expected Behaviors**

### **User Profiles**
- **Sajal**: Entrepreneurial transition → Motivational/business movies
- **Sneha**: Creative professional → Artistic/visually stunning movies
- **Prasanna**: Business owner → Leadership/success stories
- **Neha**: Early mid-career → Trendy/social movies
- **Dilasha**: Creative professional → Artistic/emotional movies
- **Shreish**: Mid-career → Quality entertainment/family movies

### **UI Features**
- Modern gradient styling
- Personalized greetings based on career stage
- User stats dashboard in sidebar
- Enhanced movie cards with hover effects
- Mobile-responsive design

### **Learning System**
- Profile updates based on movie ratings
- Genre, cast, and director preference learning
- Feedback count tracking
- Session activity logging

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **TMDB API Issues**
   - Check if TMDB_API_KEY is set in Streamlit secrets
   - Verify internet connection

3. **Google Sheets Issues**
   - Check if GOOGLE_SHEETS credentials are configured
   - System works without Google Sheets (fallback to local storage)

4. **Profile Loading Issues**
   - Check if `user_profiles` directory exists
   - Verify file permissions

### **Performance Notes**
- First recommendation generation may take 30-60 seconds
- Subsequent recommendations use caching
- Mobile performance may be slower on older devices

## 📊 **Success Criteria**

### **All Tests Pass When:**
- [ ] All 6 demo users can log in successfully
- [ ] Movie search returns results with posters
- [ ] 5 movies can be added and recommendations generated
- [ ] Different users get different recommendations
- [ ] Profile learning updates stats in sidebar
- [ ] UI is responsive on mobile devices
- [ ] Logout works and clears session

### **Bonus Features Working:**
- [ ] Google Sheets integration (if configured)
- [ ] Profile export functionality
- [ ] Advanced recommendation algorithms
- [ ] Real-time activity tracking

## 🎉 **Ready for Saturday When:**
- All manual tests pass
- Automated test script shows "ALL TESTS PASSED"
- UI looks professional and modern
- Multi-user functionality works correctly
- Mobile experience is smooth

---

**Last Updated:** $(date)
**System Version:** Enhanced v1.0
**Test Status:** Ready for Saturday launch! 🚀 