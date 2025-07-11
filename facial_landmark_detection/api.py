from flask import Flask, jsonify
from database import Session, Landmark

app = Flask(__name__)

@app.route('/landmarks/<face_id>', methods=['GET'])
def get_landmarks(face_id):
    session = Session()
    landmarks = session.query(Landmark).filter_by(face_id=face_id).all()
    return jsonify([
        {"x": lm.x, "y": lm.y} for lm in landmarks
    ])

if __name__ == '__main__':
    app.run(debug=True)
