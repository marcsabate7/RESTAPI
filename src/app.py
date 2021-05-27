from flask import Flask,request,jsonify,Response
from flask_pymongo import PyMongo
from bson import json_util


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/DatabaseRESTAPI'
mongo = PyMongo(app)



######################################
#                EXAM
######################################


@app.route('/exams', methods=['GET'])
def list_exams():
    exams = mongo.db.exams.find()           
    response = json_util.dumps(exams)   

    return Response(response,mimetype='application/json')

@app.route('/exam', methods=['POST'])
def createExam():
    count = 0
    # The unique key generated for the new uploaded exam is the ID
    try:
        name_exam = request.json['name_exam']
        query = mongo.db.exams.find({"name_exam":name_exam})
        for item in query:
            count+=1
        if count !=0:
            return {"message":"Exam is added to the database so you CAN'T add this exam with the same name"}
        else:
            description = request.json['description']
            date = request.json['date']
            time = request.json['time']
            location = request.json['location']

            total_exams = mongo.db.exams.count()+1
            id = mongo.db.exams.insert(
                {'key_generated': total_exams,'name_exam':name_exam, 'description':description,'date':date,'time':time,'location':location}
            )
        
            response = jsonify({
                'name':name_exam,
                'description':description,
                'date':date,
                'time':time,
                'location':location,
                'key_generated':total_exams,
                'status_query': 'OK DONE'
            })
            return response
    except:   
        return {"message":"You miss some fields to add an exam or some one are incorrect!"}

@app.route('/modifydescription', methods=['POST'])
def modifyDescriptionExam():
    name_exam = request.json['name_exam']
    description = request.json['description']
    if name_exam!= "" and description != "":
        mongo.db.exams.update_one({
            "name":name_exam
        },
        {"$set": {'description':description}})

        #mongo.db.exams.find({"name":name})

        return {"message":"Description modifyed correctly"}

    else:
        return {"message":"YOU MISS SOME FIELDS TO ADD AN EXAM!","parameters":"name_exam and description"}

@app.route('/deletexam', methods=['POST'])
def deleteExam():
    exam_exists = False
    name_exam = request.json['name_exam']
    query = mongo.db.students.find({"grades":{"$elemMatch":{"name_exam":name_exam}}})
    for item in query:
        print(item)
        return {"message":"Can NOT delete this exam because some students have grades in it"}
    
    query2 = mongo.db.exams.find({"name_exam":name_exam})
    for item in query2:
        exam_exists = True
    if exam_exists:
        mongo.db.exams.remove({"name_exam":name_exam})
        return {"message":"Exam has been deleted"}
    else:
        return {"message":"This exam dosn't exist so can't be deleted"}

######################################
#            STUDENTS
######################################

@app.route('/user', methods=['POST'])
def createStudent():
    count = 0
    try:
        name_student = request.json['name_student']
        query = mongo.db.students.find({"name_student":name_student})
        for item in query:
            count+=1
        if count !=0 or name_student== "":
            return {"message":"This student is added to the database / or the name is empty, try another one"}
        else:
            total_students = mongo.db.students.count()+1
            id = mongo.db.students.insert(
                {'key_generated': total_students,'name_student':name_student, 'grades':[]}
            )
        
            response = jsonify({
                'name_student':name_student,
                'status_query': 'OK DONE'
            })
            return response
    except:   
        return {"message":"YOU MISS SOME FIELDS TO ADD AN USER!"}


@app.route('/addgrade', methods=['POST'])
def addGradeStudent():
    exam_exists = False
    name_student = request.json['name_student']
    name_exam = request.json['name_exam']
    grade = request.json['grade']
    query = mongo.db.exams.find({"name_exam":name_exam})
    for item in query:
        exam_exists = True
    
    if exam_exists and name_student!= "" and grade!= "":
        toinsert = {'name_exam':name_exam,'grade':grade}
        mongo.db.students.update(
            {"name_student":name_student}, {'$push': {'grades': toinsert}})

        #mongo.db.exams.find({"name":name})

        return {"message":"Grade added correctly to student "+name_student}

    else:
        return {"message":"Exam doesn't exist or name_student or grade are empty","parameters":"name_student, name_exam, grade"}


@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource Not Found: ' + request.url,
        'status': 404,
    })
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)