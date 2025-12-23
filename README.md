# AI-Financial-Research-Agent
AI Financial Research Agent is a professional-grade AI & Machine Learning–powered financial intelligence platform that delivers real-time market analysis, predictive insights, and institutional-quality reporting.
The platform uses Machine Learning, Generative AI, and automated analytics to convert raw financial data into actionable investment intelligence.

## Problem Statement
### Challenges

- Information overload with no clear insights

- Expensive and inaccessible professional tools

- Fragmented financial data across multiple platforms

- Manual analysis that is slow and biased

- Lack of professional, decision-ready reports

### Market Need

- Institutional-quality financial analysis

- Real-time crypto and stock monitoring

- **Machine Learning–driven insights**

- Risk-aware investment decisions

- Automated professional reporting

## Solution

A unified AI-powered financial intelligence platform that provides:

- Real-time multi-source market data

- Machine Learning models for prediction and risk scoring

- Generative AI–based financial insights

- Interactive visual analytics

- Automated PDF reporting

## AI & Machine Learning

- This project actively uses Machine Learning for:

- Risk scoring and volatility modeling

- Trend and pattern detection

- Technical indicator analysis (RSI, MACD, Moving Averages)

- News sentiment analysis using NLP

- Buy / Hold / Sell recommendation engine

- Risk-based position sizing

## Core Features
### Real-Time Market Intelligence

**[Dashboard Preview](https://github.com/Hassan0397/AI-Financial-Research-Agent/blob/main/Dashboard%20page%20preview%20.png)**

- Live cryptocurrency prices (100+ assets)

- Stock market quotes and fundamentals

- Market news aggregation with sentiment analysis

- Smart asset detection (Crypto vs Stock)

- Price discrepancy alerts

### AI-Powered Analysis

**[AI-Analysis Preview](https://github.com/Hassan0397/AI-Financial-Research-Agent/blob/main/Analysis%20Page%20Preview.png)**

- Machine learning–based risk assessment (1–10 scale)

- Technical and trend analysis

- Sentiment scoring from financial news

- Trading recommendations with confidence levels

- Risk-aware position sizing

### Visualization

- Interactive candlestick and volume charts

- Multi-timeframe technical analysis

- Market sentiment dashboards

- Portfolio performance analytics

### Professional Reporting

**[Report Preview 1](https://github.com/Hassan0397/AI-Financial-Research-Agent/blob/main/Report%20Generator%20page%20Preview%201.png)**

**[Report Preview 2](https://github.com/Hassan0397/AI-Financial-Research-Agent/blob/main/Report%20Generator%20page%20Preview%202.png)**

**[Report Preview 3](https://github.com/Hassan0397/AI-Financial-Research-Agent/blob/main/Report%20Generator%20page%20Preview%203.png)**

- One-click PDF report generation

- Executive and investment memo templates

- Risk matrices and action plans

- Confidential watermarks

## Enterprise Capabilities

- Multi-source data verification

- Smart caching system

- Graceful error handling

- API-first architecture

- Scalable and modular design

## Architecture
### Frontend

- Streamlit-based user interface

- Plotly interactive visualizations

- Professional custom CSS

### Backend Services

- **ai_engine.py** – Machine learning and AI analysis engine

- **data_fetch.py** – Multi-source data aggregation

- **news_fetch.py** – News collection and sentiment analysis

- **report_gen.py** – Automated PDF reporting

## Data Flow

User Input

↓
   
Data Fetching

↓
   
Multi-Source Verification

↓
   
Machine Learning Analysis

↓
   
AI Insight Generation

↓

Visualization

↓
   
PDF Report

## Technology Stack
### Frontend & Visualization

- Streamlit

- Plotly

- Custom CSS

- FPDF

### Data Processing

- Pandas

- NumPy

- yFinance

### AI & Machine Learning

- Scikit-learn

- Llama 3 (Ollama)

- OpenAI GPT-4

- TextBlob (NLP)

### APIs

- CoinGecko

- CoinCap

- Yahoo Finance

- Google News RSS

## Use Cases

- Retail investors seeking AI-driven insights

- Financial analysts and advisors

- Market research and education

- Institutional monitoring and reporting

## Getting Started

### 1️⃣ Create a virtual environment

**Windows:**

python -m venv myenv


**Linux/macOS:**

python3 -m venv myenv


Here, myenv is the name of your virtual environment. You can choose any name.

### 2️⃣ Activate the virtual environment

**Windows (Command Prompt):**

myenv\Scripts\activate


**Windows (PowerShell):**

.\myenv\Scripts\Activate.ps1


**Linux/macOS:**

source myenv/bin/activate


You should now see (myenv) at the start of your terminal prompt.

### 3️⃣ Install required packages

Make sure Streamlit is installed:

pip install streamlit


If your project has a requirements.txt, install dependencies using:

pip install -r requirements.txt

### 4️⃣ Run the Streamlit app
streamlit run app.py


After running this, Streamlit will open your app in the default web browser.
