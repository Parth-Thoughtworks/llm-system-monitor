#!/usr/bin/env python3
"""
System Monitor Agent
Main orchestrator that combines SystemInfoCollector and LLMQueryProcessor
"""

from typing import Dict, Any, List, Optional

from llm_processor import LLMQueryProcessor
from system_info_collector import SystemInfoCollector


class SystemMonitorAgent:
    """
    Main orchestrator that combines SystemInfoCollector and LLMQueryProcessor.
    Handles the overall workflow and user interaction.
    """

    def __init__(self, api_key: Optional[str] = None, llm_model: str = "gpt-4o-mini"):
        """Initialize the system monitor agent"""
        self.system_collector = SystemInfoCollector()
        self.llm_processor = LLMQueryProcessor(api_key, llm_model)
        print("🤖 SystemMonitorAgent ready!")

    def handle_query(self, user_query: str) -> str:
        """Handle user query with LLM-powered processing"""
        print(f"🔍 Processing query: '{user_query}'")

        # Step 1: Parse query with LLM
        available_functions = self.system_collector.get_function_list()
        parsing_result = self.llm_processor.parse_query(user_query, available_functions)
        print(f"🧠 LLM parsed query: {parsing_result.get('reasoning', 'No reasoning provided')}")

        # Step 2: Collect system data
        functions_to_call = parsing_result.get('functions_to_call', [])
        print(f"📊 Calling functions: {functions_to_call}")

        system_data = self.system_collector.call_multiple_functions(functions_to_call)

        # Step 3: Generate response with LLM
        print("🤖 Generating response...")
        response = self.llm_processor.generate_response(user_query, system_data, parsing_result)

        return response

    def get_available_functions(self) -> List[str]:
        """Get list of available system monitoring functions"""
        return self.system_collector.get_function_list()

    def get_raw_system_data(self, function_names: List[str]) -> Dict[str, Any]:
        """Get raw system data without LLM processing"""
        return self.system_collector.call_multiple_functions(function_names)

    def test_components(self) -> Dict[str, bool]:
        """Test if all components are working"""
        results = {}

        # Test system collector
        try:
            self.system_collector.get_cpu_info()
            results['system_collector'] = True
        except Exception as e:
            print(f"❌ System collector test failed: {e}")
            results['system_collector'] = False

        # Test LLM processor
        results['llm_processor'] = self.llm_processor.test_connection()

        return results
