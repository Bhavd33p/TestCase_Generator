#!/usr/bin/env python3
"""
Setup and run script for LangGraph Milvus Test Case Generator
"""

import os
import sys
from dotenv import load_dotenv

def setup_environment():
    """Setup environment variables and check dependencies"""
    print("🔧 Setting up environment...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("Or create a .env file with: OPENAI_API_KEY=your-api-key-here")
        return False
    
    print("✅ Environment setup complete")
    return True

def check_milvus():
    """Check if Milvus is running"""
    print("🔍 Checking Milvus connection...")
    try:
        from pymilvus import connections
        connections.connect("default", host="localhost", port="19530")
        print("✅ Milvus connection successful")
        return True
    except Exception as e:
        print(f"❌ Milvus connection failed: {e}")
        print("Please make sure Milvus is running on localhost:19530")
        print("You can start Milvus using Docker:")
        print("docker run -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest")
        return False

def main():
    """Main setup and run function"""
    print("🚀 LangGraph Milvus Test Case Generator Setup")
    print("=" * 50)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Check Milvus
    if not check_milvus():
        print("\n⚠️  Milvus is not running, but you can still run the script.")
        print("It will use the fallback knowledge base for all queries.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🎯 Starting the workflow...")
    print("=" * 50)
    
    # Import and run the main workflow
    try:
        from langgraph_milvus_testcase_generator import main as run_workflow
        run_workflow()
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 