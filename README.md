# 📖 ReviewBud  
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![Render](https://img.shields.io/badge/Deployed%20on-Render-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **Streamline your business reviews with AI-powered review generation and QR code magic.**

ReviewBud helps business owners create QR codes that customers can scan to leave AI-generated Google reviews with just a few clicks. No more struggling to get customers to write reviews – our AI does the heavy lifting while keeping it authentic and personalized.

🌐 **Live Demo:** [reviewbud.co](https://reviewbud.co)

---

## 🚀 Features

### ✅ **Currently Available**
- **Business Management**: Create account and manage multiple businesses
- **QR Code Generation**: Generate custom QR codes for each business location
- **Print-Ready Cards**: Create professional QR code cards ready for printing
- **AI Review Generation**: Smart review creation with OpenAI integration
- **Seamless Google Integration**: Direct posting to Google Reviews with copied text
- **Customer-Friendly Interface**: Simple few-click process for customers

### 🔧 **Coming Soon**
- **💳 Stripe Payment Integration**: Monetization for premium features
- **📊 Admin Dashboard**: Analytics and business insights
- **🛍️ Online Store**: Purchase physical QR code cards and NFC cards
- **📈 Review Analytics**: Track review performance and customer engagement

---

## 🛠️ Tech Stack

**Backend:**
- Django (Python web framework)
- Google OAuth for authentication
- OpenAI API for review generation
- Google Places API for business integration

**Frontend:**
- HTML/CSS with server-side rendering
- Vanilla JavaScript for interactivity

**Deployment:**
- Hosted on Render.com
- Custom domain: reviewbud.co

---

## 🏃‍♂️ Quick Start  

### Local Development
```bash
# Clone the repository
git clone https://github.com/zohirhamid/reviewbud.git
cd reviewbud

# Install dependencies
pip install -r requirements.txt

# Run the development server
python manage.py runserver
