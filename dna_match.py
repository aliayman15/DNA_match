from flask import Flask, request, jsonify
from Bio import pairwise2
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('sa3edny-b7978-firebase-adminsdk-yt5ha-8a3a7205e5.json')  # Replace with the path to your service account key file
initialize_app(cred)
db = firestore.client()

@app.route('/align', methods=['POST'])
def align_sequences():
    data = request.get_json()
    child_dna = data.get('child_dna')

    if not child_dna:
        return jsonify({'error': 'Child DNA data must be provided'}), 400

    # Query all documents in the 'dna_case' collection
    dna_cases_ref = db.collection('dna_case')
    dna_cases = dna_cases_ref.stream()

    results = []

    for doc in dna_cases:
        doc_data = doc.to_dict()
        parent_dna = doc_data.get('patient_sequence')

        if not parent_dna:
            continue  # Skip cases where 'patient_sequence' is not present

        # Perform pairwise alignment
        alignments = pairwise2.align.globalxx(child_dna, parent_dna)

        # Check if any alignment meets your criteria (e.g., score >= threshold)
        threshold = 5  # Adjust this threshold as per your requirement
        for alignment in alignments:
            score = alignment.score
            if score >= threshold:
                results.append({
                    'match': True,
                    'case_id': doc.id,
                    'score': score,
                    'child_dna': child_dna,
                    'parent_dna': parent_dna
                })
                break  # Exit the loop if a match is found

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)



