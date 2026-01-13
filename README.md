# `dir2chat`

Generate an OpenAI Chat Completions-compatible JSON from all UTF-8 plaintext files in a directory.

## Use Cases

This tool is designed to help with a variety of tasks involving directory contents and large-language models, such as:

- **Codebase Summarization for LLMs**  
  Preparing a repository as an input for Chat Completions-compatible models, making it easy to "upload" a codebase as a
  conversational context.

- **Automated Project Documentation**  
  Quickly gather all plaintext documentation files (like `README.md`, `docs/`, etc.) and their contents for further
  summarization, analysis, or indexing.

## Installation

```
pip install dir2chat
```

## Usage

```
python -m dir2chat <directory> [options]
```

Options:

- `-o`, `--output`: Output JSON file (default: `-` for stdout).
- `--max-file-size`: Max size for files in bytes (default: `65536`, or 64 KB).

Example:

```bash
python -m dir2chat path/to/my/project -o chat.json --max-file-size 32768
```

## Output

The output is a JSON array of messages suitable for OpenAI Chat models, in the structure:

```
[
  {
    "role": "user",
    "content": "- README.md\n- src/\n  - main.py\n  - utils.py"
  },
  {
    "role": "user",
    "content": "README.md"
  },
  {
    "role": "user",
    "content": "<contents of README.md>"
  },
  ...
]
```

1. First message: The tree view of the directory.
2. Subsequent pairs: For each included file, a message with the file's relative path, then another with its content.

> **Only UTF-8-encoded, plaintext files below the size limit are included.** Skipped files are reported to stderr.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
