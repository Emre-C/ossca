#!/usr/bin/env python3
"""
DeepWiki CLI - Command Line Interface for DeepWiki

This is the main entry point for the DeepWiki application, providing a CLI
for building knowledge bases from code repositories and querying them.

Usage:
    python main.py <repo_url> [options]
    
Examples:
    python main.py https://github.com/owner/repo --build
    python main.py https://github.com/owner/repo
    python main.py /path/to/local/repo --build --provider=openai
"""

import argparse
import logging
import sys
import os
from typing import Optional

from deepwiki import KnowledgeBase
from deepwiki.logging_config import setup_logging

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DeepWiki - Create queryable knowledge bases from code repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/owner/repo --build
      Build a new knowledge base from a GitHub repository
  
  %(prog)s https://github.com/owner/repo
      Load existing knowledge base or build if it doesn't exist
  
  %(prog)s /path/to/local/repo --build --provider=openai
      Build from local repository using OpenAI models
      
  %(prog)s https://github.com/owner/repo --force-rebuild
      Force rebuild even if knowledge base exists
        """
    )
    
    # Required arguments
    parser.add_argument(
        "repo_url", 
        help="Repository URL (GitHub, GitLab, Bitbucket) or local path"
    )
    
    # Optional arguments
    parser.add_argument(
        "--build", 
        action="store_true",
        help="Force building of knowledge base (default: load existing if available)"
    )
    
    parser.add_argument(
        "--force-rebuild",
        action="store_true", 
        help="Force rebuild even if knowledge base already exists"
    )
    
    parser.add_argument(
        "--provider",
        default="google",
        choices=["google", "openai", "openrouter", "ollama", "bedrock", "azure"],
        help="AI model provider to use (default: google)"
    )
    
    parser.add_argument(
        "--model",
        help="Specific model to use with the provider"
    )
    
    parser.add_argument(
        "--type",
        default="github",
        choices=["github", "gitlab", "bitbucket", "local"],
        help="Repository type (default: github)"
    )
    
    parser.add_argument(
        "--access-token",
        help="Access token for private repositories"
    )
    
    parser.add_argument(
        "--excluded-dirs",
        nargs="*",
        help="Directories to exclude from processing"
    )
    
    parser.add_argument(
        "--excluded-files", 
        nargs="*",
        help="File patterns to exclude from processing"
    )
    
    parser.add_argument(
        "--included-dirs",
        nargs="*", 
        help="Directories to include exclusively"
    )
    
    parser.add_argument(
        "--included-files",
        nargs="*",
        help="File patterns to include exclusively"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress most output"
    )
    
    return parser.parse_args()

def setup_logging_level(verbose: bool, quiet: bool):
    """Set up logging based on verbosity flags."""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Set up logging
    setup_logging(level)

def print_welcome(repo_url: str):
    """Print welcome message."""
    print("=" * 60)
    print("🧠 DeepWiki - Interactive Code Repository Q&A")
    print("=" * 60)
    print(f"Repository: {repo_url}")
    print("=" * 60)
    print()

def print_help():
    """Print help message for interactive mode."""
    print("Commands:")
    print("  help, h, ?     - Show this help message")
    print("  clear, cls     - Clear conversation history")
    print("  exit, quit, q  - Exit the application")
    print("  Any other text - Ask a question about the repository")
    print()

def interactive_qa_loop(kb: KnowledgeBase, repo_url: str):
    """Run the interactive Q&A loop."""
    print_welcome(repo_url)
    print("💡 Ask questions about the repository. Type 'help' for commands or 'exit' to quit.")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("❓ Your question: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() in ['help', 'h', '?']:
                print_help()
                continue
            elif user_input.lower() in ['clear', 'cls']:
                kb.clear_conversation()
                print("🧹 Conversation history cleared.")
                continue
            
            # Process the question
            print("🤔 Thinking...")
            answer, retrieved_docs = kb.query(user_input)
            
            # Display the answer
            print("\n📝 Answer:")
            print("-" * 40)
            print(answer)
            print("-" * 40)
            
            # Show retrieved document count
            if retrieved_docs:
                print(f"📚 (Based on {len(retrieved_docs)} relevant documents)")
            
            print()
            
            # Add to conversation history
            kb.add_conversation_turn(user_input, answer)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'exit' to quit.")
            print()

def main():
    """Main entry point for the CLI."""
    args = parse_arguments()
    
    # Set up logging
    setup_logging_level(args.verbose, args.quiet)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the knowledge base
        if not args.quiet:
            print(f"🚀 Initializing DeepWiki with {args.provider} provider...")
        
        kb = KnowledgeBase(provider=args.provider, model=args.model)
        
        # Determine if we should build or load
        should_build = args.build or args.force_rebuild
        
        if not should_build:
            # Check if knowledge base already exists
            if kb.is_built(args.repo_url):
                if not args.quiet:
                    print("📂 Loading existing knowledge base...")
                
                success = kb.load(
                    repo_url_or_path=args.repo_url,
                    repo_type=args.type,
                    access_token=args.access_token
                )
                
                if not success:
                    print("❌ Failed to load existing knowledge base. Trying to build...")
                    should_build = True
            else:
                if not args.quiet:
                    print("🔍 No existing knowledge base found. Building new one...")
                should_build = True
        
        # Build the knowledge base if needed
        if should_build:
            if not args.quiet:
                print("🔨 Building knowledge base... This may take a few minutes.")
            
            success = kb.build(
                repo_url_or_path=args.repo_url,
                repo_type=args.type,
                access_token=args.access_token,
                excluded_dirs=args.excluded_dirs,
                excluded_files=args.excluded_files, 
                included_dirs=args.included_dirs,
                included_files=args.included_files,
                force_rebuild=args.force_rebuild
            )
            
            if not success:
                print("❌ Failed to build knowledge base. Please check the logs and try again.")
                return 1
            
            if not args.quiet:
                print("✅ Knowledge base built successfully!")
        
        # Start interactive Q&A loop
        interactive_qa_loop(kb, args.repo_url)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ An unexpected error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 