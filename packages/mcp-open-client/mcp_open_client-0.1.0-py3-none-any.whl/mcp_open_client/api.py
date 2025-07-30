from openai import AsyncOpenAI

class ChatAPI:
    def __init__(self, base_url: str, model: str, api_key: str = "not-needed"):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0,
            max_retries=3,
        )
        self.model = model
        self.base_url = base_url
        
    def validate_messages(self, messages):
        """Ensure all messages have valid content fields"""
        validated = []
        for msg in messages:
            # Create a copy to avoid modifying the original
            msg_copy = msg.copy()
            
            # Ensure content is never null
            if msg_copy.get('content') is None:
                msg_copy['content'] = ""
            
            # Ensure tool messages have tool_call_id
            if msg_copy.get('role') == 'tool' and 'tool_call_id' not in msg_copy:
                # If missing, try to find it in the original message
                if 'tool_call_id' in msg:
                    msg_copy['tool_call_id'] = msg['tool_call_id']
                
            validated.append(msg_copy)
        return validated
        
    async def get_available_models(self) -> tuple[bool, list]:
        """Fetches available models from the API"""
        try:
            response = await self.client.models.list()
            models = [model.id for model in response.data]
            return True, models
        except Exception as e:
            error_msg = f"Error fetching models: {type(e).__name__}: {str(e)}"
            return False, []
        
    async def send_message(self, messages: list, model: str = None, temperature: float = 0.7, max_tokens: int = 2000, tools: list = None) -> tuple[bool, str, bool]:
        try:
            # Validate messages to ensure content is never null
            validated_messages = self.validate_messages(messages)
            
            # Create parameters for the API call
            params = {
                "model": model or self.model,
                "messages": validated_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Add tools if provided
            # Note: For OpenAI-compatible API, tools must use the "function" format
            # Example format:
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "tool_name",
            #         "description": "tool_description",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {...},
            #             "required": [...],
            #             "additionalProperties": false
            #         }
            #     }
            # }
            if tools and len(tools) > 0:
                params["tools"] = tools
            
            # Make the API call
            response = await self.client.chat.completions.create(**params)
            
            # Check if there's a tool call in the response
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                # Get the tool calls
                tool_calls = response.choices[0].message.tool_calls
                
                # Create a message for the tool call
                tool_call_message = {
                    "role": "assistant",
                    "content": "",  # Empty string instead of null
                    "tool_calls": []
                }
                
                # Process each tool call
                tool_results = []
                
                for tool_call in tool_calls:
                    # Extract tool information
                    tool_name = tool_call.function.name
                    tool_arguments = tool_call.function.arguments
                    tool_id = tool_call.id
                    
                    # Find the tool by name
                    from mcp_open_client import state
                    import json
                    
                    # Find the tool in our tools list
                    tool = next((t for t in state.app_state['tools'] if t['name'] == tool_name), None)
                    
                    if tool:
                        # Add the tool call to the message
                        tool_call_message["tool_calls"].append({
                            "id": tool_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_arguments
                            }
                        })
                        
                        # Parse arguments
                        try:
                            args = json.loads(tool_arguments)
                        except:
                            args = {}
                        
                        # Execute the tool
                        success, result = state.execute_tool(tool['id'], args)
                        
                        # Format the result
                        tool_result = {
                            "tool_call_id": tool_id,
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps(result) if isinstance(result, dict) else str(result)
                        }
                        
                        tool_results.append(tool_result)
                
                # Get the current conversation
                current_conv_id = state.app_state['current_conversation_id']
                current_conv = next((c for c in state.app_state['conversations'] if c['id'] == current_conv_id), None)
                
                if current_conv:
                    # Add the tool call message to the conversation
                    current_conv['messages'].append(tool_call_message)
                    
                    # Add the tool results to the conversation
                    for result in tool_results:
                        current_conv['messages'].append(result)
                    
                    # Save to user storage
                    state.save_conversations_to_storage()
                
                # Add the tool call message to the messages for the API
                messages.append(tool_call_message)
                
                # Add the tool results to the messages for the API
                for result in tool_results:
                    messages.append(result)
                
                # Make a second API call with the tool results
                # Validate messages again before the second API call
                validated_messages = self.validate_messages(messages)
                
                response = await self.client.chat.completions.create(
                    model=model or self.model,
                    messages=validated_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Return the final response with has_tool_calls=True
                return True, response.choices[0].message.content, True
            
            # Return normal message content with has_tool_calls=False
            return True, response.choices[0].message.content, False
        except Exception as e:
            error_msg = f"**Error:** {type(e).__name__}: {str(e)}"
            return False, error_msg, False