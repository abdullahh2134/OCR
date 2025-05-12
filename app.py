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

def extract_patient_data(full_text):
    patient_data = {}
    patterns = {
        'Age': r"Age:\s*(\d+)",
        'Gender': r"Gender:\s*(Male|Female|\w+)",
        'BloodPressure': r"Blood Pressure \(BP\):\s*([\d/]+)",
        'Glucose': r"Blood Glucose Level \(BGR\):\s*(\d+)",
        'Specific Gravity': r"Specific Gravity \(SG\):\s*([\d.]+)",
        'Albumin': r"Albumin \(AL\):\s*([\d.]+)",
        'Sugar': r"Sugar \(SU\):\s*(\d+|\w+)",
        'RBC': r"Red Blood Cells \(RBC\):\s*(\w+)",
        'Pus Cells': r"Pus Cells \(PC\):\s*(\w+)",
        'Pus Cell Clumps': r"Pus Cell Clumps \(PCC\):\s*(\w+)",
        'Bacteria': r"Bacteria \(BA\):\s*(\w+)",
        'Blood Urea': r"Blood Urea \(BU\):\s*(\d+)",
        'Serum Creatinine': r"Serum Creatinine \(SC\):\s*([\d.]+)",
        'Sodium': r"Sodium \(SOD\):\s*(\d+)",
        'Potassium': r"Potassium \(POT\):\s*([\d.]+)",
        'Hemoglobin': r"Hemoglobin \(HEMO\):\s*([\d.]+)",
        'Hematocrit': r"Hematocrit \(PCV\):\s*(\d+)",
        'WBC Count': r"White Blood Cell Count \(WC\):\s*(\d+)",
        'RBC Count': r"Red Blood Cell Count \(RC\):\s*([\d.]+)",
        'Hypertension': r"Hypertension \(HTN\):\s*(Yes|No|\w+)",
        'Diabetes Mellitus': r"Diabetes \(DM\):\s*(Yes|No|\w+)",
        'Coronary Artery Disease': r"Coronary Artery Disease \(CAD\):\s*(Yes|No|\w+)",
        'Appetite': r"Appetite:\s*(Good|Poor|\w+)",
        'Pedal Edema': r"Pedal Edema \(PE\):\s*(Yes|No|\w+)",
        'Anemia': r"Anemia \(ANE\):\s*(Yes|No|\w+)",
        'Total Bilirubin': r"Total Bilirubin:\s*([\d.]+)",
        'Direct Bilirubin': r"Direct Bilirubin:\s*([\d.]+)",
        'Alkaline Phosphotase': r"Alkaline Phosphotase \(Alkphos\):\s*(\d+)",
        'Sgpt': r"Sgpt \(Alamine Aminotransferase\):\s*(\d+)",
        'Sgot': r"Sgot \(Aspartate Aminotransferase\):\s*(\d+)",
        'Total Proteins': r"Total Proteins:\s*([\d.]+)",
        'Albumin_G': r"Albumin \(ALB\):\s*([\d.]+)",
        'A/G Ratio': r"A/G Ratio:\s*([\d.]+)",
        'Pregnancies': r"Pregnancies:\s*(\d+)",
        'SkinThickness': r"Skin Thickness:\s*(\d+)",
        'Insulin': r"Insulin:\s*(\d+)",
        'BMI': r"BMI:\s*([\d.]+)",
        'DiabetesPedigreeFunction': r"Diabetes Pedigree Function:\s*([\d.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text)
        patient_data[key] = match.group(1) if match else "Not mentioned"
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
