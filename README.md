# UrbanFarm AI 🌱

An intelligent desktop application for sustainable urban farming, providing data-driven crop recommendations and expert sustainability advice.

## Features

### 1. Crop Advisor 🌾
- **Smart Crop Recommendations**: Get personalized crop suggestions based on:
  - Soil parameters (N, P, K, pH)
  - Climate conditions (Temperature, Humidity, Rainfall)
- **Supported Crops**: Rice, Maize, Pomegranate, Banana, Mango, Apple, Orange, Cotton, Jute, Coffee
- **High Accuracy**: 99%+ prediction accuracy using Random Forest model
- **Top 3 Recommendations**: View best matches with confidence scores
- **Detailed Reports**: Generate comprehensive analysis with growing tips

### 2. Sustainability Assistant 🤖
- Interactive chatbot providing expert advice on:
  - Urban farming best practices
  - Sustainable agriculture techniques
  - Crop-specific growing tips
  - Water management strategies
  - Soil health maintenance
- Context-aware responses
- Natural conversation interface

## Technical Details

### Requirements
- Python 3.8+
- Required packages:
  ```
  customtkinter
  pandas
  numpy
  scikit-learn
  joblib
  ```

### Installation
1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app/main.py
   ```

### Project Structure
```
app/
├── data/               # Dataset and model data
├── models/            # Trained models
├── utils/             # Utility modules
│   ├── data_processor.py    # Data handling and model training
│   ├── interface.py         # UI components
│   └── sustainability_bot.py # Chatbot implementation
└── main.py           # Main application
```

## Usage

1. **Crop Recommendation**:
   - Adjust soil and climate parameters using sliders
   - Click "Get Crop Recommendation"
   - View top 3 recommended crops with confidence scores
   - Generate detailed report if needed

2. **Sustainability Tips**:
   - Navigate to the Sustainability Tips tab
   - Type your farming-related questions
   - Get expert advice and recommendations
   - Engage in natural conversation about urban farming

## Model Details

- **Algorithm**: Random Forest Classifier
- **Features**: 7 (N, P, K, Temperature, Humidity, pH, Rainfall)
- **Training Data**: Comprehensive crop dataset
- **Accuracy**: 99%+ on test set
- **Output**: Multi-class prediction with probability scores

## Contributing

Feel free to contribute to this project by:
1. Forking the repository
2. Creating a feature branch
3. Committing your changes
4. Opening a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset source: [Crop Recommendation Dataset]
- Built with CustomTkinter for modern UI
- Powered by scikit-learn for machine learning 