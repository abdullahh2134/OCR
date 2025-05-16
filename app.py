from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    doc.close()
    return full_text

def extract_patient_data(full_text):
    patient_data = {}

    patterns = {
        'Age': r"Age\s*:?\s*(\d+)\s*(?:years)?",
        'Gender': r"Gender\s*:?\s*(Male|Female|\w+)",
        'BloodPressure': r"(?:Blood Pressure|BP)\s*(?:\([^)]+\))?\s*:?\s*([\d/]+)",
        'Glucose': r"(?:Blood Glucose Level|Glucose|BGR)\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'Specific Gravity': r"Specific Gravity\s*(?:\([^)]+\))?\s*:?\s*([\d.]+)",
        'Albumin': r"Albumin\s*\(?(?:AL|Albumin)?\)?\s*:?\s*([\d.]+)",
        'Sugar': r"Sugar\s*(?:\([^)]+\))?\s*:?\s*(\d+|\w+)",
        'RBC': r"Red Blood Cells\s*(?:\([^)]+\))?\s*:?\s*(\w+)",
        'Pus Cells': r"Pus Cells\s*(?:\([^)]+\))?\s*:?\s*(\w+)",
        'Pus Cell Clumps': r"Pus Cell Clumps\s*(?:\([^)]+\))?\s*:?\s*(\w+)",
        'Bacteria': r"(?:Bacteria|Bacterial Infection)\s*(?:\([^)]+\))?\s*:?\s*(\w+)",
        'Blood Urea': r"Blood Urea\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'Serum Creatinine': r"Serum Creatinine\s*(?:\([^)]+\))?\s*:?\s*([\d.]+)",
        'Sodium': r"Sodium\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'Potassium': r"Potassium\s*(?:\([^)]+\))?\s*:?\s*([\d.]+)",
        'Hemoglobin': r"Hemoglobin\s*(?:\([^)]+\))?\s*:?\s*([\d.]+)",
        'Hematocrit': r"Hematocrit\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'WBC Count': r"(?:White Blood Cell Count|WBC Count)\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'RBC Count': r"(?:Red Cell Count|Red Blood Cell Count)\s*(?:\([^)]+\))?\s*:?\s*([\d.]+)",
        'Hypertension': r"Hypertension\s*(?:\([^)]+\))?\s*:?\s*(Yes|No|\w+)",
        'Diabetes Mellitus': r"(?:Diabetes|Diabetes Mellitus|DM)\s*(?:\([^)]+\))?\s*:?\s*(Yes|No|\w+)",
        'Coronary Artery Disease': r"Coronary Artery Disease\s*(?:\([^)]+\))?\s*:?\s*(Yes|No|\w+)",
        'Appetite': r"Appetite\s*:?\s*(Good|Poor|\w+)",
        'Pedal Edema': r"Pedal Edema\s*(?:\([^)]+\))?\s*:?\s*(Yes|No|\w+)",
        'Anemia': r"Anemia\s*(?:\([^)]+\))?\s*:?\s*(Yes|No|\w+)",
        'Total Bilirubin': r"Total Bilirubin\s*:?\s*([\d.]+)",
        'Direct Bilirubin': r"Direct Bilirubin\s*:?\s*([\d.]+)",
        'Alkaline Phosphotase': r"Alkaline Phosphotase\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'Sgpt': r"Sgpt\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'Sgot': r"Sgot\s*(?:\([^)]+\))?\s*:?\s*(\d+)",
        'Total Proteins': r"Total Proteins\s*:?\s*([\d.]+)",
        'Albumin_G': r"Albumin\s*\(?ALB\)?\s*:?\s*([\d.]+)",
        'A/G Ratio': r"A/G Ratio\s*:?\s*([\d.]+)",
        'Pregnancies': r"Pregnancies\s*:?\s*(\d+)",
        'SkinThickness': r"Skin Thickness\s*:?\s*(\d+)",
        'Insulin': r"Insulin\s*:?\s*(\d+)",
        'BMI': r"(?:Body Mass Index|BMI)\s*:?\s*([\d.]+)",
        'DiabetesPedigreeFunction': r"Diabetes Pedigree Function\s*:?\s*([\d.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text, re.IGNORECASE)
        patient_data[key] = match.group(1) if match else "Not mentioned"

    return patient_data

@app.route('/extract', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            extracted_text = extract_text_from_pdf(filepath)
            patient_data = extract_patient_data(extracted_text)
            
            # Clean up - remove the uploaded file after processing
            os.remove(filepath)
            
            return jsonify({
                'status': 'success',
                'data': patient_data
            })
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Allowed file type is PDF only'}), 400

@app.route('/')
def home():
    return "Patient Data Extraction API - Send a POST request to /extract with a PDF file"

if __name__ == '__main__':
    app.run(debug=True)
