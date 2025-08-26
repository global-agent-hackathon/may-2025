from flask import render_template, session
from app.main import bp
import uuid

@bp.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = uuid.uuid4().hex
    if 'user_id' not in session: 
        session['user_id'] = session['session_id'] 
    return render_template('index.html') 
