from flask import Flask,request,jsonify
from flask_pymongo import PyMongo



app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/DatabaseRESTAPI'
mongo = PyMongo(app)


@app.route('/exams', methods=['POST'])
def create_exam():
    name = request.json['name_exam']
    description = request.json['description']
    date = request.json['date']
    time = request.json['time']
    location = request.json['location']

    # Ficar la condició aqui
    if name:
        id = mongo.db.exams.insert(
            {'name':name, 'description':description,'date':date,'time':time,'location':location}
        )
        response = jsonify({
            'name':name,
            'description':description,
            'date':date,
            'time':time,
            'location':location,
            'status_query': 'OK DONE'
        })
        return response
    else:   
        return {"message":"received"}


if __name__ == "__main__":
    app.run(debug=True)