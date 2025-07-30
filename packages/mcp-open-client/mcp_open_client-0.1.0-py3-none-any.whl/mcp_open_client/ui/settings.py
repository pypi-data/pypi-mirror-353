# Settings UI components

from nicegui import ui
from mcp_open_client import state
from typing import Optional
import asyncio

async def fetch_models():
    """Fetches available models from the API and returns them as options for the dropdown"""
    # Get the current model
    current_model = state.app_state['settings']['model']
    
    # Create a dictionary with only the current model
    current_model_dict = {current_model: f'Current: {current_model}'}
    
    # If API is not initialized, return only the current model
    if state.api is None:
        ui.notify('API no inicializada, solo se muestra el modelo actual', type='warning')
        return current_model_dict
    
    try:
        # Show ongoing notification
        ui.notify('Obteniendo modelos disponibles...', type='ongoing')
        success, models_dict = await state.get_available_models()
        
        if success and models_dict:
            # Return the models dictionary from the API
            return models_dict
        else:
            # This warning notification will replace the ongoing one
            ui.notify('No se pudieron obtener los modelos de la API, solo se muestra el modelo actual', type='warning')
            return current_model_dict
    except Exception as e:
        # This error notification will replace the ongoing one
        ui.notify(f'Error al obtener modelos: {str(e)}', type='negative')
        return current_model_dict

def render_settings_page(container):
    """Renders the settings page"""
    with container:
        ui.label('Configuración').classes('text-h5 q-mb-md')
        
        with ui.card().classes('w-full q-mb-md'):
            ui.label('Modelo de IA').classes('text-h6 q-mb-sm')
            
            # Get the current model
            current_model = state.app_state['settings']['model']
            
            # Initialize with only the current model (no default options)
            initial_options = {current_model: f'Current: {current_model}'}
            
            # Create the model dropdown with minimal initial options
            model_select = ui.select(
                options=initial_options,
                value=current_model,
                on_change=lambda e: state.update_setting('model', e.value)
            ).classes('w-full q-mb-md')
            
            # Function to update the model dropdown
            async def update_model_dropdown():
                # Use fetch_models directly which returns a dictionary
                # fetch_models will show its own notifications
                model_options = await fetch_models()
                
                # Update the dropdown options and force a UI refresh
                model_select.options = model_options
                model_select.update()
                
                # Make sure the current value is valid
                current_model = state.app_state['settings']['model']
                if current_model in model_options:
                    model_select.value = current_model
                elif model_options:
                    # Set to first option if current is not available
                    first_model = next(iter(model_options))
                    model_select.value = first_model
                    state.update_setting('model', first_model)
                
                ui.notify('Lista de modelos actualizada', type='positive')
            
            # Add a refresh button with a more descriptive label
            ui.button('Actualizar lista de modelos', icon='refresh', on_click=update_model_dropdown).classes('q-mb-md')
            
            # Initialize with only the current model without automatic fetching
            # This prevents the get_available_models function from being called too frequently
        
        with ui.card().classes('w-full q-mb-md'):
            ui.label('Parámetros de Generación').classes('text-h6 q-mb-sm')
            
            # Temperature slider
            ui.label(f"Temperatura: {state.app_state['settings']['temperature']}")
            ui.slider(
                min=0, max=1, step=0.1,
                value=state.app_state['settings']['temperature'],
                on_change=lambda e: update_temperature(e.value)
            ).classes('w-full q-mb-md')
            
            # Max tokens slider
            ui.label(f"Tokens máximos: {state.app_state['settings']['max_tokens']}")
            ui.slider(
                min=100, max=4000, step=100,
                value=state.app_state['settings']['max_tokens'],
                on_change=lambda e: update_max_tokens(e.value)
            ).classes('w-full')
        
        with ui.card().classes('w-full q-mb-md'):
            ui.label('System Prompt').classes('text-h6 q-mb-sm')
            
            # System prompt text area
            ui.label('Prompt del sistema:')
            system_prompt_input = ui.textarea(
                value=state.app_state['settings']['system_prompt'],
                placeholder='Ingresa el prompt del sistema...'
            ).classes('w-full q-mb-md min-h-[100px]')
            
            # Update system prompt on change
            def update_system_prompt():
                state.update_setting('system_prompt', system_prompt_input.value)
            
            system_prompt_input.on('change', lambda _: update_system_prompt())
            
        with ui.card().classes('w-full q-mb-md'):
            ui.label('Configuración de API').classes('text-h6 q-mb-sm')
            
            # Base URL input
            ui.label('URL Base:')
            base_url_input = ui.input(
                value=state.app_state['settings']['base_url'],
                on_change=lambda e: update_base_url(e.value)
            ).classes('w-full q-mb-md')
            
            # API Key input
            ui.label('API Key:')
            api_key_input = ui.input(
                value=state.app_state['settings']['api_key'],
                password=True,
                on_change=lambda e: update_api_key(e.value)
            ).classes('w-full q-mb-md')
            
            # Button to apply API changes
            ui.button('Aplicar cambios de API', on_click=apply_api_changes).classes('w-full')
        
        with ui.card().classes('w-full'):
            ui.label('Información').classes('text-h6 q-mb-sm')
            
            with ui.row().classes('w-full items-center'):
                ui.label('Versión de la aplicación:').classes('text-bold')
                ui.label('1.0.0')
            
            with ui.row().classes('w-full items-center'):
                ui.label('Desarrollado por:').classes('text-bold')
                ui.label('Claude Chat')

def update_temperature(value):
    """Updates the temperature setting and shows the current value"""
    state.update_setting('temperature', value)
    ui.notify(f'Temperatura actualizada a: {value}')

def update_max_tokens(value):
    """Updates the max tokens setting and shows the current value"""
    state.update_setting('max_tokens', int(value))
    ui.notify(f'Tokens máximos actualizados a: {int(value)}')

def update_base_url(value):
    """Updates the base URL setting"""
    state.update_setting('base_url', value)
    ui.notify(f'URL Base actualizada a: {value}')

def update_api_key(value):
    """Updates the API key setting"""
    state.update_setting('api_key', value)
    ui.notify('API Key actualizada')

def apply_api_changes():
    """Applies API changes by reinitializing the API client"""
    state.save_settings()
    if state.reinitialize_api():
        ui.notify('Configuración de API aplicada correctamente', type='positive')
        
        # No need to refresh the entire page, just notify the user
        # The user can manually refresh the model list if needed
    else:
        ui.notify('Error al aplicar configuración de API', type='negative')