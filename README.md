# 🩺 Human Disease Diagnosis System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-success)
![Status](https://img.shields.io/badge/Status-Deployed-brightgreen)

**Live Demo:** [(https://disease-diagnosis-system-rouw.onrender.com)]

## 📌 Project Overview
The Human Disease Diagnosis System is an intelligent, full-stack web application designed to predict potential medical conditions based on user-reported symptoms. It integrates a trained Machine Learning model with a secure, multi-user web interface to provide instant diagnostic insights.

Moving beyond basic single-class prediction, this system utilizes a **Diagnostic Confidence Matrix** to provide users with a probabilistic breakdown of potential conditions, mimicking real-world differential diagnosis. It is fully mobile-responsive and deployed to the cloud.

## ✨ Key Features
* **AI-Powered Diagnosis:** Utilizes a Random Forest Classifier trained on 132 unique medical symptoms to predict over 40 distinct diseases.
* **Diagnostic Confidence Matrix:** Calculates and displays the top 3 most probable diseases with dynamic percentage confidence bars.
* **Secure User Authentication:** Full session management with hashed passwords for secure access.
* **Private Medical History:** A relational database architecture ensures users can securely log, view, and delete their own diagnostic records.
* **Automated Report Generation:** Built-in functionality to save clinical reports as PDFs.
* **Data Export:** Instantly export medical history to Excel-compatible CSV files.
* **Modern UI/UX:** A fully responsive card-based layout featuring a seamless Light/Dark Mode toggle, dynamic search filtering, and native-feeling mobile views.

## 🛠️ Technology Stack
**Frontend:** HTML5, CSS3 (Custom Variables, CSS Flexbox/Grid), Vanilla JavaScript
**Backend:** Python 3, Flask, Flask-Login, Werkzeug Security
**Machine Learning:** Scikit-Learn 1.8.0 (Random Forest), NumPy, Pandas
**Database:** PostgreSQL (Cloud Production) / SQLite (Local Development)
**Deployment:** Render, Gunicorn WSGI

## 🚀 How to Run Locally

1. Clone the repository:
   
   git clone [https://github.com/yourusername/Disease-Diagnosis-System.git](https://github.com/chintashyamala/Disease-Diagnosis-System.git)
   cd Disease-Diagnosis-System

2. Create a virtual environment:

    python -m venv venv
# On Windows use: venv\Scripts\activate
# On Mac/Linux use: source venv/bin/activate

3. Install dependencies:

    pip install -r requirements.txt

4. Run the application:

    python app.py

5. Access the portal:

    Open your browser and navigate to http://127.0.0.1:5000


⚠️ Disclaimer
This application was developed for educational and research purposes as part of a computer science curriculum. It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified health provider with any questions you may have regarding a medical condition.