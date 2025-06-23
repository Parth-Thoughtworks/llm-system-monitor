#!/usr/bin/env python3
"""
Main Application Entry Point
LLM-Powered System Monitor with Interactive CLI
"""

import os
import sys
from system_monitor_agent import SystemMonitorAgent


def main():
    print("🤖 LLM-Powered System Monitor Agent")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n❌ OpenAI API key not found!")
        print("Please set the OPENAI_API_KEY environment variable:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr enter it now:")
        api_key = input("OpenAI API Key: ").strip()
        if not api_key:
            print("❌ API key required. Exiting.")
            return

    # Initialize the agent
    try:
        print("\n🚀 Initializing System Monitor Agent...")
        agent = SystemMonitorAgent(api_key)

        # Test components
        print("\n🔧 Testing components...")
        test_results = agent.test_components()

        for component, status in test_results.items():
            status_emoji = "✅" if status else "❌"
            print(f"  {status_emoji} {component}: {'OK' if status else 'FAILED'}")

        if not all(test_results.values()):
            print("\n❌ Some components failed. Please check your setup.")
            return

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    # Show available functions
    print(f"\n📋 Available system functions:")
    functions = agent.get_available_functions()
    for i, func in enumerate(functions, 1):
        print(f"  {i:2d}. {func}")

    # Interactive loop
    print("\n" + "=" * 50)
    print("🎯 Ask me anything about your system! Examples:")
    print("  • 'What's my battery percentage?'")
    print("  • 'Is my CPU running hot?'")
    print("  • 'How much memory am I using?'")
    print("  • 'Give me a full system overview'")
    print("  • 'What processes are using the most CPU?'")
    print("  • 'Show me disk usage'")
    print("\n💡 Commands:")
    print("  • 'functions' - Show available functions")
    print("  • 'test' - Test system components")
    print("  • 'quit' or 'exit' - Exit the program")
    print("=" * 50)

    while True:
        try:
            print()
            query = input("You: ").strip()

            if query.lower() in ['quit', 'exit', 'bye', 'q']:
                print("👋 Goodbye!")
                break

            if not query:
                continue

            if query.lower() == 'functions':
                print("\n📋 Available functions:")
                for i, func in enumerate(agent.get_available_functions(), 1):
                    print(f"  {i:2d}. {func}")
                continue

            if query.lower() == 'test':
                print("\n🔧 Testing components...")
                test_results = agent.test_components()
                for component, status in test_results.items():
                    status_emoji = "✅" if status else "❌"
                    print(f"  {status_emoji} {component}: {'OK' if status else 'FAILED'}")
                continue

            # Process the query
            print("🤖 Agent: ", end="", flush=True)
            response = agent.handle_query(query)
            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            print("Please try again or type 'quit' to exit")


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['psutil', 'openai', 'platform', 'datetime', 'json', 'os', 'typing']
    missing_packages = []

    for package in required_packages:
        try:
            if package in ['platform', 'datetime', 'json', 'os', 'typing']:
                # These are built-in modules
                __import__(package)
            else:
                # These need to be installed
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  • {package}")
        print("\nInstall them using:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False

    return True


if __name__ == "__main__":
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        print("❌ Please install missing dependencies first.")
        sys.exit(1)

    print("✅ All dependencies available!")
    main()