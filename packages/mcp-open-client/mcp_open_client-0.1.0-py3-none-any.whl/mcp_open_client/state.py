# Global state management for the application

import json
import os

# API instance (will be initialized in main.py)
api = None

# State of the application
app_state = {
    'initialized': False,
    'current_page': 'chat',
    'messages': [],
    'conversations': [],
    'current_conversation_id': None,
    'settings': {
        'temperature': 0.7,
        'max_tokens': 2000,
        'model': 'claude-3-7-sonnet',
        'base_url': 'http://192.168.58.101:8123/v1',
        'api_key': 'not-needed',
        'dark_mode': False,
        'system_prompt': 'You are a helpful AI assistant.'
    },
    'tools': [],  # List to store custom tools
    'page_renderers': {}
}

# UI references (will be set in main.py)
content_container = None
chat_container = None
chat_input = None

def update_setting(key, value):
    """Actualiza una configuración"""
    app_state['settings'][key] = value
    from nicegui import ui
    ui.notify(f"Configuración actualizada: {key} = {value}")

def select_conversation(conv_id):
    """Selecciona una conversación"""
    app_state['current_conversation_id'] = conv_id
    from nicegui import ui
    ui.notify(f"Conversación seleccionada")
    save_conversations_to_storage()
    
    # Trigger UI update to show the selected conversation
    from mcp_open_client.ui.common import render_content
    render_content()
    
    # Update the conversation list in the sidebar
    from mcp_open_client.ui.common import update_conversation_list
    update_conversation_list()

def delete_conversation(conv_id):
    """Elimina una conversación"""
    app_state['conversations'] = [c for c in app_state['conversations'] if c['id'] != conv_id]
    save_conversations_to_storage()
    
    # If we deleted the current conversation, select another one
    if app_state['current_conversation_id'] == conv_id and app_state['conversations']:
        app_state['current_conversation_id'] = app_state['conversations'][0]['id']
    elif not app_state['conversations']:
        # Create a new default conversation if we deleted the last one
        create_conversation("Nueva conversación")
        
    from mcp_open_client.ui.common import render_content
    render_content()
    from nicegui import ui
    ui.notify("Conversación eliminada")
    
    # Update the conversation list in the sidebar
    from mcp_open_client.ui.common import update_conversation_list
    update_conversation_list()

def create_conversation(name):
    """Crea una nueva conversación"""
    if name.strip():
        import uuid
        new_id = str(uuid.uuid4())
        new_conversation = {
            'id': new_id,
            'name': name.strip(),
            'messages': []
        }
        app_state['conversations'].append(new_conversation)
        app_state['current_conversation_id'] = new_id
        save_conversations_to_storage()
        
        from mcp_open_client.ui.common import render_content
        render_content()
        from nicegui import ui
        ui.notify(f"Conversación '{name}' creada")
        
        # Update the conversation list in the sidebar
        from mcp_open_client.ui.common import update_conversation_list
        update_conversation_list()
        
        return new_id
    return None

def save_settings():
    """Saves the current settings and tools to a file in user's home directory"""
    try:
        # Use user's home directory with ~/mcp-open-client/config/
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, "mcp-open-client", "config")
        
        # Create directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # Save settings
        settings_path = os.path.join(config_dir, "user_settings.json")
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(app_state['settings'], f, indent=2)
        
        # Save tools
        tools_path = os.path.join(config_dir, "user_tools.json")
        with open(tools_path, 'w', encoding='utf-8') as f:
            json.dump(app_state['tools'], f, indent=2)
        
        from nicegui import ui
        ui.notify("Configuración y herramientas guardadas en " + config_dir)
    except Exception as e:
        from nicegui import ui
        ui.notify(f"Error al guardar configuración: {str(e)}", type='negative')

def load_settings():
    """Loads settings and tools from file in user's home directory if available"""
    settings_loaded = False
    tools_loaded = False
    
    try:
        # Use user's home directory with ~/mcp-open-client/config/
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, "mcp-open-client", "config")
        
        # Load settings
        settings_path = os.path.join(config_dir, "user_settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                app_state['settings'].update(loaded_settings)
            settings_loaded = True
        
        # Load tools
        tools_path = os.path.join(config_dir, "user_tools.json")
        if os.path.exists(tools_path):
            with open(tools_path, 'r', encoding='utf-8') as f:
                app_state['tools'] = json.load(f)
            tools_loaded = True
    except Exception as e:
        print(f"Error loading settings or tools: {str(e)}")
    
    return settings_loaded or tools_loaded

def migrate_settings_to_home_directory():
    """Migrates existing settings from current directory to user's home directory if needed"""
    try:
        # Current directory settings paths
        current_settings_path = os.path.join("settings", "user_settings.json")
        current_tools_path = os.path.join("settings", "user_tools.json")
        
        # User's home directory paths
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, "mcp-open-client", "config")
        home_settings_path = os.path.join(config_dir, "user_settings.json")
        home_tools_path = os.path.join(config_dir, "user_tools.json")
        
        # Create config directory if it doesn't exist
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # Migrate settings if they exist in current directory but not in home directory
        if os.path.exists(current_settings_path) and not os.path.exists(home_settings_path):
            with open(current_settings_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            with open(home_settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2)
        
        # Migrate tools if they exist in current directory but not in home directory
        if os.path.exists(current_tools_path) and not os.path.exists(home_tools_path):
            with open(current_tools_path, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
            
            with open(home_tools_path, 'w', encoding='utf-8') as f:
                json.dump(tools_data, f, indent=2)
                
        return True
    except Exception as e:
        print(f"Error migrating settings: {str(e)}")
        return False

def reinitialize_api():
    """Reinitializes the API client with current settings"""
    from mcp_open_client.api import ChatAPI
    global api
    
    try:
        api = ChatAPI(
            base_url=app_state['settings']['base_url'],
            model=app_state['settings']['model'],
            api_key=app_state['settings']['api_key']
        )
        from nicegui import ui
        ui.notify("API reinicializada con la nueva configuración")
        return True
    except Exception as e:
        from nicegui import ui
        ui.notify(f"Error al reinicializar API: {str(e)}", type='negative')
        return False

async def get_available_models():
    """Fetches available models from the API"""
    # Create a dictionary with only the current model
    current_model = app_state['settings']['model']
    current_model_dict = {current_model: f'Current: {current_model}'}
    
    # If API is not initialized, return only the current model
    if api is None:
        return False, current_model_dict
    
    try:
        success, models_list = await api.get_available_models()
        if success and models_list:
            # Convert list to dictionary format
            models_dict = {model: model for model in models_list}
            
            # Always ensure current model is in the dictionary
            if current_model not in models_dict:
                models_dict[current_model] = f'Current: {current_model}'
                
            return True, models_dict
        return False, current_model_dict
    except Exception as e:
        from nicegui import ui
        ui.notify(f"Error al obtener modelos: {str(e)}", type='negative')
        return False, current_model_dict

def save_conversations_to_storage():
    """Saves the current conversations to user storage"""
    from nicegui import app
    try:
        # Make sure we're only saving what we need to avoid large storage
        simplified_conversations = []
        for conv in app_state['conversations']:
            simplified_conversations.append({
                'id': conv['id'],
                'name': conv['name'],
                'messages': conv['messages']
            })
        
        # Save to user storage
        app.storage.user['conversations'] = simplified_conversations
        app.storage.user['current_conversation_id'] = app_state['current_conversation_id']
        app.storage.user['tools'] = app_state['tools']  # Save tools to storage
        return True
    except Exception as e:
        from nicegui import ui
        ui.notify(f"Error al guardar conversaciones: {str(e)}", type='negative')
        return False

def load_conversations_from_storage():
    """Loads conversations from user storage"""
    from nicegui import app
    try:
        if 'conversations' in app.storage.user:
            app_state['conversations'] = app.storage.user['conversations']
            if 'current_conversation_id' in app.storage.user:
                app_state['current_conversation_id'] = app.storage.user['current_conversation_id']
            if 'tools' in app.storage.user:
                app_state['tools'] = app.storage.user['tools']
            return True
        return False
    except Exception as e:
        from nicegui import ui
        ui.notify(f"Error al cargar conversaciones: {str(e)}", type='negative')
        return False
    
# Tool management functions
def create_tool(name, description, tool_type, parameters, code, active=True):
    """Creates a new tool"""
    import uuid
    tool_id = str(uuid.uuid4())
    
    new_tool = {
        'id': tool_id,
        'type': tool_type,
        'name': name,
        'description': description,
        'parameters': parameters,
        'code': code,
        'active': active
    }
    
    app_state['tools'].append(new_tool)
    save_conversations_to_storage()  # Save to NiceGUI storage
    save_settings()  # Save to file-based storage
    return tool_id

def update_tool(tool_id, name=None, description=None, tool_type=None, parameters=None, code=None, active=None):
    """Updates an existing tool"""
    for tool in app_state['tools']:
        if tool['id'] == tool_id:
            if name is not None:
                tool['name'] = name
            if description is not None:
                tool['description'] = description
            if tool_type is not None:
                tool['type'] = tool_type
            if parameters is not None:
                tool['parameters'] = parameters
            if code is not None:
                tool['code'] = code
            if active is not None:
                tool['active'] = active
                
            save_conversations_to_storage()  # Save to NiceGUI storage
            save_settings()  # Save to file-based storage
            from nicegui import ui
            ui.notify(f"Herramienta actualizada")
            return True
    
    from nicegui import ui
    ui.notify(f"Herramienta no encontrada", type='negative')
    return False

def execute_tool(tool_id, parameters):
    """Executes a tool with the given parameters"""
    # Find the tool
    tool = next((t for t in app_state['tools'] if t['id'] == tool_id), None)

    if not tool:
        from nicegui import ui
        ui.notify(f"Herramienta no encontrada", type='negative')
        return False, "Herramienta no encontrada"

    # Execute the tool code
    try:
        # Create a local namespace for execution
        local_namespace = {'params': parameters}
        
        # Execute the code
        exec(tool['code'], {}, local_namespace)
        
        # Get the result from the execute_tool function
        if 'execute_tool' in local_namespace:
            result = local_namespace['execute_tool'](parameters)
            return True, result
        else:
            from nicegui import ui
            ui.notify(f"La herramienta no tiene una función execute_tool", type='negative')
            return False, "La herramienta no tiene una función execute_tool"
    except Exception as e:
        from nicegui import ui
        ui.notify(f"Error al ejecutar la herramienta: {str(e)}", type='negative')
        return False, f"Error al ejecutar la herramienta: {str(e)}"

def delete_tool(tool_id):
    """Deletes a tool"""
    initial_count = len(app_state['tools'])
    app_state['tools'] = [t for t in app_state['tools'] if t['id'] != tool_id]
    
    if len(app_state['tools']) < initial_count:
        save_conversations_to_storage()  # Save to NiceGUI storage
        save_settings()  # Save to file-based storage
        from nicegui import ui
        ui.notify(f"Herramienta eliminada")
        return True
    else:
        from nicegui import ui
        ui.notify(f"Herramienta no encontrada", type='negative')
        return False