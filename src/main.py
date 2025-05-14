"""
CodeLve - Local AI Code Assistant
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import flet
    except ImportError:
        missing_deps.append("flet")
    
    try:
        import markdown2
    except ImportError:
        missing_deps.append("markdown2")
    
    try:
        import torch
    except ImportError:
        missing_deps.append("torch")
    
    try:
        import transformers
    except ImportError:
        missing_deps.append("transformers")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n📦 Install them with:")
        print(f"   pip install {' '.join(missing_deps)}")
        sys.exit(1)

def main():
    """Main entry point for CodeLve"""
    print("🚀 Starting CodeLve AI Assistant...")
    print("📊 Privacy-First Local AI Code Analysis")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    try:
        # Import and run the Flet-based chat interface
        from src.simplified_chat_ui import run_ui
        
        print("\n🖥️ Launching CodeLve Desktop Application...")
        print("This will open in a new window.\n")
        
        # Run the Flet UI as desktop app
        run_ui()
        
    except ImportError as e:
        print(f"\n❌ Error importing modules: {e}")
        print("\n🔍 Checking file structure...")
        
        # Check if required files exist
        required_files = [
            "src/simplified_chat_ui.py",
            "src/codelve_chat.py",
            "src/codebase_loader.py",
            "src/codebase_consolidator.py",
            "src/codebase_indexer.py",
            "src/framework_detector.py",
            "src/entity_analyzer.py",
            "src/architecture_analyzer.py",
            "src/query_analyzer.py",
            "src/dual_llm_handler.py",
            "src/advanced_query_processor.py"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = project_root / file
            if not file_path.exists():
                missing_files.append(file)
        
        if missing_files:
            print("\n📁 Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            print("\n💡 Make sure all required modules are in the src/ directory")
        
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using CodeLve! Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_cli():
    """Run CodeLve in CLI mode (legacy)"""
    print("🖥️ Running in CLI mode...")
    
    try:
        from src.codebase_loader import CodebaseLoader
        from src.codebase_consolidator import CodebaseConsolidator
        from src.framework_detector import FrameworkDetector
        from src.codebase_indexer import CodebaseIndexer
        from src.entity_analyzer import EntityAnalyzer
        from src.architecture_analyzer import ArchitectureAnalyzer
        from src.dual_llm_handler import DualLLMHandler
        from src.advanced_query_processor import AdvancedQueryProcessor
        
        # Get directory from command line or prompt
        if len(sys.argv) > 2:
            directory = sys.argv[2]
        else:
            directory = input("Enter the path to your codebase: ").strip()
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return
        
        print(f"\n📁 Loading codebase from: {directory}")
        
        # Load codebase
        loader = CodebaseLoader(directory)
        files = loader.scan_files()
        
        if not files:
            print("❌ No supported files found!")
            return
        
        print(f"✅ Found {len(files)} files")
        
        # Load files
        file_contents = loader.load_files(files)
        
        # Consolidate
        consolidated_content, stats = loader.consolidate_files(file_contents)
        
        print(f"📊 Consolidated: {stats['total_files']} files, {stats['total_lines']} lines")
        
        # Detect framework
        detector = FrameworkDetector()
        framework_info = detector.detect_frameworks(consolidated_content)
        primary_framework = framework_info.get('primary', 'Unknown')
        print(f"🔍 Detected framework: {primary_framework}")
        
        # Initialize dual LLM handler
        print("\n🤖 Initializing AI models...")
        dual_llm = DualLLMHandler()
        
        # Initialize advanced query processor
        indexer = CodebaseIndexer(consolidated_content)
        entity_analyzer = EntityAnalyzer(consolidated_content, framework_info)
        query_processor = AdvancedQueryProcessor(consolidated_content)
        
        # Interactive query loop
        print("\n💬 CodeLve is ready! Type 'exit' to quit.")
        print("Try: 'create a new component' or 'explain the architecture'\n")
        
        while True:
            query = input("\n🤖 You: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print("\n🤖 CodeLve: ", end="")
            
            try:
                # Process query through advanced processor
                response, response_type = query_processor.process_query(query)
                print(response)
            except Exception as e:
                print(f"Error processing query: {e}")
        
    except Exception as e:
        print(f"\n❌ Error in CLI mode: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if running with --cli flag
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        main()