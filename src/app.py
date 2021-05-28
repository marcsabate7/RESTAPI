from flask import Flask,request,jsonify,Response
from flask_pymongo import PyMongo
from bson import json_util
import json

# Initiating Flask app
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/DatabaseRESTAPI'
mongo = PyMongo(app)



######################################
#                EXAM
######################################


# Listing exams by id or all exams
@app.route('/exams', methods=['GET'])
def listExams():
    try:
        id_exam = request.json['id_exam']
        exams = mongo.db.exams.find({'key_generated':id_exam})           
        response = json_util.dumps(exams) 
    except:
        exams = mongo.db.exams.find()           
        response = json_util.dumps(exams)   

    return Response(response,mimetype='application/json')

# Searching exams by key or partial key 
@app.route('/examsearch', methods=['GET'])
def foundExams():
    try:
        exist_exam = False
        list_exams = ["EXAMS FOUND!"]
        key_search = request.json['key_search']
        query = mongo.db.exams.find()
        for item in query:
            if item['name_exam'].find(key_search) !=-1 or item['description'].find(key_search) != -1:
                list_exams.append(item)
                exist_exam = True
        if exist_exam:
            print(list_exams)  
            all_exams = '\n\n'.join(str(elem) for elem in list_exams)
            return all_exams
        return {"message":"Any exam was found with the KEY introduced!"}
    except:
        return notFound()

# Add exam
@app.route('/exam', methods=['POST'])
def createExam():
    count = 0
    # The unique key generated for the new uploaded exam is the id_exam referenced in all code
    try:
        name_exam = request.json['name_exam']
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

# Modify description
@app.route('/modifydescription', methods=['PUT'])
def modifyDescriptionExam():
    try:
        exam_exists = False
        id_exam = request.json['id_exam']
        description = request.json['description']
        query = mongo.db.exams.find({"key_generated":id_exam})
        for item in query:
            exam_exists = True
        if exam_exists and id_exam!= "" and description != "":
            mongo.db.exams.update_one(
                {"key_generated":id_exam},
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

# Delete exam
@app.route('/deletexam', methods=['DELETE'])
def deleteExam():
    try:
        exam_exists = False
        id_exam = request.json['id_exam']
        query = mongo.db.students.find({"grades":{"$elemMatch":{"id_exam":id_exam}}})
        for item in query:              # Comproving if any student have grades of this id_exam
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


# Create student
@app.route('/student', methods=['POST'])
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

# Add grade to student
@app.route('/addgrade', methods=['PUT'])
def addGradeStudent():
    try:
        exam_exists = False
        grade_iscreated = False
        id_student = request.json['id_student']
        id_exam = request.json['id_exam']
        grade = request.json['grade']
        query = mongo.db.exams.find({"key_generated":id_exam})
        for item in query:
            exam_exists = True
        
        if exam_exists and id_student!= "" and grade!= "":
            query2 = mongo.db.students.find({"key_generated":id_student})
            for item in query2:
                response = json_util.dumps(item) 
                grades = json.loads(response)
                grades = grades['grades']
                for grade in grades:
                    id_exam2 = grade['id_exam']
                    if id_exam == id_exam2:
                        grade_iscreated = True
                        break
            if grade_iscreated:
                return {"message":"This grade is created so you CAN'T add another grade from the same exam, please update it if you want"}
            else:
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

# Modify grades from student
@app.route('/modifygrade', methods=['PUT'])
def modifyGrade():
    try:
        exam_exists = False
        comprovation_exam = False
        all_grades = []
        id_student = request.json['id_student']
        id_exam = request.json['id_exam']
        grade_st = request.json['grade']
        query = mongo.db.exams.find({"key_generated":id_exam})
        for item in query:
            comprovation_exam = True
        if comprovation_exam == True and id_student != "" and id_exam != "" and grade_st != "":
            query2 = mongo.db.students.find({"key_generated":id_student})
            for item in query2:
                response = json_util.dumps(item) 
                grades = json.loads(response)
                grades = grades['grades']
                for grade in grades:
                    id_exam2 = grade['id_exam']
                    if id_exam == id_exam2 and exam_exists == False:
                        grade['grade'] = grade_st
                        exam_exists = True
                    all_grades.append(grade)
                
            if exam_exists:
                mongo.db.students.update_one(
                    {"key_generated":id_student},
                    {"$set": {'grades':all_grades}})
                return {"message":"Grade: " + str(grade_st) + " for ID student: "+ str(id_student) + " and ID exam: " + str(id_exam) + " was updated succesfully!!"}
            else:    
                return {"message":"The id_exam doesn't match with the id_student grades OR the id_student doesn't exist"}
        else:
            return {"message":"Doesn't exist an exam with this ID (create a grade before) or some JSON fields are in blank"}
    
    except:
        return notFound()

# Download grades from a student
@app.route('/downloadgrades', methods=['GET'])
def downloadGrades():
    try:
        item_bo = ""
        user_exists = False
        id_student = request.json['id_student']
        query = mongo.db.students.find({"key_generated":id_student})
        for item in query:
            item_bo = item
            user_exists = True
        if user_exists:
            response = json_util.dumps(item) 
            grades = json.loads(response)
            grades = grades['grades']
            '''for grade in grades:
                print(grade)'''
            grades_final = json_util.dumps(grades)
            if(len(grades) == 0):
                return {"message":"The student doesn't have any grade!"}
            else:
                return grades_final
        else:
            return {"message":"This id_student don't EXIST put a good one!"}
    except:
        return notFound()


# Not Found function called when some parameters fault
@app.errorhandler(404)
def notFound(error=None):
    response = jsonify({
        'message': 'Resource Not Found, you probably miss some data to the JSON (incorrect name of params), requested url: ' + request.url,
        'status': 404,
    })
    response.status_code = 404
    return response



if __name__ == "__main__":
    app.run(debug=True)