# Chat UI components and functionality

from nicegui import ui
from mcp_open_client import state
import json

def render_chat_page(container):
    """Renders the chat page"""
    with container:
        # Check if we have a current conversation
        current_conv = next((c for c in state.app_state['conversations']
                              if c['id'] == state.app_state['current_conversation_id']), None)
        
        if current_conv:
            # Display existing conversation
            ui.label(f"Conversación: {current_conv['name']}").classes('text-h6 q-mb-md')
            
            # Chat messages container
            state.chat_container = ui.column().classes('w-full h-[60vh] overflow-y-auto overflow-x-hidden')
            render_messages()
            
            # Loading spinner (hidden by default)
            state.loading_spinner = ui.spinner(size='lg').classes('self-center my-4').style('display: none')
            
            # Input area
            with ui.row().classes('w-full items-center'):
                state.chat_input = ui.input(placeholder='Escribe un mensaje...').classes('flex-grow')
                
                # Add event handler for Enter key
                def on_enter(_):
                    send_message()
                
                state.chat_input.on('keydown.enter', on_enter)
                    
                state.send_button = ui.button('Enviar', icon='send', on_click=send_message).classes('q-ml-sm')
        else:
            # No conversation selected, show welcome screen
            with ui.column().classes('w-full h-full items-center justify-center'):
                ui.label('Bienvenido a Claude Chat').classes('text-h4 q-mb-xl')
                ui.button('Iniciar Nueva Conversación',
                         icon='add',
                         on_click=lambda: state.create_conversation("Nueva conversación")
                         ).classes('text-h6')

def render_messages():
    """Renders the messages in the current conversation"""
    if state.chat_container is None:
        return
    
    state.chat_container.clear()
    
    current_conv = next((c for c in state.app_state['conversations'] 
                        if c['id'] == state.app_state['current_conversation_id']), None)
    
    if current_conv:
        with state.chat_container:
            for message in current_conv['messages']:
                from mcp_open_client.ui.common import format_message
                format_message(message)

def send_message():
    """Sends a message to the API and updates the UI"""
    if state.chat_input is None or not state.chat_input.value.strip():
        return
    
    message_text = state.chat_input.value.strip()
    state.chat_input.value = ''
    
    # Add user message to conversation
    current_conv = next((c for c in state.app_state['conversations']
                        if c['id'] == state.app_state['current_conversation_id']), None)
    
    if current_conv:
        user_message = {'role': 'user', 'content': message_text}
        current_conv['messages'].append(user_message)
        
        # Save to user storage
        state.save_conversations_to_storage()
        
        render_messages()
        
        # Show loading spinner and disable input
        if hasattr(state, 'loading_spinner') and state.loading_spinner:
            state.loading_spinner.style('display: flex')
        if hasattr(state, 'chat_input') and state.chat_input:
            state.chat_input.disable()
        if hasattr(state, 'send_button') and state.send_button:
            state.send_button.disable()
        
        # Create message history for API
        # Add system prompt as the first message
        system_prompt = state.app_state['settings']['system_prompt']
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation messages with validation
        for m in current_conv['messages']:
            msg = {'role': m['role']}
            
            # Ensure content is never null
            msg['content'] = m.get('content', "")
            if msg['content'] is None:
                msg['content'] = ""
            
            # Add tool_calls if present
            if 'tool_calls' in m:
                msg['tool_calls'] = m['tool_calls']
            
            # Add name if present (for tool responses)
            if 'name' in m:
                msg['name'] = m['name']
                
            # Add tool_call_id if present (for tool responses)
            if 'tool_call_id' in m:
                msg['tool_call_id'] = m['tool_call_id']
            
            messages.append(msg)
        
        # Call API asynchronously
        async def get_response():
            try:
                # Get active tools
                active_tools = []
                for tool in state.app_state['tools']:
                    if tool.get('active', True):
                        # Parse parameters
                        if isinstance(tool["parameters"], str):
                            params = json.loads(tool["parameters"])
                        else:
                            params = tool["parameters"]
                        
                        # Ensure parameters has the required "type": "object" field
                        if "type" not in params:
                            params["type"] = "object"
                        
                        # Format tool according to OpenAI function calling format
                        active_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool["name"],
                                "description": tool["description"],
                                "parameters": params
                            }
                        })
                
                success, content, has_tool_calls = await state.api.send_message(
                    messages=messages,
                    model=state.app_state['settings']['model'],
                    temperature=state.app_state['settings']['temperature'],
                    max_tokens=state.app_state['settings']['max_tokens'],
                    tools=active_tools if active_tools else None
                )
                
                if success:
                    # Always add the assistant's response to the conversation
                    # For tool calls, this will be the final response after processing the tool results
                    assistant_message = {'role': 'assistant', 'content': content}
                    current_conv['messages'].append(assistant_message)
                    
                    # Save to user storage
                    state.save_conversations_to_storage()
                    
                    render_messages()
                    
                    # Scroll to bottom
                    if state.chat_container:
                        ui.run_javascript('''
                            setTimeout(() => {
                                const chatContainer = document.querySelector('.overflow-y-auto');
                                if (chatContainer) {
                                    chatContainer.scrollTop = chatContainer.scrollHeight;
                                }
                            }, 100);
                        ''')
                else:
                    ui.notify('Error al obtener respuesta', type='negative')
            finally:
                # Hide loading spinner and re-enable input
                if hasattr(state, 'loading_spinner') and state.loading_spinner:
                    state.loading_spinner.style('display: none')
                if hasattr(state, 'chat_input') and state.chat_input:
                    state.chat_input.enable()
                if hasattr(state, 'send_button') and state.send_button:
                    state.send_button.enable()
        
        ui.timer(0.5, get_response, once=True)