from flask import Flask, render_template, request, jsonify, session
import sys
import os
import json
import shutil
from datetime import datetime
import secrets

# Add parent directory to path to import memoryos
# Ensure the path is /root/autodl-tmp for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import memoryos modules directly
from memoryos import Memoryos
from memoryos.utils import get_timestamp

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global memoryos instance (in production, you'd use proper session management)
memory_systems = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init_memory', methods=['POST'])
def init_memory():
    data = request.json
    api_key = data.get('api_key','sk-VJNRYlFE142b1c4191fAT3BLbKFJ7c244329f6824E10A214')
    base_url = data.get('base_url', 'https://cn2us02.opapi.win/v1')
    model = data.get('model', 'gpt-4o-mini')
    user_id = data.get('user_id', 'demo_user')
    
    if not api_key:
        return jsonify({'error': 'OpenAI API key is required'}), 400
    
    try:
        # Initialize memoryos for this session
        data_path = '/root/autodl-tmp/memoryos/memdemo/data'
        os.makedirs(data_path, exist_ok=True)
        
        memory_system = Memoryos(
            user_id=user_id,
            openai_api_key=api_key,
            openai_base_url=base_url,
            data_storage_path=data_path,
            short_term_capacity=7,  # Smaller for demo
            mid_term_capacity=200,   # Smaller for demo
            long_term_knowledge_capacity=100,  # Smaller for demo
            mid_term_heat_threshold=5.0,  # 降低阈值，更容易触发长期记忆更新（原默认值为5.0）
            llm_model=model
        )
        
        session_id = secrets.token_hex(8)
        memory_systems[session_id] = memory_system
        session['memory_session_id'] = session_id
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_id': user_id,
            'model': model,
            'base_url': base_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Get response from memoryos (this already adds the memory internally)
        response = memory_system.get_response(user_input)
        
        # Do NOT add memory again here - it's already done in get_response()
        
        return jsonify({
            'response': response,
            'timestamp': get_timestamp()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory_state', methods=['GET'])
def get_memory_state():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Get short-term memory
        short_term = memory_system.short_term_memory.get_all()
        
        # Get mid-term memory sessions (top 5)
        mid_term_sessions = []
        for sid, session_data in list(memory_system.mid_term_memory.sessions.items())[:5]:
            mid_term_sessions.append({
                'id': sid,
                'summary': session_data.get('summary', ''),
                'keywords': session_data.get('summary_keywords', []),
                'heat': session_data.get('H_segment', 0),
                'visit_count': session_data.get('N_visit', 0),
                'last_visit': session_data.get('last_visit_time', ''),
                'page_count': len(session_data.get('details', []))
            })
        
        # Sort by heat
        mid_term_sessions.sort(key=lambda x: x['heat'], reverse=True)
        
        # Get long-term memory - separate user profile, user knowledge, and assistant knowledge
        user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
        user_knowledge = memory_system.user_long_term_memory.get_user_knowledge()
        assistant_knowledge = memory_system.assistant_long_term_memory.get_assistant_knowledge()
        
        return jsonify({
            'short_term': {
                'capacity': memory_system.short_term_memory.max_capacity,
                'current_count': len(short_term),
                'memories': short_term
            },
            'mid_term': {
                'capacity': memory_system.mid_term_memory.max_capacity,
                'current_count': len(memory_system.mid_term_memory.sessions),
                'sessions': mid_term_sessions,
                'heat_threshold': memory_system.mid_term_heat_threshold
            },
            'long_term': {
                'user_profile': user_profile,
                'user_knowledge': [k.get('knowledge', '') for k in user_knowledge],
                'assistant_knowledge': [k.get('knowledge', '') for k in assistant_knowledge]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger_analysis', methods=['POST'])
def trigger_analysis():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Force mid-term analysis
        memory_system.force_mid_term_analysis()
        return jsonify({'success': True, 'message': 'Analysis triggered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/personality_analysis', methods=['POST'])
def personality_analysis():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Get user profile
        user_profile = memory_system.user_long_term_memory.get_raw_user_profile(memory_system.user_id)
        
        if not user_profile or user_profile.lower() in ['none', 'no profile data yet']:
            return jsonify({'error': 'No user profile available for analysis'}), 400
        
        # Parse personality traits from the user profile
        personality_analysis = parse_personality_traits(user_profile)
        
        return jsonify({
            'success': True,
            'personality_analysis': personality_analysis
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_personality_traits(user_profile):
    """
    Parse personality traits from user profile text.
    Extract traits in format: Dimension ( Level(High/Medium/Low) )
    """
    # Define the three main categories
    categories = {
        'Psychological Model': [
            'Extraversion', 'Openness', 'Agreeableness', 'Conscientiousness', 'Neuroticism',
            'Physiological Needs', 'Need for Security', 'Need for Belonging', 'Need for Self-Esteem',
            'Cognitive Needs', 'Aesthetic Appreciation', 'Self-Actualization', 'Need for Order',
            'Need for Autonomy', 'Need for Power', 'Need for Achievement'
        ],
        'AI Alignment Dimensions': [
            'Helpfulness', 'Honesty', 'Safety', 'Instruction Compliance', 'Truthfulness',
            'Coherence', 'Complexity', 'Conciseness'
        ],
        'Content Platform Interest Tags': [
            'Science Interest', 'Education Interest', 'Psychology Interest', 'Family Concern',
            'Fashion Interest', 'Art Interest', 'Health Concern', 'Financial Management Interest',
            'Sports Interest', 'Food Interest', 'Travel Interest', 'Music Interest',
            'Literature Interest', 'Film Interest', 'Social Media Activity', 'Tech Interest',
            'Environmental Concern', 'History Interest', 'Political Concern', 'Religious Interest',
            'Gaming Interest', 'Animal Concern', 'Emotional Expression', 'Sense of Humor',
            'Information Density', 'Language Style', 'Practicality'
        ]
    }
    
    # Extract traits from user profile
    extracted_traits = {}
    
    import re
    
    # Look for patterns like "Dimension ( Level(High/Medium/Low) )"
    pattern = r'([A-Za-z\s]+)\s*\(\s*([A-Za-z]+)\s*\)'
    matches = re.findall(pattern, user_profile)
    
    for match in matches:
        dimension = match[0].strip()
        level = match[1].strip()
        
        # Find which category this dimension belongs to
        for category, dimensions in categories.items():
            for cat_dimension in dimensions:
                if dimension.lower() in cat_dimension.lower() or cat_dimension.lower() in dimension.lower():
                    if category not in extracted_traits:
                        extracted_traits[category] = []
                    extracted_traits[category].append({
                        'dimension': dimension,
                        'level': level
                    })
                    break
    
    # Alternative pattern: look for lines containing trait descriptions
    lines = user_profile.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for mentions of High/Medium/Low levels
        for level in ['High', 'Medium', 'Low']:
            if level.lower() in line.lower():
                # Try to extract the dimension name
                for category, dimensions in categories.items():
                    for dimension in dimensions:
                        if dimension.lower() in line.lower():
                            if category not in extracted_traits:
                                extracted_traits[category] = []
                            
                            # Check if this trait is already added
                            existing = [t for t in extracted_traits[category] if t['dimension'] == dimension]
                            if not existing:
                                extracted_traits[category].append({
                                    'dimension': dimension,
                                    'level': level
                                })
                            break
    
    return extracted_traits

@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    
    try:
        # Clear all memory files
        user_data_dir = memory_system.user_data_dir
        assistant_data_dir = memory_system.assistant_data_dir
        
        # Remove the entire user data directory
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
        
        # Remove the entire assistant data directory  
        if os.path.exists(assistant_data_dir):
            shutil.rmtree(assistant_data_dir)
        
        # Reinitialize the memory system with the same configuration
        api_key = memory_system.client.api_key
        base_url = memory_system.client.base_url
        model = memory_system.llm_model
        user_id = memory_system.user_id
        data_path = memory_system.data_storage_path
        
        # Create new memory system
        new_memory_system = Memoryos(
            user_id=user_id,
            openai_api_key=api_key,
            openai_base_url=base_url,
            data_storage_path=data_path,
            short_term_capacity=7,
            mid_term_capacity=200,
            long_term_knowledge_capacity=100,
            mid_term_heat_threshold=3.0,
            llm_model=model
        )
        
        # Replace the old memory system
        memory_systems[session_id] = new_memory_system
        
        return jsonify({'success': True, 'message': 'All memories cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/import_conversations', methods=['POST'])
def import_conversations():
    session_id = session.get('memory_session_id')
    if not session_id or session_id not in memory_systems:
        return jsonify({'error': 'Memory system not initialized'}), 400
    
    memory_system = memory_systems[session_id]
    data = request.json
    conversations = data.get('conversations', [])
    
    if not conversations:
        return jsonify({'error': 'No conversations provided'}), 400
    
    try:
        imported_count = 0
        for conv in conversations:
            user_input = conv.get('user_input', '')
            agent_response = conv.get('agent_response', '')
            timestamp = conv.get('timestamp', get_timestamp())
            
            if user_input and agent_response:
                # Add each conversation to memory system
                memory_system.add_memory(
                    user_input=user_input,
                    agent_response=agent_response,
                    timestamp=timestamp
                )
                imported_count += 1
            else:
                print(f"Skipping invalid conversation: {conv}")
        
        return jsonify({
            'success': True,
            'imported_count': imported_count,
            'message': f'Successfully imported {imported_count} conversations'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010) 