import os, json;
import pyrebase;
import jwt;
from flask import jsonify, request, abort;
from functools import wraps;
import mysql;
from jwt.algorithms import get_default_algorithms;
from flask import current_app;
get_default_algorithms();


secret = "foesoifbhfiobflbfoifhiefifesifhbelfkjsifhesfseobf";

def token_Author(function):
    wraps(function);
    print("Verify Token");
    def verify_Token(*args, **kwargs):
        token = None;
        if "Authorization" in request.headers:
            token = request.headers["Authorization"];
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401;
        # print(token)
        try:
            data = jwt.decode(token, secret,algorithms=["HS384"]);
            # print("Token",data);
            if data['userId'] is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401;
            
        except jwt.ExpiredSignatureError as timeout:
            print("Token time out")
            return jsonify(timeout),401
        except Exception as error:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(error)
            }, 500;
        return function(data, *args, **kwargs);
    return verify_Token;
