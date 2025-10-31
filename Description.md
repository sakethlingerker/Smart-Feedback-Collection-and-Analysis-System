# **Feedback Analytics & Sentiment Analysis Dashboard**

## **Project Overview**

This is a comprehensive **web-based analytics platform** that collects, analyzes, and visualizes user feedback using artificial intelligence and data visualization techniques. The system automatically processes customer feedback to extract sentiment, emotions, and key topics, presenting them through an interactive admin dashboard with real-time charts and insights.

---

## **Tech Stack Used**

### **Frontend (Client-Side)**
- **HTML5/CSS3**: For structure and responsive styling
- **Vanilla JavaScript**: Core application logic and DOM manipulation
- **Chart.js**: Interactive data visualizations and cxharts
- **Modern CSS**: Gradient backgrounds, flexbox, grid layouts

### **Backend (Inferred from API calls)**
- **RESTful API Server** (running on localhost:5000)
- **Python/Node.js**: Likely backend framework
- **AI/NLP Libraries**: For sentiment analysis and emotion detection
- **Database**: Persistent storage for feedback data
- **Authentication System**: JWT-based auth management

### **Key Libraries & Dependencies**
- **Chart.js**: For all data visualizations
- **Custom Auth Manager**: Handles user sessions and permissions
- **Fetch API**: For HTTP requests to backend services

---

## **Core Features**

### **1. Multi-Layer Authentication System**
- Role-based access control (Guest, User, Admin)
- Automatic redirects for unauthorized users
- Secure API calls with authentication headers

### **2. Comprehensive Analytics Dashboard**
- **8 Interactive Chart Types**:
  - Sentiment distribution (Doughnut)
  - Rating frequency (Bar chart)
  - Emotion analysis (Polar area)
  - Priority action matrix (Bubble chart)
  - Historical trends (Line chart)
  - Live sentiment meter (Gauge)
  - Topic-sentiment correlation (Stacked bar)
  - Sentiment intensity (Detailed breakdown)

### **3. Real-time Data Processing**
- Auto-refresh every 30 seconds
- Live sentiment scoring
- Dynamic chart updates
- Real-time metrics display

### **4. Advanced Feedback Management**
- **Feedback Submission System**:
  - Text-based feedback input
  - Star rating system (1-5 stars)
  - Category classification
  - Anonymous and authenticated submissions

- **Feedback Display & Management**:
  - Recent feedback listing
  - Delete functionality with confirmation modals
  - Detailed metadata display (polarity, subjectivity, analysis method)

### **5. AI-Powered Analysis**
- **Sentiment Analysis**: Positive/Negative/Neutral classification
- **Emotion Detection**: Joy, Trust, Fear, Surprise, Sadness, Anger
- **Text Analysis**: Polarity and subjectivity scoring
- **Topic Extraction**: Automatic categorization of feedback topics
- **Word Cloud Generation**: Visual representation of common terms

### **6. Data Export & Reporting**
- Multiple export formats: CSV, PDF, JSON
- Automated report generation
- Download functionality for offline analysis

### **7. Error Handling & User Experience**
- Toast notifications for errors
- Loading states and progress indicators
- Responsive design for all devices
- Graceful degradation for failed API calls

---

## **User Types & Their Capabilities**

### **👤 Guest Users**
- Submit feedback anonymously
- No authentication required
- Basic feedback form access
- **Cannot**: View analytics, access dashboard, or see history

### **👥 Registered Users**
- Submit authenticated feedback
- View personal feedback history
- Track own submission patterns
- Update profile information
- **Cannot**: Access admin dashboard or analytics

### **👑 Administrator Users**
- **Full dashboard access** with all 8 chart types
- View and analyze **all user feedback**
- Delete any feedback submissions
- Access **real-time analytics** and trends
- Generate **word clouds** and topic analysis
- Export data in multiple formats
- Monitor system performance metrics
- Manage user permissions and access

---

## **Key Differentiators**

1. **AI-Driven Insights**: Goes beyond basic charts to provide emotional and topical analysis
2. **Real-time Processing**: Live data updates without page refresh
3. **Actionable Intelligence**: Priority matrix helps identify critical issues
4. **Enterprise Security**: Robust role-based access control
5. **Comprehensive Export**: Multiple formats for different use cases

This system transforms raw customer feedback into **actionable business intelligence**, helping organizations understand customer sentiment, identify pain points, and make data-driven decisions to improve products and services.