# UrbanFarm AI - Sustainable Urban Farming Assistant

An AI-powered web application that helps urban farmers optimize crop selection and resource use, promoting sustainable urban agriculture.

## 🌱 Features

- **AI Crop Advisor**: Machine learning model that recommends crops based on:
  - Soil characteristics
  - Climate conditions
  - Urban constraints (space, sunlight)
  
- **Sustainability Tips**: AI-powered chatbot providing:
  - Resource-saving practices
  - Farming best practices
  - Local climate adaptation advice

- **Plant Health Diagnosis**: Mobile-friendly features including:
  - Camera-based plant health analysis
  - Offline capability using TensorFlow Lite
  - Disease detection and treatment recommendations

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Machine Learning**: 
  - Scikit-learn (Crop Recommendation)
  - TensorFlow (Plant Health)
  - Hugging Face Transformers (Chatbot)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

## 🚀 Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app/main.py
   ```

## 📊 Dataset

The application uses the Crop Recommendation Dataset for training the crop recommendation model. The dataset includes:
- Soil parameters (N, P, K, pH)
- Climate conditions (temperature, humidity, rainfall)
- Crop labels

## 🌍 Sustainable Development Goals

This project contributes to:
- SDG 11: Sustainable Cities and Communities
- SDG 12: Responsible Consumption and Production
- SDG 13: Climate Action

## 📝 License

MIT License - See LICENSE file for details 