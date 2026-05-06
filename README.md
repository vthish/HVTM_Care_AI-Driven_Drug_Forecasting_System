# 🧠 HVTM CARE

### AI-Driven Pharmaceutical Inventory Forecasting System

HVTM CARE is an advanced AI-powered pharmaceutical inventory forecasting platform designed to transform how healthcare institutions manage drug stock, predict demand, and prevent shortages.

By combining machine learning, deep learning, and ensemble intelligence, the system enables data-driven decision-making for smarter pharmaceutical inventory planning.

---

## 🚀 Project Vision

Modern healthcare systems struggle with balancing drug availability and inventory costs.
HVTM CARE aims to bridge this gap by delivering:

* 📊 Accurate demand forecasting
* ⚠️ Early shortage risk detection
* 📦 Smarter procurement planning

This system empowers pharmacies, hospitals, and healthcare providers to move from reactive stock management to **predictive, AI-driven planning**.

---

## 🧩 Core Capabilities

### 📈 Intelligent Demand Forecasting

Leverages historical pharmaceutical data to predict future drug demand with high accuracy, helping reduce both understocking and overstocking.

### ⚠️ Shortage Risk Intelligence

Identifies potential inventory risks early by analyzing predicted demand patterns and stock behavior.

### 📦 Smart Inventory Planning

Provides actionable insights for optimizing stock levels, minimizing wastage, and improving supply chain efficiency.

### 🧠 NeuroStack Ensemble Engine

A meta-learning inspired ensemble system that combines multiple models to produce more stable and reliable predictions.

### 🔬 Deep Learning Forecasting

Implements sequence-aware models such as **BiLSTM** and **GRU** to capture temporal patterns and seasonal demand fluctuations.

### ⚖️ Model Benchmarking System

Includes classical ML models (Random Forest, XGBoost, Linear Regression) to compare and validate prediction performance.

### 🌐 Unified Web Dashboard

Interactive interface for running predictions, visualizing results, and supporting decision-making in real time.

---

## 🧠 AI Architecture Overview

HVTM CARE follows a **multi-layer intelligent forecasting pipeline** instead of relying on a single model.

```
Historical Data
   ↓
Data Preprocessing & Feature Engineering
   ↓
ML Models + Deep Learning Models
   ↓
Model Evaluation & Comparison
   ↓
NeuroStack Ensemble Integration
   ↓
FastAPI Prediction Engine
   ↓
Web Dashboard Visualization
```

This hybrid approach improves robustness, accuracy, and adaptability of predictions.

---

## 🤖 Models & Techniques Used

### 🔹 Deep Learning

* BiLSTM (Bidirectional Long Short-Term Memory)
* GRU (Gated Recurrent Unit)

### 🔹 Machine Learning

* Linear Regression
* Random Forest
* XGBoost
* Optimized Ensemble Models

### 🔹 Advanced Concepts

* Ensemble Learning
* Meta-Learning (NeuroStack)
* Time Series Forecasting
* Feature Engineering

---

## 🛠️ Technology Stack

### 🔬 AI & Data Science

* Python
* Pandas / NumPy
* Scikit-learn
* TensorFlow / Keras
* XGBoost

### ⚙️ Backend

* FastAPI
* REST API Architecture
* Joblib (model serialization)

### 🎨 Frontend

* HTML / CSS / JavaScript
* Responsive Dashboard UI

### 📊 Data & Experimentation

* Jupyter Notebooks
* Data Preprocessing Pipelines
* Model Evaluation & Comparison

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/hashan-7/hvtm-care-pharma-forecasting.git
cd hvtm-care-pharma-forecasting
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### 3️⃣ Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the System

### 🔹 Start Backend Server

```bash
cd backend
uvicorn app:app --reload
```

Backend will run on:

```
http://127.0.0.1:8000
```

---

### 🔹 Launch Frontend

Open:

```
frontend/index.html
```

(Recommended: use VS Code Live Server)

---

## 🧪 How to Use

1. Start backend server
2. Open frontend dashboard
3. Input pharmaceutical inventory data
4. Run prediction
5. Analyze forecasted demand
6. Use insights for stock planning and risk reduction

---

## 📂 Dataset

The system uses pharmaceutical inventory datasets containing historical drug consumption patterns.

**Main Files:**

* `drugs.csv`
* `drugs_featured.csv`

These datasets power:

* Data preprocessing
* Feature engineering
* Model training
* Forecasting

---

## 📊 Model Evaluation

The project includes comprehensive evaluation pipelines to compare models based on:

* Prediction accuracy
* Error metrics
* ML vs Deep Learning performance
* Ensemble effectiveness
* Demand trend analysis

---

## 🔐 Production Considerations

For real-world deployment, the following enhancements are recommended:

* Secure authentication system
* Environment-based configuration management
* Input validation & API security
* Database integration
* Logging & monitoring
* Role-based access control
* CI/CD pipeline setup

---

## 🔮 Future Enhancements

* Real-time economic data integration
* Automated procurement cost estimation
* Cloud deployment (AWS / GCP)
* Continuous model retraining
* Self-learning system updates
* Advanced shortage alert engine
* Analytics dashboard & reporting

---

## 🎯 Project Impact

HVTM CARE demonstrates how AI can be applied in healthcare to:

* Improve drug availability
* Reduce wastage and costs
* Enable predictive decision-making
* Strengthen pharmaceutical supply chains

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Developed as an AI-driven solution for modern healthcare inventory challenges.

---
