# James Carlson 
# Coding Temple - SE FT-144
# Backend Module 6 Lesson 2 Assignment: Building RESTFul APIs

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

# local import for db_connection
from connect_db import connect_db, Error

app = Flask(__name__)
app.json.sort_keys = False # maintain order set in program
ma = Marshmallow(app)

# homepage
@app.route('/')
def home():
    return "<h1>Welcome to the Fitness Scheduler!</h1>\
<h2>Let's get yoked!</h2><br>\
<img src=\"https://as1.ftcdn.net/v2/jpg/05/53/59/18/1000_F_553591884_dkgQVT2nF94pyW1PkD6rzx5hzIWtt256.jpg\" >"

# ========= MEMBERS SCHEMA and ROUTES ========= #

# define Members schema
class MemberSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    member_name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    membership_type = fields.String(required=True)

    class Meta:
        fields = ("member_id", "member_name", "email", "phone", "membership_type")

# instantiating schema classes
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


# route: get all members
@app.route('/members', methods=['GET'])
def get_members():

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor(dictionary=True)

        # get all members from database
        query = "SELECT * FROM Members"
        cursor.execute(query)
        members = cursor.fetchall()
        return members_schema.jsonify(members)
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: get single member by id
@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor(dictionary=True)

        # get all members from database
        query = "SELECT * FROM Members WHERE member_id = %s"
        cursor.execute(query, (id,))
        member = cursor.fetchone()
        return member_schema.jsonify(member)
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: add new member
@app.route('/members', methods = ['POST'])
def add_member():
    
    # Validate the data follows our structure from the schema
    try:
        member_data = member_schema.load(request.json)

    # handle invalid data
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor() 

        # use new member details and insert new member into database
        new_member = (member_data['member_name'], member_data['email'], member_data['phone'], member_data['membership_type'])
        query = "INSERT INTO Members (member_name, email, phone, membership_type) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, new_member)
        conn.commit()

        # successful addition of the new member
        return jsonify({"Message":"New Member Added Successfully"}), 201
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: update member details
@app.route('/members/<int:id>', methods = ['PUT'])
def update_member(id):
    
    # Validate the data follows our structure from the schema
    try:
        member_data = member_schema.load(request.json)

    # handle invalid data
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor() 

        # update member details
        updated_member = (member_data['member_name'], member_data['email'], member_data['phone'], member_data['membership_type'], id)
        query = "UPDATE Members SET member_name = %s, email = %s, phone = %s, membership_type = %s WHERE member_id = %s"
        cursor.execute(query, updated_member)
        conn.commit()

        # successful update to member
        return jsonify({"Message":"Customer Details Successfully Updated!"}), 200
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: delete member by id
@app.route('/members/<int:id>', methods = ['DELETE'])
def delete_member(id):
    
    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor() 

        # search for member to delete from database
        query = "SELECT * FROM Members WHERE member_id = %s"
        cursor.execute(query, (id,))
        member_found = cursor.fetchone()

        # handle member not found
        if not member_found:
            return jsonify({"Error": "Member ID Not Found"}), 404
        
        # delete member if found
        delete_query = "DELETE FROM Members WHERE member_id = %s"
        cursor.execute(delete_query, (id,))
        conn.commit()

        # successful deletion of the member
        return jsonify({"Message":"Member Removed Successfully"}), 200
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ========= WORKOUT SESSIONS SCHEMA and ROUTES ========= #

# define Sessions schema with only Workout_Sessions table data
class SessionSchema(ma.Schema):
    session_id = fields.Int(dump_only=True)
    member_id = fields.Int(required=True)
    session_date = fields.DateTime(required=True)
    workout_type = fields.String(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "workout_type")

# instantiating session schema classes
session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

# define Workout_Sessions schema using name from Member
class SessionMemberSchema(ma.Schema):
    session_id = fields.Int(dump_only=True)
    member_name = fields.String(required=True)
    session_date = fields.DateTime(required=True)
    workout_type = fields.String(required=True)

    class Meta:
        fields = ("session_id", "member_name", "session_date", "workout_type")

# instantiating session schema classes with member names
session_member_schema = SessionMemberSchema()
sessions_members_schema = SessionMemberSchema(many=True)

# route: view all sessions
@app.route('/sessions', methods=['GET'])
def view_sessions():

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor(dictionary=True)

        # get all workout sessions from database
        query = """
SELECT session_id, member_name, session_date, workout_type
FROM Members, Workout_Sessions
WHERE Members.member_id = Workout_Sessions.member_id"""

        cursor.execute(query)
        sessions = cursor.fetchall()
        return sessions_members_schema.jsonify(sessions)
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: get single session by id
@app.route('/sessions/<int:id>', methods=['GET'])
def view_session(id):

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor(dictionary=True)

        # get all members from database
        query = """
SELECT session_id, member_name, session_date, workout_type
FROM Members, Workout_Sessions
WHERE Members.member_id = Workout_Sessions.member_id AND session_id = %s"""
        cursor.execute(query, (id,))
        member = cursor.fetchone()
        return session_member_schema.jsonify(member)
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: schedule new session
@app.route('/sessions', methods = ['POST'])
def schedule_session():
    
    # Validate the data follows our structure from the schema
    try:
        session_data = session_schema.load(request.json)

    # handle invalid data
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor() 

        # use new session details and insert new session into database
        new_session = (session_data['member_id'], session_data['session_date'], session_data['workout_type'])
        query = "INSERT INTO Workout_Sessions (member_id, session_date, workout_type) VALUES (%s, %s, %s)"
        cursor.execute(query, new_session)
        conn.commit()

        # successful addition of the new session
        return jsonify({"Message":"New Session Scheduled Successfully"}), 201
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: update session details
@app.route('/sessions/<int:id>', methods = ['PUT'])
def update_session(id):
    
    # Validate the data follows our structure from the schema
    try:
        session_data = session_schema.load(request.json)

    # handle invalid data
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor() 

        # update session details
        updated_session = (session_data['member_id'], session_data['session_date'], session_data['workout_type'], id)
        query = "UPDATE Workout_Sessions SET member_id = %s, session_date = %s, workout_type = %s WHERE session_id = %s"
        cursor.execute(query, updated_session)
        conn.commit()

        # successful update of the session
        return jsonify({"Message":"Customer Details Successfully Updated!"}), 200
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# route: delete member by id
@app.route('/sessions/<int:id>', methods = ['DELETE'])
def delete_session(id):
    
    # connect to database
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor() 

        # search for session to delete from database
        query = "SELECT * FROM Workout_Sessions WHERE session_id = %s"
        cursor.execute(query, (id,))
        session_found = cursor.fetchone()

        # handle session not found
        if not session_found:
            return jsonify({"Error": "Session ID Not Found"}), 404
        
        # delete session if found
        delete_query = "DELETE FROM Workout_Sessions WHERE session_id = %s"
        cursor.execute(delete_query, (id,))
        conn.commit()

        # successful deletion of the session
        return jsonify({"Message":"Session Removed Successfully"}), 200
    
    # handle errors
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    # close connection
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)