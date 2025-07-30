# Main application entry point

import os
import argparse
from nicegui import ui, app
import uuid

# Import our modules
from mcp_open_client import state
from mcp_open_client.api import ChatAPI
from mcp_open_client.ui.common import setup_ui, render_content
from mcp_open_client.ui.chat import render_chat_page
from mcp_open_client.ui.settings import render_settings_page
from mcp_open_client.ui.tools import render_tools_page


def setup_app():
    """Setup the application"""
    # Migrate settings from current directory to user's home directory if needed
    state.migrate_settings_to_home_directory()
    
    # Load settings and tools from user's home directory
    state.load_settings()
    
    # Initialize API and set it in state
    state.api = ChatAPI(
        base_url=state.app_state['settings']['base_url'],
        model=state.app_state['settings']['model'],
        api_key=state.app_state['settings']['api_key']
    )
    
    # Setup page configuration
    # Commented out favicon-related code until favicon files are available
    # app.add_static_files('/favicon', 'assets/favicon')
    ui.page_title('Claude Chat')
    # ui.add_head_html('<link rel="icon" href="/favicon/favicon.ico" sizes="any">')
    # ui.add_head_html('<link rel="apple-touch-icon" href="/favicon/apple-touch-icon.png">')
    
    # Initialize state if not already done
    if not state.app_state['initialized']:
        # Load conversations from user storage if available
        @ui.page('/_init_storage')
        async def init_storage():
            await ui.context.client.connected()
            # Initialize user storage if needed
            if 'conversations' not in app.storage.user:
                app.storage.user['conversations'] = []
            
            # Load conversations and tools from storage
            state.app_state['conversations'] = app.storage.user.get('conversations', [])
            
            # Load tools from storage if not already loaded from file
            if 'tools' in app.storage.user and not state.app_state['tools']:
                state.app_state['tools'] = app.storage.user.get('tools', [])
            
            # Create default conversation if none exists
            if not state.app_state['conversations']:
                default_conversation = {
                    'id': str(uuid.uuid4()),
                    'name': 'Nueva conversación',
                    'messages': []
                }
                state.app_state['conversations'].append(default_conversation)
                app.storage.user['conversations'] = state.app_state['conversations']
                
            # Set current conversation
            if not state.app_state['current_conversation_id'] and state.app_state['conversations']:
                state.app_state['current_conversation_id'] = state.app_state['conversations'][0]['id']
            
            # Set initialized flag
            state.app_state['initialized'] = True
            
            # Redirect to main page
            ui.navigate.to('/')
        
        # Redirect to initialization page
        ui.navigate.to('/_init_storage')
    
    # Setup page routing
    @ui.page('/')
    def index_page():
        """Main application page"""
        # Setup the UI structure
        setup_ui()
        
        # Register page renderers
        state.app_state['page_renderers'] = {
            'chat': render_chat_page,
            'settings': render_settings_page,
            'tools': render_tools_page
        }
        
        # Render initial content (default to chat page)
        if not state.app_state['current_page']:
            state.app_state['current_page'] = 'chat'
        
        render_content()


def main():
    """Main entry point for the application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Claude Chat Application')
    parser.add_argument('--port', type=int, default=8081, help='Port to run the application on')
    args = parser.parse_args()
    
    # Setup the application
    setup_app()
    
    # Run the application
    ui.run(
        title='Claude Chat',
        # favicon='assets/favicon/favicon.ico',  # Commented out until favicon is available
        dark=True,
        reload=False,
        show=False,
        port=args.port,  # Use the port from command line arguments
        storage_secret='claude-chat-secret-key'  # Added for app.storage.user functionality
    )


# Allow running the module directly
if __name__ == '__main__':
    main()