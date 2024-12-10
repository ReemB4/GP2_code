# PDPrognosis

<img src="/PDPrognosis.jpeg" width='400'>
<h2>Introduction</h1>
<p>PDPrognosis is a graduation project that offers a user-friendly platform designed to streamline the management of Parkinson's disease for doctors. It provides time-saving tools and comprehensive insights into patients' protein and peptide profiles, aiding doctors in making informed decisions with ease, and ensures all relevant information is readily accessible for effective patient care.</p>
<h2>Technology</h1> 
<ul>
<li>Digital Ocean hosting services.</li>
<li>TensorFlow and GPflow are tools for machine learning. </li>
<li>Anaconda as a tool for managing Python environments.</li>
<li>Visual Studio Code</li>
<li>Python</li>
<li>Html</li>
<li>CSS</li>
<li>JavaScript</li>
</ul>
<h2>Launching Instructions</h1> 

To run and deploy the code in this repository, follow these detailed instructions:

---

### **1. Clone the Repository**
Ensure that Git is installed on your system. Open your terminal or command prompt and run:

```bash
git clone https://github.com/ReemB4/GP2_code.git
cd GP2_code
```

---

### **2. Set Up the Environment**

#### **Using Python Virtual Environment**
1. Create a virtual environment:
   ```bash
   python3 -m venv env
   ```

2. Activate the virtual environment:
   - **On Windows**:
     ```bash
     .\env\Scripts\activate
     ```
   - **On macOS/Linux**:
     ```bash
     source env/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### **3. Prepare the Application**

#### **Configuration**
- Ensure the necessary datasets (e.g., protein and peptide data) are available in the appropriate directory or paths specified in the code.
- If the application uses `.env` for environment variables, create a `.env` file in the root directory and configure it with the required settings (e.g., API keys, database connections, or application secrets).

---

### **4. Run the application Locally**

#### **Flask Application**
1. Start the Flask development server:
   ```bash
   flask run
   ```
2. If a specific script (e.g., `create_database.py`,` app.py`) needs to be executed:
   ```bash
   python create_database.py
   python app.py
   ```

#### **Access the Application**
- Open your browser and navigate to:
  ```
  http://127.0.0.1:5000
  ```

### **Troubleshooting**
- Verify Python version compatibility (as specified in `requirements.txt`).
- Check for missing dependencies or library versions and update if necessary.
- Ensure your system meets the hardware/software requirements for the application.



---

### GP2 code Features

The GP2 Code application provides tools for analyzing Parkinson’s disease progression, including:
- Protein and Peptide Insights: Fetches detailed data from the UniProt API.
- Patient History: Tracks patient visits and progression over time.
- Comparisons: Compares data across patient visits and between patients.
- Clustering: Groups patients into meaningful subpopulations using clustering techniques.
- Regression Analysis: Predicts UPDRS scores with advanced machine learning models like XGBoost.

---
The source code: [PDPrognosis on GitHub](https://github.com/sarahksu7/2024-GP-08)
The source code: [PDPrognosis on GitHub]((https://github.com/ReemB4/GP2_code)) 
