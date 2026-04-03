# 🏎️ Formula 1 Telemetry Analysis Project


[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastF1](https://img.shields.io/badge/FastF1-3.0+-red.svg)](https://github.com/theOehrly/Fast-F1)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end data analysis and machine learning project that explores Formula 1 race telemetry, lap times, tyre strategies, and driver performance using the FastF1 API.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project analyzes Formula 1 race data with a focus on the **2021 Abu Dhabi Grand Prix** – one of the most controversial and dramatic championship finales in F1 history. The analysis includes:

- **Telemetry Analysis**: Speed, throttle, brake, and gear usage
- **Lap Time Prediction**: Machine learning models (RMSE ≈ 1-2 seconds)
- **Strategy Analysis**: Tyre compound performance and degradation
- **Driver Comparison**: Verstappen vs Hamilton battle analysis
- **Interactive Dashboard**: Streamlit app for real-time exploration

---

## ✨ Features

### 📊 Data Analysis
- Load and analyze F1 sessions (races, qualifying, practice)
- Clean and preprocess lap data
- Compare multiple drivers' performance
- Visualize lap time evolution throughout races

### 🏎️ Telemetry Visualization
- Speed traces along the circuit
- Throttle and brake application patterns
- Gear usage and RPM analysis
- Track position mapping with color-coded metrics

### 🔧 Strategy Insights
- Tyre compound usage patterns
- Stint-by-stint performance analysis
- Degradation curves for different compounds
- Pit stop timing optimization

### 🤖 Machine Learning
- Lap time prediction using Random Forest, Gradient Boosting, and Linear Regression
- Feature importance analysis
- Model comparison and evaluation
- Real-world prediction validation

### 🖥️ Interactive Dashboard
- Multi-page Streamlit application
- Real-time data exploration
- Driver and session selection
- Dynamic visualizations

---

## 📁 Project Structure

```
f1_telemetry_project/
│
├── notebooks/
│   ├── 01_abu_dhabi_2021_exploration.ipynb    # Data exploration & visualization
│   └── 02_laptime_prediction_ml.ipynb         # Machine learning models
│
├── utils/
│   └── f1_helper.py                            # Reusable utility functions
│
├── data_cache/                                 # FastF1 cached data
│
├── app.py                                      # Streamlit dashboard
├── requirements.txt                            # Python dependencies
├── README.md                                   # This file
└── .gitignore                                  # Git ignore rules
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/MenushJagathchandra/f1-telemetry-analysis.git
cd f1-telemetry-analysis
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Jupyter Notebooks

Launch Jupyter Lab:
```bash
jupyter lab
```

**Notebook 1**: Data Exploration
- Open `notebooks/01_abu_dhabi_2021_exploration.ipynb`
- Run cells sequentially to explore race data
- Visualize telemetry and lap times

**Notebook 2**: Machine Learning
- Open `notebooks/02_laptime_prediction_ml.ipynb`
- Train and evaluate prediction models
- Analyze feature importance

### Streamlit Dashboard

Launch the interactive dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Features:**
- Select year, Grand Prix, and session type
- Compare multiple drivers
- View telemetry traces
- Analyze tyre strategies
- Explore session statistics

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


**⭐ If you found this project useful, please consider giving it a star!**