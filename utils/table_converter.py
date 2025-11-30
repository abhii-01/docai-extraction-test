"""
Table conversion utilities for Document AI Layout Parser
Converts tables to markdown and narrative paragraphs using LLM
"""

import os
from typing import List, Optional
from dotenv import load_dotenv


def table_to_markdown(table_data: List[List[str]]) -> str:
    """
    Convert 2D table data to markdown format
    
    Args:
        table_data: 2D list of cell values (rows x columns)
        
    Returns:
        Markdown formatted table string
    """
    if not table_data or len(table_data) == 0:
        return ""
    
    markdown_lines = []
    
    # Header row
    header = "| " + " | ".join(table_data[0]) + " |"
    markdown_lines.append(header)
    
    # Separator row
    separator = "| " + " | ".join(["---"] * len(table_data[0])) + " |"
    markdown_lines.append(separator)
    
    # Data rows
    for row in table_data[1:]:
        row_str = "| " + " | ".join(row) + " |"
        markdown_lines.append(row_str)
    
    return "\n".join(markdown_lines)


def detect_table_type(table_data: List[List[str]]) -> str:
    """
    Detect the type of table using heuristics
    
    Args:
        table_data: 2D list of cell values
        
    Returns:
        One of: "comparison", "time-series", "summary", "data"
    """
    if not table_data or len(table_data) < 2:
        return "data"
    
    # Check for time-series indicators in first column
    first_column = [row[0].lower() if row else "" for row in table_data]
    time_keywords = ['year', 'month', 'quarter', 'date', 'time', 'period', 'q1', 'q2', 'q3', 'q4']
    
    if any(keyword in " ".join(first_column) for keyword in time_keywords):
        return "time-series"
    
    # Check for comparison indicators (multiple similar columns)
    if len(table_data[0]) > 2:
        return "comparison"
    
    # Check for summary indicators (totals, averages)
    all_text = " ".join([" ".join(row) for row in table_data]).lower()
    summary_keywords = ['total', 'sum', 'average', 'mean', 'summary']
    
    if any(keyword in all_text for keyword in summary_keywords):
        return "summary"
    
    return "data"


def table_to_narrative(markdown: str, method: str = "auto") -> str:
    """
    Convert markdown table to narrative paragraph using LLM
    
    Args:
        markdown: Markdown formatted table
        method: Table type hint ("comparison", "time-series", "summary", "auto")
        
    Returns:
        Narrative paragraph describing the table
    """
    load_dotenv()
    
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "openai":
        return _convert_with_openai(markdown, method)
    else:
        return _convert_with_anthropic(markdown, method)


def _convert_with_openai(markdown: str, method: str) -> str:
    """Convert table to narrative using OpenAI"""
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")
    
    client = OpenAI(api_key=api_key)
    
    prompt = _build_conversion_prompt(markdown, method)
    
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that converts tables to clear, readable narrative paragraphs. Preserve all key information from the table."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()


def _convert_with_anthropic(markdown: str, method: str) -> str:
    """Convert table to narrative using Anthropic Claude"""
    from anthropic import Anthropic
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    
    client = Anthropic(api_key=api_key)
    
    prompt = _build_conversion_prompt(markdown, method)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return response.content[0].text.strip()


def _build_conversion_prompt(markdown: str, method: str) -> str:
    """Build LLM prompt for table conversion"""
    
    type_instructions = {
        "comparison": "This is a comparison table. Describe the key differences and similarities between the entities being compared.",
        "time-series": "This is a time-series table. Describe the trends, changes, and patterns over time.",
        "summary": "This is a summary table. Describe the key statistics, totals, and aggregate information.",
        "data": "Describe the information presented in this table clearly and concisely.",
        "auto": "Analyze and describe the information in this table clearly and concisely."
    }
    
    instruction = type_instructions.get(method, type_instructions["auto"])
    
    prompt = f"""Convert the following markdown table into a clear, readable narrative paragraph.

{instruction}

Preserve all important numerical data, names, and relationships. Write in a flowing, natural style suitable for a textbook.

Table:
{markdown}

Narrative paragraph:"""
    
    return prompt


def extract_table_data(table, full_text):
    """
    Helper function to extract table data from Document AI table object
    (This is a compatibility function - actual extraction is done in notebooks)
    
    Args:
        table: Document AI table object
        full_text: Full document text
        
    Returns:
        2D list of cell values
    """
    cells_dict = {}
    max_row = 0
    max_col = 0
    
    # Extract all cells
    all_cells = []
    if hasattr(table, 'header_rows'):
        for row in table.header_rows:
            all_cells.extend(row.cells)
    if hasattr(table, 'body_rows'):
        for row in table.body_rows:
            all_cells.extend(row.cells)
    
    # Build cell grid
    for cell in all_cells:
        if not hasattr(cell, 'layout') or not cell.layout.text_anchor:
            continue
        
        row_idx = getattr(cell.layout, 'table_row_index', 0)
        col_idx = getattr(cell.layout, 'table_col_index', 0)
        
        # Get cell text
        text_parts = []
        for segment in cell.layout.text_anchor.text_segments:
            text = full_text[segment.start_index:segment.end_index]
            text_parts.append(text)
        
        cell_text = " ".join(text_parts).strip()
        cells_dict[(row_idx, col_idx)] = cell_text
        max_row = max(max_row, row_idx)
        max_col = max(max_col, col_idx)
    
    # Convert to 2D list
    if not cells_dict:
        return []
    
    table_data = []
    for row in range(max_row + 1):
        row_data = [cells_dict.get((row, col), "") for col in range(max_col + 1)]
        table_data.append(row_data)
    
    return table_data

