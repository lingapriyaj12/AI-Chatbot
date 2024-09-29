from flask import Flask, request, jsonify, render_template
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import spacy

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

user_states = {}

def preprocess_text(text):
    tokens = nltk.word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    return lemmatized_tokens

def identify_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ("BODY", "CONDITION"):
            entities.append((ent.text, ent.label_))
    return entities

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message').lower()
    user_id = request.remote_addr  # Using IP address as user identifier for simplicity

    if user_id not in user_states:
        user_states[user_id] = {'state': 'initial'}

    state = user_states[user_id]['state']

    if state == 'initial':
        if 'student' in user_message:
            response = "Great! As a student, you can visit <a href='https://www.cmch-vellore.edu/Content.aspx?pid=P160802002'>CMC Vellore Student portal</a>. Thank you for visiting CMC!"
        elif 'job seeker' in user_message:
            response = "Excellent! I can assist you with your job search. Here's a link <a href='https://www.cmch-vellore.edu/JobVacancy.aspx?jtype=ALL'>CMC Vellore Jobs & Training</a>. Thank you for visiting CMC!"
        elif 'patient' in user_message:
            response = "Please provide your sex (Male/Female) to proceed."
            user_states[user_id]['state'] = 'sex'
        else:
            response = "I apologize, but I didn't understand your response. Could you please clarify if you are a Student, Job Seeker, or Patient?"
    elif state == 'sex':
        if 'male' in user_message or 'female' in user_message:
            user_states[user_id]['sex'] = user_message
            response = "Thank you! Now, please enter your age:"
            user_states[user_id]['state'] = 'age'
        else:
            response = "I apologize, but I didn't understand your response. Please enter either 'Male' or 'Female' to proceed."
    elif state == 'age':
        try:
            age = int(user_message)
            user_states[user_id]['age'] = age
            response = "Thank you! Please describe your main symptoms (separated by commas):"
            user_states[user_id]['state'] = 'symptoms'
        except ValueError:
            response = "I apologize, but I didn't understand your response. Please enter a valid age."
    elif state == 'symptoms':
        symptoms = user_message
        age = user_states[user_id]['age']
        symptoms_list = preprocess_text(symptoms)

        department_symptoms = {
            "Medicine": ["fever", "cough", "body aches", "nausea", "vomiting", "diarrhea"],
            "Child Health": ["fever", "cough", "earache", "diarrhea", "vomiting", "rash"],
            "Haematology": ["fatigue", "pale skin", "easy bruising", "bleeding", "frequent infections"],
            "Cardiology": ["chest pain", "shortness of breath", "palpitations", "fatigue", "sweating"],
            "ENT": ["earache", "sore throat", "sinus congestion", "runny nose", "loss of voice"],
            "Gastrology": ["Gas and Acidity", "Indigestion", "Hard Stool", "Vomiting", "Belching", "Hiccups", "Bloating", "Flatulence", "Mucoid Stool", "Worm Stool", "Loose Stool", "Frequency Dysentery", "Abdomen pain", "RUQ", "LUQ", "RLQ", "LLQ", "Blood mixed stool", "Constipation"],
            "Oncology": ["Bladder cancer", "Breast cancer", "Colorectal Cancer", "Kidney Cancer", "Lung Cancer Non small cell", "Lymphoma Non Hodgkin", "Melanoma", "Myeloma", "Oral and Oropharyngeal Cancer", "Pancreatic Cancer", "Prostate cancer", "Thyroid Cancer", "Uterine Cancer"],
            "Nephrology": ["Facial puffiness", "Bilateral Pedel edema", "Dryness oral and skin", "Hair fall", "Pallor", "Breathing Difficulty", "Loss of Appetite", "Bad smell"],
            "Neurology": ["Severe head ache", "Recurrent Seizure", "Giddiness", "Unclean Speech", "Memory loss", "Weakness of Right limb", "Weakness of Left Upperlimb", "Weakness of both upper limb and lower limb", "Involuntary movement of upperlimbs and lower limbs", "Imbalance while walking", "Chronic head ache", "Learning Disorder", "Wasting of muscles", "Tremors of upper limb and lower limb"],
            "Urology": ["Cancers in Kidney", "Urinary Bladder", "Testes", "Penis or Prostate", "Other Prostate problems", "Urinary Infection", "Urine Leakage", "Hematuria", "blood in Urine", "Sexual Dysfunction", "Kidney stones", "Urinary TB", "Blockage in Urine Pipes"]
        }

        if age < 16:
            response = "Based on your age, you should visit the Child Health department."
            department_info = "For concerns related to children's health, visit: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=074'>Child Health Department</a>."
            response += " " + department_info
            response += "<br/><br/>If you have to book appointment online, you may visit this webpage <a href='https://clin.cmcvellore.ac.in/webapt/CMC/Login'>CMC Appointment Booking</a>."
            response += "<br/><br/>Thank you for visiting our CMC!"
        else:
            department_scores = {dept: 0 for dept in department_symptoms}

            for symptom in symptoms_list:
                for dept, dept_list in department_symptoms.items():
                    # Check if all words in symptom match any phrase in dept_list
                    if all(word in ' '.join(dept_list) for word in symptom.split()):
                        department_scores[dept] += 1

            best_department = max(department_scores, key=department_scores.get)

            if department_scores[best_department] == 0:
                response = "I'm not sure which department is best suited. Can you describe your symptoms in more detail?"
            else:
                department_info = {
                    "Medicine": "For information on general medical conditions, visit: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=370'>Medicine Department</a>",
                    "Child Health": "For concerns related to children's health, visit: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=074'>Child Health Department</a>",
                    "Haematology": "Visit a hematologist for evaluation. Find one near you: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=017'>Haematology Department</a>",
                    "Cardiology": "Visit a cardiologist for evaluation. Find one near you: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=113'>Cardiology Department</a>",
                    "ENT": "Visit an otolaryngologist (ENT) for evaluation. Find one near you: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=013'>ENT Services</a>",
                    "Gastrology": "Visit an Gastroenterologist for evaluation. Find one near you: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=121'>Gastroenterology Department</a>",
                    "Oncology": "Visit an Oncologist for evaluation. Find one near you:<a href='https://www.cmch-vellore.edu/Departments.aspx?depttype=ALL'>Oncology Department</a>",
                    "Nephrology": "Visit an Nephrologist for evaluation. Find one near you:<a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=102'>Nephrology Department</a>",
                    "Neurology": "Visit an Neurologist for evaluation. Find one near you: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=893'>Neurology Department</a>",
                    "Urology": "Visit an Urologist for evaluation. Find one near you: <a href='https://www.cmch-vellore.edu/DeptContent.aspx?dept=090'>Urology Department</a>"
                }
                response = f"Based on your description, the {best_department} department might be most suited for your needs. {department_info.get(best_department, '')}"
                response += "<br/><br/>If you have to book appointment online, you may visit this webpage <a href='https://clin.cmcvellore.ac.in/webapt/CMC/Login'>CMC Appointment Booking</a>."
                response += "<br/><br/>Thank you for visiting our CMC!"
                
    return jsonify(response=response)

if __name__ == "__main__":
    app.run(debug=True)