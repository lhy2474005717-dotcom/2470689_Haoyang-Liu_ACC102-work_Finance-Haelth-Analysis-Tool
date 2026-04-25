READ ME - Financial Health Analyzer

Overview:
Financial Health Analyzer is an interactive web application designed to evaluate a firm's financial condition using a multi-factor weighted scoring model. It integrates key financial metrics and allows users to customize weights to reflect different analytical preferences.

Key Functions:
1. Customizable Health Score
Users can adjust weights across four dimensions:Profitability (ROA),Solvency (Debt Ratio),Profit Margin,Sales Growth.
2. Peer Comparison
Support comparative analysis between enterprises and visually display differences through radar charts.
3. Financial Diagnosis
Automatically generate financial diagnostics to identify the strengths and potential risks of the firm.
4. Historical Trend Analysis
Support time series analysis to observe enterprise development trends.
5. Industry Benchmarking
Compare company performance against industry averages.


Installation & Setup:
Prerequisites - Python 3.8+ - pip (Python package manager)

Installation Steps:
1.Clone this repository (or download the source code)
2.Install required packages
- pip install -r requirements.txt
3.Prepare your data
Place your data2.csv file in the root directory of the project.Ensure the CSV follows the column format specified above.
4.Run the application
- streamlit run app.py
5.Access the application
Open your web browser automatically.

Data Source:
Compustat (via WRDS)
Compustat provides standardized, comparable financial data widely used in academic research and institutional investment.


Tech Stack:
-Python
-Streamlit
-Pandas / NumPy
-Plotly


Disclaimer:
This tool is for educational and informational purposes only and does not constitute investment advice.


Author
Haoyang Liu
Undergraduate in XJTLU,Economics & Finance
