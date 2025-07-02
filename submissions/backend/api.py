from flask import Flask, request, jsonify
from flask_cors import CORS
from linkedin_info import extract_linkedin_id, get_linkedin_profile
from agent_search import search_social_media, analyze_profile, extract_useful_profile_info, format_search_query
import os
from dotenv import load_dotenv
import traceback
import json
from chat_edit import edit_message, logger
import logging
import time
import random

# DO NOT import extension.py components directly here to avoid execution on startup
# Instead, we'll use lazy imports when components are needed
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS with explicit origins for all API routes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    app_logger.info("Health check endpoint called")
    return jsonify({'status': 'healthy'})

@app.route('/api/edit-message', methods=['POST'])
def api_edit_message():
    app_logger.info("Edit message endpoint called")
    try:
        app_logger.info(f"Request headers: {request.headers}")
        data = request.get_json()
        app_logger.info(f"Request data: {data}")
        
        if not data:
            app_logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
            
        original_msg = data.get('original_message')
        edit_req = data.get('edit_request')
        
        if not original_msg or not edit_req:
            app_logger.error(f"Missing required fields: original_message={bool(original_msg)}, edit_request={bool(edit_req)}")
            return jsonify({'error': 'Both original_message and edit_request are required'}), 400
            
        app_logger.info("Calling edit_message function")
        edited_message = edit_message(original_msg, edit_req)
        app_logger.info("Successfully got edited message")
        
        response = jsonify({
            'success': True,
            'edited_message': edited_message
        })
        app_logger.info(f"Sending response: {response}")
        return response
        
    except Exception as e:
        app_logger.error(f"Error in edit message: {str(e)}")
        app_logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("Received chat request")
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'invalid_request',
                'message': 'No data provided'
            }), 400
            
        query = data.get('query')
        user_profile = data.get('user_profile')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'missing_query',
                'message': 'Please provide a search query'
            }), 400
            
        try:
            # Format the search query
            formatted_query = format_search_query(query)
            print(f"Formatted query: {formatted_query}")
            
            print(f"Searching for profiles with query: {formatted_query}")
            # Search for profiles
            profiles = search_social_media(formatted_query)
            print(f"Found {len(profiles)} profiles")
            
            if not profiles:
                return jsonify({
                    'success': True,
                    'message': 'No profiles found matching your criteria',
                    'profiles': []
                })
                
            print("Analyzing profiles...")
            # Analyze profiles
            analyzed_profiles = analyze_profile(profiles, query, user_profile)
            print(f"Analysis complete for {len(analyzed_profiles)} profiles")
            
            # Process the analyzed profiles
            processed_profiles = []
            for profile in analyzed_profiles:
                try:
                    # The analysis is already in the correct format
                    processed_profile = {
                        "profile": profile["profile"],
                        "analysis": profile["analysis"]
                    }
                    processed_profiles.append(processed_profile)
                except Exception as e:
                    print(f"Error processing profile: {str(e)}")
                    # Skip this profile if there's an error
                    continue
            
            return jsonify({
                'success': True,
                'message': f'Found {len(processed_profiles)} matching profiles',
                'profiles': processed_profiles
            })
            
        except Exception as e:
            print(f"Error in search/analysis: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': 'search_failed',
                'message': str(e)
            }), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'server_error',
            'message': str(e)
        }), 500

@app.route('/api/process-linkedin', methods=['POST'])
def process_linkedin():
    try:
        data = request.get_json()
        linkedin_url = data.get('linkedin_url')
        
        if not linkedin_url:
            return jsonify({'error': 'LinkedIn URL is required'}), 400
            
        linkedin_id = extract_linkedin_id(linkedin_url)
        if not linkedin_id:
            return jsonify({'error': 'Invalid LinkedIn URL format'}), 400
            
        try:
            # Get profile data
            profile_data = get_linkedin_profile(linkedin_id)
            return jsonify({
                'success': True,
                'profile_data': profile_data
            })
        except Exception as e:
            error_message = str(e)
            if "LinkedIn integration is not available" in error_message:
                return jsonify({
                    'error': 'linkedin_unavailable',
                    'message': 'LinkedIn integration is currently unavailable. Please try again later or contact support.'
                }), 503
            elif "This profile can't be accessed" in error_message:
                return jsonify({
                    'error': 'profile_not_accessible',
                    'message': 'This LinkedIn profile is not accessible. Please make sure the profile is public or you have the correct permissions.'
                }), 403
            else:
                return jsonify({
                    'error': 'linkedin_error',
                    'message': 'There was an error accessing the LinkedIn profile. Please try again later.'
                }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'message': str(e)
        }), 500

@app.route('/api/social-profiles/', methods=['POST'])
def save_social_profile():
    try:
        data = request.get_json()
        name = data.get('name')
        avatar = data.get('avatar')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
            
        # Here you can save the profile data to a database
        # For now, we'll just return a success message
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully',
            'data': {
                'name': name,
                'avatar': avatar
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expand-profile', methods=['POST'])
def expand_profile_endpoint():
    app_logger.info("Expand profile endpoint called")
    print("Expand profile endpoint called")
    
    try:
        data = request.json
        profile_id = data.get('profileId')
        profile_data = data.get('profileData')
        
        if not profile_id or not profile_data:
            app_logger.error("Missing profile ID or data")
            print("Missing profile ID or data")
            return jsonify({"success": False, "error": "Missing profile ID or data"}), 400
        
        app_logger.info(f"Processing expansion request for profile: {profile_id}")
        print(f"Processing expansion request for profile: {profile_id}")
        
        # Lazy import extension components only when needed
        from extension import expand_profile
        
        # Use the expand_profile function directly from extension.py
        start_time = time.time()
        result = expand_profile(profile_id, profile_data)
        elapsed_time = time.time() - start_time
        
        print(f"expand_profile function completed in {elapsed_time:.2f} seconds")
        print(f"Result success: {result.get('success')}")
        print(f"Result nodes count: {len(result.get('nodes', []))}")
        
        return jsonify(result)
        
    except Exception as e:
        app_logger.error(f"Error in expand profile: {str(e)}")
        print(f"Error in expand profile: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e), "nodes": []}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 