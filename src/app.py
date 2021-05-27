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
    # The unique key generated for the new uploaded exam is the id_exam referenced in all code
    try:
        name_exam = request.json['name_exam']
        query = mongo.db.exams.find({"name_exam":name_exam})
        for item in query:
            count+=1
        if count !=0:
            return {"message":"This exam is already added to the database, try another name"}
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
        return notFound()

@app.route('/modifydescription', methods=['POST'])
def modifyDescriptionExam():
    try:
        exam_exists = False
        id_exam = request.json['id_exam']
        description = request.json['description']
        query = mongo.db.exams.find({"key_generated":id_exam})
        for item in query:
            exam_exists = True
        if exam_exists and id_exam!= "" and description != "":
            mongo.db.exams.update_one({
                "key_generated":id_exam
            },
            {"$set": {'description':description}})

            return {"message":"Description modifyed correctly for exam with ID: "+str(id_exam)}

        else:
            response = jsonify({
                "message":"Exam doesn't exist so we CAN'T modify the description",
                "parameters":"id_exam, description"
            })
            response.status_code = 404
            return response
    except:
        return notFound()

@app.route('/deletexam', methods=['POST'])
def deleteExam():
    try:
        exam_exists = False
        id_exam = request.json['id_exam']
        query = mongo.db.students.find({"grades":{"$elemMatch":{"id_exam":id_exam}}})
        for item in query:
            print(item)
            return {"message":"CAN'T delete this exam because some students have grades in it"}
        
        query2 = mongo.db.exams.find({"key_generated":id_exam})
        for item in query2:
            exam_exists = True
        if exam_exists:
            mongo.db.exams.remove({"key_generated":id_exam})
            return {"message":"Exam has been deleted"}
        else:
            return {"message":"This exam dosn't exist so can't be deleted"}
    except:
        return notFound()

######################################
#            STUDENTS
######################################

@app.route('/user', methods=['POST'])
def createStudent():
    count = 0
    try:
        name_student = request.json['name_student']
        if name_student== "":
            return {"message":"The name of the student is empty, add name"}
        else:
            total_students = mongo.db.students.count()+1
            id = mongo.db.students.insert(
                {'key_generated': total_students,'name_student':name_student, 'grades':[]}
            )
        
            response = jsonify({
                'name_student':name_student,
                'key_generated': total_students,
                'status_query': 'OK DONE'
            })
            response.status_code = 200
            return response
    except:   
        return notFound()


@app.route('/addgrade', methods=['POST'])
def addGradeStudent():
    try:
        exam_exists = False
        id_student = request.json['id_student']
        id_exam = request.json['id_exam']
        grade = request.json['grade']
        query = mongo.db.exams.find({"key_generated":id_exam})
        for item in query:
            exam_exists = True
        
        if exam_exists and id_student!= "" and grade!= "":
            toinsert = {'id_exam':id_exam,'grade':grade}
            mongo.db.students.update(
                {"key_generated":id_student}, {'$push': {'grades': toinsert}})

            return {"message":"Grade: " + str(grade) + " added correctly to student ID: "+ str(id_student) +", for exam ID: " +str(id_exam)}

        else:
            response = jsonify({
                "message":"Exam doesn't exist or id_student or grade are empty",
                "parameters":"id_student, id_exam, grade"
            })
            response.status_code = 404
            return response
    except:
        return notFound()


@app.errorhandler(404)
def notFound(error=None):
    response = jsonify({
        'message': 'Resource Not Found, you miss some data to the JSON, requested url: ' + request.url,
        'status': 404,
    })
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)