import urllib.parse
import tiktoken
import PyPDF2
import io
import streamlit as st
import textwrap
import re, json
from pydantic import BaseModel



def count_tokens(text):
    """Count tokens using tiktoken, fallback to simple estimation"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        return len(text) // 4


def process_pdf(uploaded_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)

        return "\n\n".join(text_parts)
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def format_source_title(content, prefix="📝", max_length=60):
    """Format source title with emoji prefix and length limit"""
    return f"{prefix} {content[:max_length]}..."


def create_download_button(label, data, file_name_prefix, key_suffix,
                           use_container_width=False, is_primary=False):
    """Create a download button with consistent styling"""
    st.download_button(
        label=label,
        data=data,
        file_name=f"{file_name_prefix.lower().replace(' ', '_')}_{key_suffix}.md",
        mime="text/markdown",
        key=f"download_{key_suffix.replace(' ', '_')}_{file_name_prefix.replace(' ', '_')}",
        use_container_width=use_container_width,
        type="primary" if is_primary else "secondary"
    )


def combine_sources(sources):
    """Combine all source contents with separators"""
    return "\n\n--- Source Separator ---\n\n".join(
        [f"Source {i + 1}:\n{s['content']}" for i, s in enumerate(sources)]
    )


def strip_code_fences(text: str) -> str:
    """
    Remove leading / trailing triple-backtick blocks like
    ```markdown … ``` or ```dot … ```
    and return the inner payload.
    """
    pattern = re.compile(r"```[a-zA-Z0-9]*\s*\n(.+?)```", re.DOTALL)
    m = pattern.search(text)
    cleaned = m.group(1) if m else text
    return textwrap.dedent(cleaned).strip()



def render_dot_quickchart(raw: str, width: int = 700):
    """
    Show a DOT graph via QuickChart GraphViz PNG.
    """
    # 1. Strip ``` fences or stray labels
    dot = re.sub(r"```[a-zA-Z0-9]*\s*\n(.+?)```", r'\1', raw, flags=re.DOTALL).strip()
    dot = textwrap.dedent(dot)

    # 2. If the agent still used 'A --> B' Mermaid arrows, convert them
    if "-->" in dot and "digraph" not in dot:
        edges = re.sub(r'"?([^"]+)"?\s*-->\s*"?([^"]+)"?', r'\1 -> \2;', dot)
        dot = f"digraph {{\n{edges}\n}}"

    # 3. Build API URL
    encoded = urllib.parse.quote_plus(dot)
    url = f"https://quickchart.io/graphviz?format=png&graph={encoded}"

    st.image(url, width=width)


# ------------------------------------------------------------------
# UNIVERSAL RESPONSE NORMALISER
# ------------------------------------------------------------------
def normalise_payload(analysis_type: str, raw):
    """
    Devuelve un string limpio para el front-end.
    """
    if isinstance(raw, BaseModel):
        raw = raw.model_dump_json()

    text = str(raw)
    text = re.sub(r"^```[a-zA-Z0-9]*\s*\n|\n```$", "", text, flags=re.S).strip()

    # 2.  Quiz mantiene su lógica especial
    if analysis_type == "📝 Knowledge Check":
        # Already JSON? great
        if text.lstrip().startswith("{"):
            return text
        # Looks like a Pydantic repr → eval and dump
        if text.startswith("Quiz("):
            try:
                obj = eval(text, {}, {})          # safe: no globals, locals
                if isinstance(obj, BaseModel):
                    return obj.model_dump_json()
            except Exception:
                pass
        # If nothing worked we fall through – UI will warn.

    if text.lstrip().startswith("{"):
        try:
            obj = json.loads(text)
            if "result" in obj:
                return obj["result"]
            if "csv" in obj:
                return obj["csv"]
        except json.JSONDecodeError:
            pass

    return text

