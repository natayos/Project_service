import mysql.connector
from flask import Blueprint, redirect, request, jsonify
import requests
import os
import mysql
from functools import wraps
from .author import token_Author
controller = Blueprint('controller', __name__)

db = mysql.connector.connect(
    host="project-service.ctyetg9uawza.ap-southeast-2.rds.amazonaws.com", user="root", password="ikfIjN-23412ddasd+3d", db="project_service"
)

@controller.route('/', methods=['GET'], endpoint="index")
# @token_Author
def index(): return "TEST"


@controller.route('/projects', methods=['GET'], endpoint="get_projects")
@token_Author
def get_projects(data):
    """__GetAll projects in database__
        return ArrayList of Project's data 
    """
    db.connect();
    cursor = db.cursor(dictionary=True)
    try:
        sql = "SELECT * from Project_info WHERE isActive = 'YES';"
        cursor.execute(sql)
        reply = cursor.fetchall()  # Get data from db => [{}....]
        return reply, 200
    except Exception as error:
        return jsonify(error), 400
    finally:
        cursor.close()
        db.close()


@controller.route('/create/project', methods=['POST'], endpoint="create_project")
@token_Author
def create_project(data):
    db.connect()
    cursor = db.cursor(dictionary=True)
    db.start_transaction()
    try:
        req = request.json
        # print("JSON: ",req)
        project_info = req['project_info']
        print("\nProject :", project_info, "\n")
        members = req['member']
        if (project_info is None):
            return {
                "status": False,
                "message": "Create project fail! project's infomation is None!"
            }, 400
        if (members is None or not members):
            return {
                "status": False,
                "message": "Create project fail! your project's members < 1 !"
            }, 400
        sql_create_project = "INSERT INTO Project_info(project_name, project_chief, due_date_project) VALUES({0}, {1}, {2})".format(
            "'"+project_info['project_name']+"'",
            "'"+project_info['project_chief']+"'",
            "'"+project_info['due_date_project']+"'"
        )
        cursor.execute(sql_create_project)
        current_project_id = cursor.lastrowid
        print("\n PROJECTID: => ", current_project_id, "\n")

        index = 0
        for id in members:
            print(index, id)
            cursor.execute(
                "INSERT INTO Members(emp_id, project_id) VALUES({0}, {1})".format(
                    "'"+id+"'",
                    current_project_id
                )
            )
            index += 1
        db.commit()
        return {
            "status": True,
            'message': "Successfuly create Project "+project_info['project_name']+"."
        }, 200

    except Exception as error:
        print(error)
        db.rollback()
        return {
            "status": False,
            "message": "Create new Project fail!",
            "error": jsonify(error)
        }, 409

    finally:
        cursor.close()
        db.close()


@controller.route("/add/member", methods=['POST'], endpoint="add_member")
@token_Author
def add_member(data):
    db.connect()
    cursor = db.cursor(dictionary=True)
    db.start_transaction()
    try:
        req = request.json
        project_id = req['project_id']
        member = req['member']
        index = 0
        for item in member:
            cursor.execute(
                "INSERT INTO Members(emp_id, project_id) VALUES({0}, {1})".format(
                    "'" + item['emp_id'] + "'",
                    project_id
                )
            )
            index += 1
        db.commit()
        return {
            "status": True,
            "message": "Add member to project_id = "+project_id
        }, 200

    except Exception as error:
        print(error)
        db.rollback()
        return {
            "status": False,
            "message": "Add member fail!",
            "error": jsonify(error)
        }, 409
    finally:
        cursor.close()
        db.close()


@controller.route('/edit/project', methods=["PUT"], endpoint="edit_project")
@token_Author
def edit_project(data):
    db.connect()
    cursor = db.cursor(dictionary=True)
    # db.start_transaction();
    try:
        req = request.form.to_dict()
        sql = "UPDATE Project_info set project_name = {0}, project_chief = {1}, project_status = {2}, due_date_project ={3} WHERE project_id = {4}".format(
            req['project_name'],
            req['project_chief'],
            req['project_status'],
            req['due_date_project'],
            req['project_id']
        )
        cursor.execute(sql)
        return {
            "status": True,
            "message": "Update Project succesfuly!"
        }, 200
    except Exception as error:
        print(error)
        return {
            "status": False,
            "message": "Edit project fail!",
            "error": jsonify(error)
        }, 409
    finally:
        cursor.close()
        db.close()


@controller.route('/stop/project/<project_id>', methods=['PUT'], endpoint="stopActive_project")
@token_Author
def stopActive_project(data, project_id: int):
    """"""
    db.connect()
    cursor = db.cursor(dictionary=True)
    try:
        sql = "UPDATE Project_info set isActive ='NO' where project_id = {0}".format(
            project_id)
        cursor.execute(sql)
        return {
            "status": True,
            "message": "Project_id => {0} update isActive to 'NO' !".format(project_id)
        }, 200
    except Exception as error:
        print(error)
        return {
            "status": False,
            "message": "Project_id => {0} update fail !".format(project_id),
            "error": jsonify(error)
        }, 409
    finally:
        cursor.close()
        db.close()


@controller.route('/delete/member/<project_id>/<emp_id>', methods=['DELETE'], endpoint="delete_project")
@token_Author
def delete_project(data, project_id: int, emp_id: str):
    """"""
    db.connect()
    cursor = db.cursor(dictionary=True)
    print(project_id, emp_id)
    try:
        sql = "DELETE Members where emp_id = {0} and project_id = {1}".format(
            "'"+emp_id+"'",
            project_id
        )
        cursor.execute(sql)
        return {
            "status": True,
            "message": "Delete emp_id = {0} from project_id = {1} Successfuly !".format(emp_id, project_id)
        }, 200
    except Exception as error:
        print(error)
        return {
            "status": True,
            "message": "Delete emp_id = {0} from project_id = {1} fail!".format(emp_id, project_id),
            "error": jsonify(error)
        }, 409
    finally:
        cursor.close()
        db.close()

@controller.route('/getAll/member/<project_id>', methods=['GET'], endpoint="get_all_member")
def get_all_member(project_id: int):
    """"""
    db.connect();
    cursor = db.cursor(dictionary=True);
    try:
        sql_fetch_member = "SELECT emp_id FROM Members WHERE project_id = {0}".format(project_id);
        cursor.execute(sql_fetch_member);
        member = cursor.fetchall();
        # print("MEMBER in PROJECT => ",member, "\n");
        all_user = requests.get('http://localhost:8080/user/getAllUser').json();
        
        reply = [];
        for item in member:
            for user in all_user:
                if (user['_id'] == item['emp_id']):
                    obj = {
                        "emp_id": user['_id'],
                        "firstName": user['fname'],
                        "last_name": user['lname']
                    }
                    reply.append(obj);
        return reply, 200;
        
    except Exception as error:
        print(error);
        return {
            "error": error
        }
    finally:
        cursor.close();
        db.close();
    
