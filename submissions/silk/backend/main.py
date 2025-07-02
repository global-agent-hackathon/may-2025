import logging
import os
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, Namespace, emit
import uuid
import time
from core.models import CourseOutline, CourseAuthenticator
from core.prompts import SYSTEM_PROMPT_CONTENT, SYSTEM_PROMPT_OUTLINE
from core.database.db import Database
from flask_cors import CORS
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

db = Database()

@app.route('/')
def home():
    db.health_check()
    return {"message": "Hello from Flask!"}

@app.route('/course', methods=["GET", "DELETE"])
def course_handler():
    course_id = request.args.get('id')
    if not course_id:
        return jsonify({"error": "Missing 'id' query parameter"}), 400

    if request.method == "GET":
        course = db.get_course(course_id)
        if course:
            return jsonify(course)
        else:
            return jsonify({"error": "Course not found"}), 404

    elif request.method == "DELETE":
        deleted = db.delete_course(course_id)
        if deleted:
            return jsonify({"message": f"Course with id {course_id} deleted successfully."}), 200
        else:
            return jsonify({"error": "Course not found"}), 404

@app.route('/courses')
def get_all_courses():
    courses = db.get_all_courses()
    return jsonify(courses)

@app.route('/sections')
def get_sections():
    course_id = request.args.get('course_id')
    if not course_id:
        return jsonify({"error": "Missing 'course_id' query parameter"}), 400

    sections = db.get_all_sections_for_course(course_id)
    return jsonify(sections)

@app.route('/section/complete', methods=['POST'])
def complete_section():
    try:
        data = request.get_json()
        section_id = data.get('section_id')

        if not section_id:
            return jsonify({"error": "Missing 'section_id' in request body"}), 400

        db.complete_section(section_id)
        return jsonify({"status": "success", "message": f"Section {section_id} marked as complete"}), 200

    except Exception as e:
        logger.exception(f"Failed to complete section {section_id}.")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analytics')
def get_analytics():
    try:
        analytics_data = db.get_analytics_data()
        return jsonify(analytics_data), 200
    except Exception as e:
        logger.exception("Failed to retrieve analytics data.")
        return jsonify({"error": "Failed to retrieve analytics data", "details": str(e)}), 500


outline_agent = Agent(
    model=Gemini(id=os.getenv("GEMINI_MODEL"), api_key=os.getenv("GEMINI_API_KEY")),
    description=SYSTEM_PROMPT_OUTLINE,
    introduction=SYSTEM_PROMPT_OUTLINE,
    structured_outputs=True,
    use_json_mode=True,
    response_model= CourseOutline
)

course_validator = Agent(
    model=Gemini(id=os.getenv("GEMINI_MODEL"), api_key=os.getenv("GEMINI_API_KEY")),
    description="You are a course validator. Your task is to determine if the given course request is valid or a random chat message. Respond with 'true' if it is a valid course request and 'false' if it is not.",
    instructions="Please respond with 'true' or 'false'. Send true if the given text is a valid request for making a course or description of a course and false if it is not.",
    structured_outputs=True,
    use_json_mode=True,
    response_model= CourseAuthenticator
)

section_agent = Agent(
    model=Gemini(id=os.getenv("GEMINI_MODEL"), api_key=os.getenv("GEMINI_API_KEY")),
    description=SYSTEM_PROMPT_CONTENT,
    introduction=SYSTEM_PROMPT_CONTENT
)
class CreateNamespace(Namespace):
    def emit_session_update(self, session_id, course_id = None):
        session = db.get_session(session_id)
        self.emit('session_update', {**session, "course_id": course_id}, namespace='/create')

    def emit_error(self, session_id, error_message):
        self.emit('error', {"session_id": session_id, "error": error_message}, namespace='/create')

    def on_connect(self):
        print("Client connected to /create")

    def on_disconnect(self):
        print("Client disconnected from /create")

    def on_start_creation(self, data):
        session_id = data.get('session_id') or str(uuid.uuid4())
        description = data.get('description', '')
        level = data.get('level', '')

        validator_response = course_validator.run(description)
        course_validation: CourseAuthenticator = validator_response.content
        if not course_validation.is_valid_course_request:
            error_message = "Invalid course description. Please provide a valid course request."
            self.emit_error(session_id, error_message)
            return
        actions = []
        course_id = str(uuid.uuid4())

        db.create_session(session_id, actions, description, level, 'in_progress')
        self.emit_session_update(session_id)

        actions.append("Creating course details")
        db.update_session_progress(session_id, 'in_progress')
        db.update_session_actions(session_id, actions)

        self.emit_session_update(session_id)

        response = outline_agent.run(f"Course Description: {description} \n\n Level: {level}")
        course_outline: CourseOutline = response.content

        created_at = int(time.time())
        db.create_course(course_id, session_id, course_outline.course_title, course_outline.course_description, level, created_at)
        actions.append(f"Course outline created")
        db.update_session_actions(session_id, actions)
        self.emit_session_update(session_id, course_id)
        for i, section in enumerate(course_outline.sections):
            actions.append(f"Creating section: {section.section_title}")
            db.update_session_actions(session_id, actions)
            self.emit_session_update(session_id, course_id)

            section_response = section_agent.run(section.section_description)
            section_content = section_response.content
            section_id = str(uuid.uuid4())
            db.create_section(
                section_id=section_id,
                course_id=course_id,
                title=section.section_title,
                description=section.section_description,
                content=section_content,
                section_order=i,
                created_at=created_at
            )

            db.update_session_actions(session_id, actions)
            self.emit_session_update(session_id, course_id)

        actions.append("Course creation completed!")
        db.update_session_progress(session_id, 'success')
        db.update_session_actions(session_id, actions)

        self.emit_session_update(session_id, course_id)

socketio.on_namespace(CreateNamespace('/create'))

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000)
