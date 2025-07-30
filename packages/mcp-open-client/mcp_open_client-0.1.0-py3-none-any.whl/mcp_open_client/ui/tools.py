# Tools UI components

from nicegui import ui
from mcp_open_client import state
import json
import asyncio

def render_tools_page(container):
    """Renders the tools page"""
    with container:
        # Page header with title and save button
        with ui.row().classes('w-full items-center justify-between q-mb-md'):
            ui.label('Herramientas').classes('text-h5')
            ui.button('Guardar herramientas', icon='save', on_click=state.save_settings).classes('bg-primary')
        
        # Tools list section
        with ui.card().classes('w-full q-mb-md shadow-lg'):
            with ui.row().classes('w-full items-center justify-between bg-primary text-white q-pa-sm rounded-top'):
                ui.label('Herramientas disponibles').classes('text-h6')
                ui.icon('build').classes('text-xl')
            
            # Container for the list of tools
            tools_list_container = ui.column().classes('w-full gap-2 q-pa-md')
            
            # Function to update the tools list
            def update_tools_list():
                tools_list_container.clear()
                
                if not state.app_state['tools']:
                    with tools_list_container:
                        with ui.row().classes('w-full items-center justify-center q-pa-lg'):
                            ui.icon('info').classes('text-grey q-mr-sm')
                            ui.label('No hay herramientas disponibles').classes('text-italic text-grey')
                else:
                    for tool in state.app_state['tools']:
                        with tools_list_container:
                            with ui.card().classes('w-full q-pa-md shadow-sm hover:shadow-md transition-shadow'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    # Left side with tool info
                                    with ui.column().classes('gap-1 flex-grow'):
                                        # Tool name and type in one row
                                        with ui.row().classes('items-center gap-2'):
                                            ui.icon('build_circle').classes('text-primary')
                                            ui.label(tool['name']).classes('text-h6 q-my-none')
                                            ui.label(f"Tipo: {tool['type']}").classes('bg-blue-100 text-blue-800 rounded-full px-2 py-1 text-xs')
                                            # Status badge
                                            status_color = 'bg-green-500' if tool['active'] else 'bg-grey-500'
                                            status_text = 'Activa' if tool['active'] else 'Inactiva'
                                            ui.label(status_text).classes(f'{status_color} text-white rounded-full px-2 py-1 text-xs')
                                        
                                        # Tool description
                                        ui.label(tool['description']).classes('text-body2 text-grey-8')
                                    
                                    # Right side with action buttons
                                    with ui.row().classes('items-center gap-2 flex-shrink-0'):
                                        # Active toggle with better styling
                                        ui.switch('Activar', value=tool['active'],
                                                on_change=lambda e, t_id=tool['id']: state.update_tool(t_id, active=e.value)
                                                ).classes('text-primary')
                                        
                                        # Edit button
                                        ui.button('Editar', icon='edit', on_click=lambda t=tool: show_edit_tool_dialog(t, update_tools_list)
                                                ).classes('bg-blue-500 text-white')
                                        
                                        # Delete button with confirmation
                                        ui.button('Eliminar', icon='delete', on_click=lambda t=tool['id']: confirm_delete_tool(t, update_tools_list)
                                                ).classes('bg-red-500 text-white')
            
            # Function to confirm tool deletion
            def confirm_delete_tool(tool_id, callback):
                with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
                    ui.label('Confirmar eliminación').classes('text-h6 q-mb-md')
                    ui.label('¿Estás seguro de que deseas eliminar esta herramienta? Esta acción no se puede deshacer.')
                    
                    with ui.row().classes('w-full justify-end gap-2 q-mt-lg'):
                        ui.button('Cancelar', on_click=dialog.close).classes('bg-grey-500 text-white')
                        ui.button('Eliminar', on_click=lambda: delete_tool_and_update(tool_id, dialog, callback)
                                ).classes('bg-red-500 text-white')
                
                dialog.open()
            
            # Function to delete a tool and update the list
            def delete_tool_and_update(tool_id, dialog, callback):
                if state.delete_tool(tool_id):
                    dialog.close()
                    callback()
                    ui.notify('Herramienta eliminada correctamente', type='positive')
            
            # Function to show edit tool dialog
            def show_edit_tool_dialog(tool, callback):
                with ui.dialog() as dialog, ui.card().classes('w-full max-w-5xl p-4'):
                    ui.label(f'Editar herramienta: {tool["name"]}').classes('text-h6 q-mb-md')
                    
                    # Tool name and description
                    ui.label('Nombre:').classes('text-weight-bold')
                    tool_name_input = ui.input(value=tool['name']).classes('w-full q-mb-md')
                    
                    ui.label('Descripción:').classes('text-weight-bold')
                    tool_description_input = ui.textarea(value=tool['description']).classes('w-full q-mb-md')
                    
                    # Tool type
                    ui.label('Tipo:').classes('text-weight-bold')
                    tool_type_input = ui.select(
                        options={'function': 'Función'},
                        value=tool['type'],
                        label='Tipo de herramienta'
                    ).classes('w-full q-mb-md')
                    
                    # JSON Schema editor for parameters
                    ui.label('Parámetros (Esquema JSON):').classes('text-weight-bold')
                    
                    # Parse the parameters JSON
                    try:
                        parameters_json = json.loads(tool['parameters'])
                    except:
                        parameters_json = {
                            "type": "object",
                            "properties": {},
                            "required": [],
                            "additionalProperties": False
                        }
                    
                    parameters_editor = ui.json_editor(
                        {'content': {'json': parameters_json}},
                        on_change=lambda e: ui.notify('Esquema actualizado')
                    ).classes('w-full q-mb-md min-h-[200px]')
                    
                    # Python code editor
                    ui.label('Código Python:').classes('text-weight-bold')
                    code_editor = ui.codemirror(
                        tool['code'],
                        language='python',
                        theme='basicLight',
                        line_wrapping=True
                    ).classes('w-full q-mb-md min-h-[300px]')
                    
                    # Buttons
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Cancelar', on_click=dialog.close).classes('bg-grey-500 text-white')
                        ui.button('Guardar cambios',
                                on_click=lambda: save_tool_changes(tool['id'], tool_name_input.value,
                                                                tool_description_input.value, tool_type_input.value,
                                                                parameters_editor, code_editor.value, dialog, callback)
                                ).classes('bg-primary text-white')
                
                dialog.open()
            
            # Function to save tool changes
            async def save_tool_changes(tool_id, name, description, tool_type, parameters_editor, code, dialog, callback):
                try:
                    # Validate inputs
                    if not name or not description:
                        ui.notify('El nombre y la descripción son obligatorios', type='warning')
                        return
                    
                    # Get schema JSON
                    parameters_json = await get_schema_json(parameters_editor)
                    parameters = json.dumps(parameters_json)
                    
                    # Update the tool
                    if state.update_tool(tool_id, name=name, description=description,
                                        tool_type=tool_type, parameters=parameters, code=code):
                        dialog.close()
                        callback()
                        ui.notify('Herramienta actualizada correctamente', type='positive')
                except Exception as e:
                    ui.notify(f'Error al actualizar la herramienta: {str(e)}', type='negative')
            
            # Initial update of the tools list
            update_tools_list()
        
        # Create new tool section
        with ui.card().classes('w-full shadow-lg'):
            with ui.row().classes('w-full items-center justify-between bg-primary text-white q-pa-sm rounded-top'):
                ui.label('Crear nueva herramienta').classes('text-h6')
                ui.icon('add_circle').classes('text-xl')
            
            with ui.column().classes('w-full q-pa-md gap-4'):
                # Tool name and description
                # Tool name input (full width)
                ui.label('Nombre:').classes('text-weight-bold')
                tool_name_input = ui.input(placeholder='Nombre de la herramienta').classes('w-full')
                
                # Hidden tool type input (always "function")
                tool_type_input = ui.input(value='function').classes('hidden')
                
                # Description input
                ui.label('Descripción:').classes('text-weight-bold')
                tool_description_input = ui.textarea(placeholder='Descripción detallada de la herramienta y su funcionamiento').classes('w-full')
                
                # JSON Schema editor for parameters with improved guidance
                # Editors in a two-column layout with explicit display flex
                ui.label('Editores').classes('text-weight-bold q-mt-md')
                with ui.row().classes('w-full gap-4 flex'):
                    # Left column - JSON Schema Editor
                    with ui.column().classes('w-1/2 flex-grow'):
                        ui.label('Parámetros (Esquema JSON)').classes('text-weight-bold')
                        # Default schema with required "type": "object" field
                        default_schema = {
                            'type': 'object',
                            'properties': {
                                'query': {
                                    'type': 'string',
                                    'description': 'Consulta o parámetro principal'
                                },
                                'options': {
                                    'type': 'object',
                                    'properties': {
                                        'limit': {
                                            'type': 'number',
                                            'description': 'Número máximo de resultados'
                                        }
                                    }
                                }
                            },
                            'required': ['query'],
                            'additionalProperties': False
                        }
                        
                        parameters_editor = ui.json_editor(
                            {'content': {'json': default_schema}},
                            on_change=lambda e: ui.notify('Esquema actualizado')
                        ).classes('w-full min-h-[350px]')
                    
                    # Right column - Python Code Editor
                    with ui.column().classes('w-1/2 flex-grow'):
                        ui.label('Código Python').classes('text-weight-bold')
                        ui.label('Implementa la función execute_tool que recibirá los parámetros y devolverá el resultado').classes('text-caption q-mb-sm')
                        
                        code_template = """def execute_tool(params):
    \"\"\"Implementación de la herramienta
    
    Args:
        params (dict): Parámetros recibidos según el esquema JSON definido
        
    Returns:
        dict: Resultado de la ejecución de la herramienta
    \"\"\"
    # Extraer parámetros
    query = params.get('query', '')
    options = params.get('options', {})
    limit = options.get('limit', 10)
    
    # Lógica de la herramienta
    # Aquí implementa la funcionalidad principal
    
    # Ejemplo de respuesta
    result = f"Procesando consulta: {query} (límite: {limit})"
    
    # Devolver resultado estructurado
    return {
        "result": result,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
"""
                        
                        code_editor = ui.codemirror(
                            code_template,
                            language='python',
                            theme='basicLight',
                            line_wrapping=True
                        ).classes('w-full min-h-[350px]')
                
                # Button to create the tool
                # Button to create the tool
                async def create_new_tool():
                    name = tool_name_input.value
                    description = tool_description_input.value
                    tool_type = tool_type_input.value
                    
                    # Validate inputs
                    if not name or not description:
                        ui.notify('El nombre y la descripción son obligatorios', type='warning')
                        return
                    
                    # Get code from editor
                    code = code_editor.value
                    
                    try:
                        # Use the helper function to get the schema JSON
                        parameters_json = await get_schema_json(parameters_editor)
                        
                        # Ensure the schema has the required "type": "object" field
                        if "type" not in parameters_json:
                            parameters_json["type"] = "object"
                        
                        # Convert to string for storage
                        parameters = json.dumps(parameters_json)
                        
                        # Create the tool
                        tool_id = state.create_tool(name, description, tool_type, parameters, code)
                        
                        # Clear inputs
                        tool_name_input.value = ''
                        tool_description_input.value = ''
                        
                        # Reset editors to default values
                        parameters_editor.run_editor_method('set', {
                            'type': 'object',
                            'properties': {},
                            'required': [],
                            'additionalProperties': False
                        })
                        code_editor.value = """def execute_tool(params):
    # Código para ejecutar la herramienta
    
    # Devolver resultado
    return {
        "result": "Éxito"
    }
"""
                        
                        # Update the tools list
                        update_tools_list()
                        
                        ui.notify('Herramienta creada correctamente', type='positive')
                        
                        # Scroll to top to see the new tool
                        ui.run_javascript('window.scrollTo(0, 0);')
                    except Exception as e:
                        ui.notify(f'Error al crear la herramienta: {str(e)}', type='negative')
                
                with ui.row().classes('w-full justify-end q-mt-md'):
                    ui.button('Crear herramienta', icon='add_circle', on_click=create_new_tool).classes('bg-primary text-white')
            
            # Helper function to get schema JSON from editor
            async def get_schema_json(editor):
                # Get the current value from the editor
                editor_value = await editor.run_editor_method('get')
                
                # Extract the JSON content
                if isinstance(editor_value, dict) and 'content' in editor_value and 'json' in editor_value['content']:
                    return editor_value['content']['json']
                else:
                    return {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    }