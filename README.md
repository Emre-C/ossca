# DeepWiki - Interactive Code Repository Q&A

DeepWiki is a powerful tool that creates queryable knowledge bases from code repositories. It allows you to ask questions about any codebase and get intelligent answers powered by AI.

## Features

- 🔍 **Repository Analysis**: Process GitHub, GitLab, Bitbucket repositories or local directories
- 🧠 **AI-Powered Q&A**: Ask questions about code in natural language
- 💾 **Persistent Knowledge Base**: Build once, query multiple times
- 🎯 **Smart Filtering**: Include/exclude specific files and directories
- 🌐 **Multi-Provider Support**: Google, OpenAI, OpenRouter, Ollama, Bedrock, Azure
- 💬 **Interactive Chat**: Conversation-aware responses with history

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/deepwiki.git
cd deepwiki
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up your AI provider API keys (choose one):
```bash
# For Google (default)
export GOOGLE_API_KEY="your-api-key"

# For OpenAI
export OPENAI_API_KEY="your-api-key"

# For OpenRouter
export OPENROUTER_API_KEY="your-api-key"

# For Azure
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"

# For AWS Bedrock
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="your-region"
```

## Quick Start

### Basic Usage

Build a knowledge base from a GitHub repository and start asking questions:

```bash
python main.py https://github.com/owner/repo --build
```

Load an existing knowledge base (if already built):

```bash
python main.py https://github.com/owner/repo
```

### Local Repository

Process a local repository:

```bash
python main.py /path/to/local/repo --build
```

### Custom AI Provider

Use OpenAI instead of Google:

```bash
python main.py https://github.com/owner/repo --provider=openai --build
```

## Command Line Options

```
usage: main.py [-h] [--build] [--force-rebuild] [--provider {google,openai,openrouter,ollama,bedrock,azure}]
               [--model MODEL] [--type {github,gitlab,bitbucket,local}] [--access-token ACCESS_TOKEN]
               [--excluded-dirs [EXCLUDED_DIRS ...]] [--excluded-files [EXCLUDED_FILES ...]]
               [--included-dirs [INCLUDED_DIRS ...]] [--included-files [INCLUDED_FILES ...]]
               [--verbose] [--quiet]
               repo_url

positional arguments:
  repo_url              Repository URL (GitHub, GitLab, Bitbucket) or local path

optional arguments:
  -h, --help            show this help message and exit
  --build               Force building of knowledge base (default: load existing if available)
  --force-rebuild       Force rebuild even if knowledge base already exists
  --provider {google,openai,openrouter,ollama,bedrock,azure}
                        AI model provider to use (default: google)
  --model MODEL         Specific model to use with the provider
  --type {github,gitlab,bitbucket,local}
                        Repository type (default: github)
  --access-token ACCESS_TOKEN
                        Access token for private repositories
  --excluded-dirs [EXCLUDED_DIRS ...]
                        Directories to exclude from processing
  --excluded-files [EXCLUDED_FILES ...]
                        File patterns to exclude from processing
  --included-dirs [INCLUDED_DIRS ...]
                        Directories to include exclusively
  --included-files [INCLUDED_FILES ...]
                        File patterns to include exclusively
  --verbose, -v         Enable verbose logging
  --quiet, -q           Suppress most output
```

## Usage Examples

### Private Repository

```bash
python main.py https://github.com/owner/private-repo --access-token=your-token --build
```

### Filter Specific Directories

Only process certain directories:

```bash
python main.py https://github.com/owner/repo --included-dirs src tests --build
```

Exclude certain directories:

```bash
python main.py https://github.com/owner/repo --excluded-dirs node_modules dist build --build
```

### Custom File Filtering

Include only Python files:

```bash
python main.py https://github.com/owner/repo --included-files "*.py" --build
```

Exclude log and temporary files:

```bash
python main.py https://github.com/owner/repo --excluded-files "*.log" "*.tmp" --build
```

### GitLab Repository

```bash
python main.py https://gitlab.com/owner/repo --type=gitlab --build
```

### Ollama (Local AI)

```bash
python main.py https://github.com/owner/repo --provider=ollama --build
```

## Interactive Commands

Once the knowledge base is loaded, you can use these commands in the interactive mode:

- **Ask any question**: Just type your question and press Enter
- **`help`** or **`h`** or **`?`**: Show help message
- **`clear`** or **`cls`**: Clear conversation history
- **`exit`** or **`quit`** or **`q`**: Exit the application

## Example Questions

Here are some example questions you can ask about a repository:

- "What is the main purpose of this project?"
- "How do I set up the development environment?"
- "What are the main components of the architecture?"
- "Show me how authentication works"
- "What are the available API endpoints?"
- "How do I run the tests?"
- "What dependencies does this project have?"
- "Explain the database schema"
- "How is error handling implemented?"
- "What design patterns are used in this codebase?"

## Configuration

DeepWiki uses configuration files in the `deepwiki/config/` directory. You can customize:

- **Model providers and settings**: Configure which AI models to use
- **Embedder settings**: Configure text embedding models
- **File filtering**: Set default exclusion/inclusion patterns

## Programmatic Usage

You can also use DeepWiki as a Python library:

```python
from deepwiki import KnowledgeBase

# Initialize knowledge base
kb = KnowledgeBase(provider="openai")

# Build from repository
success = kb.build("https://github.com/owner/repo", force_rebuild=True)

if success:
    # Ask questions
    answer, docs = kb.query("How does authentication work?")
    print(answer)
    
    # Add to conversation
    kb.add_conversation_turn("How does authentication work?", answer)
    
    # Ask follow-up questions
    follow_up, _ = kb.query("Can you show me the code for that?")
    print(follow_up)
```

## Architecture

The refactored DeepWiki consists of:

- **`KnowledgeBase`**: High-level API for building and querying knowledge bases
- **`RAG`**: Retrieval-Augmented Generation for answering questions
- **`DatabaseManager`**: Handles repository processing and vector storage
- **`main.py`**: Command-line interface

## Contributing

1. Follow the existing code patterns and styles
2. Add tests for new functionality
3. Use pytest for testing: `pytest test/`
4. Keep complexity low and architecture simple
5. Add proper logging and error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Make sure you've set the appropriate environment variable for your AI provider
2. **Permission Denied**: Use `--access-token` for private repositories
3. **Out of Memory**: Use filtering options to process smaller portions of large repositories
4. **Network Issues**: Check your internet connection and repository URL

### Getting Help

- Check the logs with `--verbose` flag for detailed error information
- Ensure all dependencies are installed correctly
- Verify your API keys are valid and have sufficient credits

### Performance Tips

- Use `--included-dirs` to focus on specific parts of large repositories
- Exclude unnecessary directories like `node_modules`, `build`, `dist`
- Knowledge bases are cached, so subsequent runs are much faster
- Consider using Ollama for local inference if you have sufficient hardware 