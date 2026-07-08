# 🛍️ Online Retail Insights Dashboard

**🔗 Streamlit Application:**  
https://micp-retail-online.streamlit.app/

An interactive Streamlit dashboard built to analyze retail transaction data, featuring robust data validation and dynamic report slides.

This app is designed to make data-driven decisions easy. To ensure accuracy, it automatically validates incoming Excel files against a strict schema before unlocking business performance, revenue, and customer risk dashboards.

---

# 🚀 Quick Start (Local Setup)

Because we ignore the virtual environment directory (`venv/`) to keep our Git history clean, you will need to spin up your own local environment. It takes less than a minute.

Open your terminal, navigate to the project root, and follow these quick steps:

## 1. Grab the code

```bash
git clone https://github.com/Aulon7/retail-online-streamlit-app.git
cd retail-online-streamlit-app
```

## 2. Create your virtual environment

### On macOS / Linux

```bash
python3 -m venv venv
```

### On Windows

```bash
python -m venv venv
```

## 3. Activate the environment

### On macOS / Linux

```bash
source venv/bin/activate
```

### On Windows (PowerShell)

```powershell
.\venv\Scripts\activate
```

### On Windows (Command Prompt)

```cmd
venv\Scripts\activate.bat
```

> 💡 You will see **`(venv)`** appear at the beginning of your terminal line once it's active.

## 4. Install the packages

Make sure to upgrade **pip** first to avoid package installation conflicts:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Launch the app!

```bash
streamlit run app.py
```
