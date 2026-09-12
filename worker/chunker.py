"""
RepoMind AI — AST-Based Code Chunker
Splits source code into semantic chunks (functions, classes, methods)
rather than arbitrary character splits for better RAG retrieval.
"""

import ast
import re
import structlog
from typing import List
from dataclasses import dataclass, field

logger = structlog.get_logger(__name__)


@dataclass
class CodeChunk:
    """Represents a semantic unit of code."""
    chunk_type: str         # FUNCTION | CLASS | METHOD | MODULE | BLOCK
    name: str               # Function/class name
    content: str            # Actual code content
    start_line: int         # 1-indexed start line
    end_line: int           # 1-indexed end line
    language: str           # Source language
    metadata: dict = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────
#  Python AST Chunker
# ──────────────────────────────────────────────────────────────

def _chunk_python(content: str, file_path: str) -> List[CodeChunk]:
    """Parse Python code using the ast module for accurate chunking."""
    chunks = []
    lines = content.split("\n")

    try:
        tree = ast.parse(content)
    except Exception as e:
        logger.warning("ast_parse_failed", file=file_path, error=str(e))
        # Fallback: treat entire file as one chunk
        return [CodeChunk(
            chunk_type="MODULE",
            name=file_path.split("/")[-1],
            content=content,
            start_line=1,
            end_line=len(lines),
            language="python",
            metadata={"file_path": file_path, "parse_error": True},
        )]

    for node in ast.walk(tree):
        try:
            if isinstance(node, ast.ClassDef):
                start = node.lineno
                end = node.end_lineno or start
                chunk_content = "\n".join(lines[start - 1:end])

                chunks.append(CodeChunk(
                    chunk_type="CLASS",
                    name=node.name,
                    content=chunk_content,
                    start_line=start,
                    end_line=end,
                    language="python",
                    metadata={
                        "file_path": file_path,
                        "decorators": [
                            ast.dump(d) for d in node.decorator_list
                        ] if node.decorator_list else [],
                        "bases": [ast.dump(b) for b in node.bases] if node.bases else [],
                    },
                ))

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = node.end_lineno or start
                chunk_content = "\n".join(lines[start - 1:end])

                # Determine if this is a method (inside a class) or standalone function
                is_method = any(
                    isinstance(parent, ast.ClassDef)
                    for parent in ast.walk(tree)
                    if hasattr(parent, 'body') and node in getattr(parent, 'body', [])
                )

                parent_class = None
                for potential_parent in ast.walk(tree):
                    if isinstance(potential_parent, ast.ClassDef):
                        if node in potential_parent.body:
                            parent_class = potential_parent.name
                            break

                chunks.append(CodeChunk(
                    chunk_type="METHOD" if is_method else "FUNCTION",
                    name=node.name,
                    content=chunk_content,
                    start_line=start,
                    end_line=end,
                    language="python",
                    metadata={
                        "file_path": file_path,
                        "parent_class": parent_class,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            ast.dump(d) for d in node.decorator_list
                        ] if node.decorator_list else [],
                    },
                ))
        except Exception as e:
            logger.warning("ast_node_failed", node_type=type(node).__name__, error=str(e))
            continue

    # If no chunks found, treat as module-level code
    if not chunks:
        chunks.append(CodeChunk(
            chunk_type="MODULE",
            name=file_path.split("/")[-1],
            content=content,
            start_line=1,
            end_line=len(lines),
            language="python",
            metadata={"file_path": file_path},
        ))

    return chunks


# ──────────────────────────────────────────────────────────────
#  Java Regex Chunker
# ──────────────────────────────────────────────────────────────

# Regex patterns for Java constructs
_JAVA_CLASS_PATTERN = re.compile(
    r'^(?:(?:public|private|protected|abstract|final|static)\s+)*'
    r'(?:class|interface|enum|record)\s+(\w+)',
    re.MULTILINE
)

_JAVA_METHOD_PATTERN = re.compile(
    r'^[ \t]*(?:(?:public|private|protected|static|final|abstract|synchronized|native)\s+)*'
    r'(?:<[\w, ?]+>\s+)?'
    r'(?:\w[\w.<>,\[\] ?]*)\s+'
    r'(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w, ]+\s*)?[{;]',
    re.MULTILINE
)


def _chunk_java(content: str, file_path: str) -> List[CodeChunk]:
    """Parse Java code using regex-based pattern matching."""
    chunks = []
    lines = content.split("\n")

    # Find classes
    for match in _JAVA_CLASS_PATTERN.finditer(content):
        class_name = match.group(1)
        start_pos = match.start()
        start_line = content[:start_pos].count("\n") + 1

        # Find matching closing brace
        end_line = _find_closing_brace(lines, start_line - 1)

        chunk_content = "\n".join(lines[start_line - 1:end_line])
        chunks.append(CodeChunk(
            chunk_type="CLASS",
            name=class_name,
            content=chunk_content,
            start_line=start_line,
            end_line=end_line,
            language="java",
            metadata={"file_path": file_path},
        ))

    # Find methods
    for match in _JAVA_METHOD_PATTERN.finditer(content):
        method_name = match.group(1)

        # Skip common false positives
        if method_name in ("if", "for", "while", "switch", "catch", "return"):
            continue

        start_pos = match.start()
        start_line = content[:start_pos].count("\n") + 1
        end_line = _find_closing_brace(lines, start_line - 1)

        chunk_content = "\n".join(lines[start_line - 1:end_line])
        chunks.append(CodeChunk(
            chunk_type="METHOD",
            name=method_name,
            content=chunk_content,
            start_line=start_line,
            end_line=end_line,
            language="java",
            metadata={"file_path": file_path},
        ))

    if not chunks:
        chunks.append(CodeChunk(
            chunk_type="MODULE",
            name=file_path.split("/")[-1],
            content=content,
            start_line=1,
            end_line=len(lines),
            language="java",
            metadata={"file_path": file_path},
        ))

    return chunks


# ──────────────────────────────────────────────────────────────
#  JavaScript/TypeScript Regex Chunker
# ──────────────────────────────────────────────────────────────

_JS_FUNCTION_PATTERN = re.compile(
    r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
    re.MULTILINE
)

_JS_ARROW_PATTERN = re.compile(
    r'^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(?',
    re.MULTILINE
)

_JS_CLASS_PATTERN = re.compile(
    r'^(?:export\s+)?(?:default\s+)?class\s+(\w+)',
    re.MULTILINE
)


def _chunk_javascript(content: str, file_path: str) -> List[CodeChunk]:
    """Parse JavaScript/TypeScript code using regex patterns."""
    chunks = []
    lines = content.split("\n")

    # Classes
    for match in _JS_CLASS_PATTERN.finditer(content):
        class_name = match.group(1)
        start_pos = match.start()
        start_line = content[:start_pos].count("\n") + 1
        end_line = _find_closing_brace(lines, start_line - 1)

        chunks.append(CodeChunk(
            chunk_type="CLASS",
            name=class_name,
            content="\n".join(lines[start_line - 1:end_line]),
            start_line=start_line,
            end_line=end_line,
            language="javascript",
            metadata={"file_path": file_path},
        ))

    # Named functions
    for match in _JS_FUNCTION_PATTERN.finditer(content):
        func_name = match.group(1)
        start_pos = match.start()
        start_line = content[:start_pos].count("\n") + 1
        end_line = _find_closing_brace(lines, start_line - 1)

        chunks.append(CodeChunk(
            chunk_type="FUNCTION",
            name=func_name,
            content="\n".join(lines[start_line - 1:end_line]),
            start_line=start_line,
            end_line=end_line,
            language="javascript",
            metadata={"file_path": file_path},
        ))

    # Arrow functions / const assignments
    for match in _JS_ARROW_PATTERN.finditer(content):
        name = match.group(1)
        start_pos = match.start()
        start_line = content[:start_pos].count("\n") + 1
        end_line = _find_closing_brace(lines, start_line - 1)

        # Only include if it looks like a substantial function (>3 lines)
        if end_line - start_line >= 3:
            chunks.append(CodeChunk(
                chunk_type="FUNCTION",
                name=name,
                content="\n".join(lines[start_line - 1:end_line]),
                start_line=start_line,
                end_line=end_line,
                language="javascript",
                metadata={"file_path": file_path, "is_arrow": True},
            ))

    if not chunks:
        chunks.append(CodeChunk(
            chunk_type="MODULE",
            name=file_path.split("/")[-1],
            content=content,
            start_line=1,
            end_line=len(lines),
            language="javascript",
            metadata={"file_path": file_path},
        ))

    return chunks


# ──────────────────────────────────────────────────────────────
#  Generic Fallback Chunker
# ──────────────────────────────────────────────────────────────

def _chunk_generic(content: str, file_path: str, language: str) -> List[CodeChunk]:
    """
    Fallback chunker for unsupported languages.
    Splits by logical blocks (double newlines) with a max chunk size.
    """
    MAX_CHUNK_LINES = 80
    lines = content.split("\n")
    chunks = []

    if len(lines) <= MAX_CHUNK_LINES:
        return [CodeChunk(
            chunk_type="MODULE",
            name=file_path.split("/")[-1],
            content=content,
            start_line=1,
            end_line=len(lines),
            language=language,
            metadata={"file_path": file_path},
        )]

    # Split into blocks
    current_block = []
    block_start = 1

    for i, line in enumerate(lines, 1):
        current_block.append(line)

        is_boundary = (
            line.strip() == "" and
            len(current_block) >= 20
        ) or len(current_block) >= MAX_CHUNK_LINES

        if is_boundary:
            block_content = "\n".join(current_block)
            if block_content.strip():
                chunks.append(CodeChunk(
                    chunk_type="BLOCK",
                    name=f"{file_path.split('/')[-1]}:{block_start}-{i}",
                    content=block_content,
                    start_line=block_start,
                    end_line=i,
                    language=language,
                    metadata={"file_path": file_path},
                ))
            current_block = []
            block_start = i + 1

    # Remaining lines
    if current_block:
        block_content = "\n".join(current_block)
        if block_content.strip():
            chunks.append(CodeChunk(
                chunk_type="BLOCK",
                name=f"{file_path.split('/')[-1]}:{block_start}-{block_start + len(current_block)}",
                content=block_content,
                start_line=block_start,
                end_line=block_start + len(current_block) - 1,
                language=language,
                metadata={"file_path": file_path},
            ))

    return chunks


# ──────────────────────────────────────────────────────────────
#  Utilities
# ──────────────────────────────────────────────────────────────

def _find_closing_brace(lines: List[str], start_idx: int) -> int:
    """Find the line number of the matching closing brace."""
    brace_count = 0
    found_open = False

    for i in range(start_idx, len(lines)):
        for char in lines[i]:
            if char == "{":
                brace_count += 1
                found_open = True
            elif char == "}":
                brace_count -= 1

            if found_open and brace_count == 0:
                return i + 1  # 1-indexed

    return len(lines)  # Fallback: end of file


# ──────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────

# Language → chunker function mapping
_CHUNKERS = {
    "python": _chunk_python,
    "java": _chunk_java,
    "javascript": _chunk_javascript,
    "typescript": _chunk_javascript,  # Reuse JS chunker
}


def chunk_code(content: str, file_path: str, language: str) -> List[CodeChunk]:
    """
    Split source code into semantic chunks based on language.

    Uses AST parsing for Python, regex-based parsing for Java/JS/TS,
    and a generic block splitter for other languages.

    Args:
        content: Raw source code
        file_path: Relative path of the file
        language: Detected programming language

    Returns:
        List of CodeChunk objects
    """
    chunker = _CHUNKERS.get(language)

    if chunker:
        try:
            chunks = chunker(content, file_path)
            logger.debug(
                "chunking_complete",
                file=file_path,
                language=language,
                chunks=len(chunks),
            )
            return chunks
        except Exception as e:
            logger.warning(
                "chunker_fallback",
                file=file_path,
                language=language,
                error=str(e),
            )

    return _chunk_generic(content, file_path, language)
