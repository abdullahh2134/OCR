from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import re

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def preprocess_text(text):
    # Replace underscores with spaces, remove multiple spaces, strip units like 'mg/dL', 'g/dL', 'U/L'
    text = text.replace("_", " ")
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\s*(mg/dL|g/dL|U/L|years)\b', '', text, flags=re.IGNORECASE)
    return text


def extract_patient_data(full_text):
    patient_data = {}
    patterns = {
        'Age': r"Age:\s*(\d+)",
        'Gender': r"Gender:\s*(Male|Female|\w+)",
        'BloodPressure': r"Blood Pressure \(BP\):\s*([\d/]+)",
        'Glucose': r"Blood Glucose Level \(BGR\):\s*(\d+)",
        'Specific_Gravity': r"Specific Gravity \(SG\):\s*([\d.]+)",
        'Albumin': r"Albumin \(AL\):\s*([\d.]+)",
        'Sugar': r"Sugar \(SU\):\s*(\d+|\w+)",
        'RBC': r"Red Blood Cells \(RBC\):\s*(\w+)",
        'Pus_Cells': r"Pus Cells \(PC\):\s*(\w+)",
        'Pus_Cell_Clumps': r"Pus Cell Clumps \(PCC\):\s*(\w+)",
        'Bacteria': r"Bacteria \(BA\):\s*(\w+)",
        'Blood_Urea': r"Blood Urea \(BU\):\s*(\d+)",
        'Serum_Creatinine': r"Serum Creatinine \(SC\):\s*([\d.]+)",
        'Sodium': r"Sodium \(SOD\):\s*(\d+)",
        'Potassium': r"Potassium \(POT\):\s*([\d.]+)",
        'Hemoglobin': r"Hemoglobin \(HEMO\):\s*([\d.]+)",
        'Hematocrit': r"Hematocrit \(PCV\):\s*(\d+)",
        'WBC_Count': r"White Blood Cell Count \(WC\):\s*(\d+)",
        'RBC_Count': r"Red Blood Cell Count \(RC\):\s*([\d.]+)",
        'Hypertension': r"Hypertension \(HTN\):\s*(Yes|No|\w+)",
        'Diabetes_Mellitus': r"Diabetes \(DM\):\s*(Yes|No|\w+)",
        'Coronary_Artery_Disease': r"Coronary Artery Disease \(CAD\):\s*(Yes|No|\w+)",
        'Appetite': r"Appetite:\s*(Good|Poor|\w+)",
        'Pedal_Edema': r"Pedal Edema \(PE\):\s*(Yes|No|\w+)",
        'Anemia': r"Anemia \(ANE\):\s*(Yes|No|\w+)",
         'Total_Bilirubin': r"Total Bilirubin:\s*([\d.]+)",
        'Direct_Bilirubin': r"Direct Bilirubin:\s*([\d.]+)",
        'Alkaline_Phosphatase': r"Alkaline Phosphatase:\s*(\d+)",
        'Alanine_Aminotransferase': r"Alanine Aminotransferase:\s*(\d+)",
        'Aspartate_Aminotransferase': r"Aspartate Aminotransferase:\s*(\d+)",
        'Total_Proteins': r"Total Proteins:\s*([\d.]+)",
        'Albumin': r"Albumin:\s*([\d.]+)",
        'A_G_Ratio': r"A/G Ratio:\s*([\d.]+)",
        'Pregnancies': r"Pregnancies:\s*(\d+)",
        'SkinThickness': r"Skin Thickness:\s*(\d+)",
        'Insulin': r"Insulin:\s*(\d+)",
        'BMI': r"BMI:\s*([\d.]+)",
        'DiabetesPedigreeFunction': r"Diabetes Pedigree Function:\s*([\d.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text)
        patient_data[key] = match.group(1) if match else "Not mentioned"

    
    alias_map = {
        'Albumin': 'Albumin',
        'A_G_Ratio': 'A/G Ratio',
        'Direct_Bilirubin': 'Direct Bilirubin',
        'Gender': 'Gender of the patient',
        'Age': 'Age of the patient',
        'Alanine_Aminotransferase': 'Sgot',
        'Aspartate_Aminotransferase': 'Aspartate Aminotransferase'
    }

    for original, alias in alias_map.items():
        if original in patient_data:
            patient_data[alias] = patient_data[original]
    return patient_data

@app.route("/extract", methods=["POST"])
def extract():
    if 'file' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400
    pdf_file = request.files['file']
    text = extract_text_from_pdf(pdf_file)
    data = extract_patient_data(text)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
