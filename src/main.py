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
        import PyQt5
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        import markdown2
    except ImportError:
        missing_deps.append("markdown2")
    
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
        # Import and run the chat interface
        from src.codelve_chat import CodeLveChat
        from PyQt5.QtWidgets import QApplication
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("CodeLve")
        app.setOrganizationName("CodeLve")
        
        # Create and show the main window
        window = CodeLveChat()
        window.show()
        
        # Run the application
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"\n❌ Error importing modules: {e}")
        print("\n🔍 Checking file structure...")
        
        # Check if required files exist
        required_files = [
            "src/codelve_chat.py",
            "src/codebase_loader.py",
            "src/codebase_consolidator.py",
            "src/codebase_indexer.py",
            "src/framework_detector.py",
            "src/entity_analyzer.py",
            "src/architecture_analyzer.py",
            "src/query_analyzer.py"
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
        
        # Get directory from command line or prompt
        if len(sys.argv) > 1:
            directory = sys.argv[1]
        else:
            directory = input("Enter the path to your codebase: ").strip()
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return
        
        print(f"\n📁 Loading codebase from: {directory}")
        
        # Load codebase
        loader = CodebaseLoader()
        file_contents = loader.load_directory(directory)
        
        if not file_contents:
            print("❌ No supported files found!")
            return
        
        print(f"✅ Loaded {len(file_contents)} files")
        
        # Consolidate
        consolidator = CodebaseConsolidator()
        consolidated_content, stats = consolidator.consolidate_files(file_contents)
        
        print(f"📊 Consolidated: {stats['file_count']} files, {stats['total_lines']} lines")
        
        # Detect framework
        detector = FrameworkDetector()
        framework = detector.detect_framework(file_contents)
        print(f"🔍 Detected framework: {framework}")
        
        # Index
        indexer = CodebaseIndexer()
        indexer.index_content(consolidated_content)
        print("✅ Codebase indexed successfully")
        
        # Interactive query loop
        print("\n💬 CodeLve is ready! Type 'exit' to quit.")
        print("Try: 'explain the architecture' or 'find UserService'\n")
        
        # Initialize analyzers
        entity_analyzer = EntityAnalyzer(detector)
        architecture_analyzer = ArchitectureAnalyzer(detector)
        
        while True:
            query = input("\n🤖 You: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print("\n🤖 CodeLve: ", end="")
            
            # Simple query routing
            if 'architecture' in query.lower():
                result = architecture_analyzer.analyze_codebase_architecture(
                    consolidated_content, framework
                )
                print(result)
            elif 'find' in query.lower():
                search_term = query.lower().replace('find', '').strip()
                # Simple search implementation
                lines = consolidated_content.split('\n')
                matches = []
                for i, line in enumerate(lines):
                    if search_term in line.lower():
                        matches.append(f"Line {i}: {line.strip()}")
                        if len(matches) >= 5:
                            break
                
                if matches:
                    print(f"Found {len(matches)} matches:")
                    for match in matches:
                        print(f"  {match}")
                else:
                    print(f"No matches found for '{search_term}'")
            else:
                print("I can help you with:")
                print("  - 'explain the architecture' - Get system overview")
                print("  - 'find [term]' - Search for something")
                print("  - 'exit' - Quit the program")
        
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