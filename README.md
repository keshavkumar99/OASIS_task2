# Advanced BMI Calculator

A desktop BMI calculator built with Python, Tkinter, SQLite, and Matplotlib.

## Features
- BMI calculation from height in centimetres and weight in kilograms
- Adult BMI category display for ages 20+
- Special caution for users under 20: adult categories are not applied
- SQLite record storage
- BMI history table
- Matplotlib trend chart
- Delete selected records and reset fields

## Requirements
- Python 3.10+
- Internet is not required after dependencies are installed

## Windows setup (VS Code)
1. Extract the ZIP and open the folder in VS Code.
2. Open Terminal and run:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Run the application:

   ```powershell
   python main.py
   ```

Tkinter is included with most standard Windows Python installations. If `import tkinter` fails, rerun the Python installer and enable Tcl/Tk support.

## Database
The app creates `bmi_history.db` automatically in the project folder. It stores name, age, height, weight, BMI, category, and timestamp. Keep this file private because it contains personal data.

## BMI note
BMI = weight (kg) / height (m)^2. The commonly used adult categories are intended for adults aged 20 and above. Children and teens need age- and sex-specific BMI percentile interpretation. BMI is a screening measure, not a diagnosis.
