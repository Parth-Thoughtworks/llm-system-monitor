#!/usr/bin/env python3
"""
LLM Query Processor
Handles LLM interactions for query parsing and response generation
"""

import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI


class LLMQueryProcessor:
    """
    Handles LLM interactions for query parsing and response generation.
    Independent of system monitoring functionality.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize the LLM query processor"""
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.model = model
        print("🧠 LLMQueryProcessor initialized")

    def get_system_prompt_for_parsing(self, available_functions: List[str]) -> str:
        """Generate system prompt for query parsing based on available functions"""
        functions_desc = "\n".join(
            [f"- {func}: {self._get_function_description(func)}" for func in available_functions])

        return f"""You are a system monitor query parser. Your job is to analyze user queries about computer system information and determine which system functions to call.

        Available functions:
        {functions_desc}
        
        Respond with a JSON object containing:
        1. "functions_to_call": Array of function names to call
        2. "response_style": How to format the response ("brief", "detailed", "conversational")
        3. "focus": What aspect the user is most interested in
        4. "reasoning": Brief explanation of your parsing
        
        Examples:
        Query: "What's my battery percentage?" 
        Response: {{"functions_to_call": ["get_battery_info"], "response_style": "brief", "focus": "battery_percentage", "reasoning": "User wants specific battery percentage"}}
        
        Query: "Give me a full system overview"
        Response: {{"functions_to_call": ["get_battery_info", "get_cpu_info", "get_memory_info", "get_disk_info"], "response_style": "detailed", "focus": "system_overview", "reasoning": "User wants comprehensive system status"}}
        
        Query: "Is my laptop running hot?"
        Response: {{"functions_to_call": ["get_temperature_info", "get_cpu_info"], "response_style": "conversational", "focus": "temperature", "reasoning": "User concerned about system temperature"}}"""

    def _get_function_description(self, func_name: str) -> str:
        """Get description for a function"""
        descriptions = {
            'get_battery_info': 'Battery percentage, charging status, time remaining',
            'get_cpu_info': 'CPU usage, cores, frequency',
            'get_memory_info': 'RAM usage, available memory, swap',
            'get_disk_info': 'Disk usage, free space, partitions',
            'get_network_info': 'Network statistics, data transferred',
            'get_processes_info': 'Running processes, CPU/memory usage',
            'get_system_info': 'OS, platform, architecture details',
            'get_uptime_info': 'System uptime, boot time',
            'get_temperature_info': 'System temperatures (if available)'
        }
        return descriptions.get(func_name, 'System information')

    def parse_query(self, user_query: str, available_functions: List[str]) -> Dict[str, Any]:
        """Parse user query and determine what system info to fetch"""
        system_prompt = self.get_system_prompt_for_parsing(available_functions)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                max_tokens=200
            )

            parsed_response = json.loads(response.choices[0].message.content)
            return parsed_response

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing error: {e}")
            return {
                "functions_to_call": ["get_battery_info", "get_cpu_info", "get_memory_info"],
                "response_style": "brief",
                "focus": "general",
                "reasoning": "Fallback due to parsing error"
            }
        except Exception as e:
            print(f"⚠️  LLM API error: {e}")
            return {
                "functions_to_call": ["get_battery_info", "get_cpu_info", "get_memory_info"],
                "response_style": "brief",
                "focus": "general",
                "reasoning": "Fallback due to API error"
            }

    def generate_response(self, user_query: str, system_data: Dict[str, Any], parsing_result: Dict[str, Any]) -> str:
        """Generate natural language response from system data"""
        system_prompt = f"""You are a helpful system monitor assistant. Generate a natural, conversational response to the user's query about their computer system.

        User's query: "{user_query}"
        Parsing result: {json.dumps(parsing_result, indent=2)}
        System data: {json.dumps(system_data, indent=2)}
        
        Guidelines:
        - Be conversational and helpful
        - Use the response_style from parsing: {parsing_result.get('response_style', 'conversational')}
        - Focus on what the user asked about: {parsing_result.get('focus', 'general')}
        - Include relevant emojis
        - If there are any errors in the data, mention them helpfully
        - Convert technical units to user-friendly formats
        - Be concise but informative
        
        Generate a response that directly answers the user's question using the system data provided."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please respond to: {user_query}"}
                ],
                temperature=0.3,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️  Response generation error: {e}")
            return f"I gathered your system information but had trouble generating a response. Here's the raw data: {system_data}"

    def test_connection(self) -> bool:
        """Test if the LLM connection is working"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, respond with 'OK' if you can hear me."}
                ],
                max_tokens=10
            )
            return "OK" in response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM connection test failed: {e}")
            return False