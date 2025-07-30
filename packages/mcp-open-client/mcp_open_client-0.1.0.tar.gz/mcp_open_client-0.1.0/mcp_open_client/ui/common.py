# Common UI components and functions

from nicegui import ui
from mcp_open_client import state
import json

def setup_ui():
    """Sets up the main UI structure"""
    # Create drawer (must be a direct child of the page)
    drawer = ui.left_drawer(value=True).classes('shadow-lg')
    
    # Create header (must be a direct child of the page)
    with ui.header().classes('w-full justify-between items-center'):
        ui.button(icon='menu', on_click=lambda: drawer.toggle())
        ui.label('Claude Chat').classes('text-h5')
        
        # Dark mode toggle
        dark_switch = ui.switch('Dark Mode', value=state.app_state['settings']['dark_mode'])
        
        @dark_switch.on_value_change
        async def toggle_dark_mode():
            value = dark_switch.value
            state.app_state['settings']['dark_mode'] = value
            ui.dark_mode().value = value
            state.save_settings()
            await ui.run_javascript(f'fetch("/dark-mode", {{method: "POST", headers: {{"Content-Type": "application/json"}}, body: JSON.stringify({value})}});')
    
    # Create sidebar (must be a direct child of the page)
    create_sidebar(drawer)
    
    # Create main content container (direct child of the page)
    state.content_container = ui.column().classes('w-full h-full p-4')

def render_content():
    """Renders the appropriate content based on the current page"""
    if state.content_container is None:
        return
    
    state.content_container.clear()
    
    if state.app_state['current_page'] == 'chat':
        from mcp_open_client.ui.chat import render_chat_page
        render_chat_page(state.content_container)
    elif state.app_state['current_page'] == 'settings':
        from mcp_open_client.ui.settings import render_settings_page
        render_settings_page(state.content_container)
    elif state.app_state['current_page'] == 'tools':
        from mcp_open_client.ui.tools import render_tools_page
        render_tools_page(state.content_container)

# Global reference to the conversations container
conversations_container = None

def update_conversation_list():
    """Updates the conversation list in the sidebar"""
    global conversations_container
    if conversations_container is None:
        return
        
    conversations_container.clear()
    
    with conversations_container:
        for conv in state.app_state['conversations']:
            with ui.row().classes('w-full items-center justify-between flex-nowrap'):
                # Truncate long conversation names
                display_name = conv['name']
                if len(display_name) > 15:
                    display_name = display_name[:12] + '...'
                    
                # Highlight current conversation
                btn_classes = 'w-4/5 text-left'
                if conv['id'] == state.app_state['current_conversation_id']:
                    btn_classes += ' bg-primary'
                    
                ui.button(display_name,
                         on_click=lambda c=conv['id']: state.select_conversation(c)
                         ).classes(btn_classes)
                
                # Delete button - positioned next to conversation name
                ui.button(icon='delete',
                         on_click=lambda c=conv['id']: state.delete_conversation(c)
                         ).classes('w-1/5 min-w-min')

def create_sidebar(drawer):
    """Creates the sidebar navigation"""
    global conversations_container
    
    # Add content to the drawer
    with drawer:
        ui.label('Claude Chat').classes('text-h5 q-pa-md')
        ui.separator()
        
        with ui.column().classes('w-full q-pa-md gap-2'):
            ui.button('Chat', icon='chat', on_click=lambda: change_page('chat')).classes('w-full')
            ui.button('Configuración', icon='settings', on_click=lambda: change_page('settings')).classes('w-full')
            ui.button('Herramientas', icon='build', on_click=lambda: change_page('tools')).classes('w-full')
            
            ui.separator()
            
            # Conversations section
            ui.label('Conversaciones').classes('text-h6 q-mt-md')
            
            # Button to create a new conversation
            def create_new_conversation():
                new_name = f"Conversación {len(state.app_state['conversations']) + 1}"
                state.create_conversation(new_name)
                
            ui.button('Nueva conversación', icon='add', on_click=create_new_conversation).classes('w-full q-mb-md')
            
            # List of conversations
            conversations_container = ui.column().classes('w-full gap-1')
            
            # Initial update of conversation list
            update_conversation_list()

def change_page(page_name):
    """Changes the current page"""
    state.app_state['current_page'] = page_name
    render_content()
    ui.notify(f'Página cambiada a: {page_name}')
    
    # Directly update conversation list
    update_conversation_list()

def format_message(message):
    """Formats a message for display"""
    is_user = message['role'] == 'user'
    is_tool = message['role'] == 'tool'
    
    # Handle tool calls
    if 'tool_calls' in message and message['tool_calls']:
        # Display the tool call message
        with ui.card().classes('w-full q-mb-md bg-blue-2 text-dark break-words'):
            ui.label('Claude está usando una herramienta:').classes('text-bold')
            
            for tool_call in message['tool_calls']:
                ui.label(f"Herramienta: {tool_call['function']['name']}").classes('q-ml-md')
                
                # Parse the arguments JSON string
                try:
                    args = json.loads(tool_call['function']['arguments'])
                    formatted_args = json.dumps(args, indent=2, ensure_ascii=False)
                except:
                    formatted_args = tool_call['function']['arguments']
                    
                ui.label(f"Argumentos: {formatted_args}").classes('q-ml-md break-all whitespace-pre-wrap')
        return
    
    # Handle tool responses
    if is_tool:
        with ui.card().classes('w-full q-mb-md bg-green-2 text-dark break-words'):
            ui.label(f"Respuesta de herramienta: {message['name']}").classes('text-bold')
            ui.label(message['content']).classes('q-ml-md break-all whitespace-pre-wrap')
        return
    
    # Handle regular messages
    ui.chat_message(
        text=message['content'] or "Usando herramientas...",
        name='Tú' if is_user else 'Claude',
        sent=is_user,
        text_html=False  # Using markdown instead of HTML
    ).classes('w-full q-mb-md break-words')