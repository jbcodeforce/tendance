
"""
Simple Tendance Taipy Application - Testing Version

A simplified version to test Taipy integration before building the full app.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from taipy.gui import Gui
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)

# Module-level variables (required by Taipy)
available_datasets = []
selected_dataset = ""
dataset_info = "Welcome! No dataset loaded yet."
questions_df = pd.DataFrame()
current_message = ""
chat_display = "Welcome! Ask me about Apache Flink."
dataset_count = 0

# App context for callbacks
_output_directory = "./output"


def _scan_datasets(output_directory: str) -> List[str]:
    """Scan for available JSON datasets"""
    output_dir = Path(output_directory)
    if not output_dir.exists():
        return []
    
    json_files = list(output_dir.glob("*.json"))
    dataset_names = []
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if it's a Tendance dataset
            if 'metadata' in data and 'questions' in data:
                dataset_names.append(file_path.stem)
                
        except Exception:
            pass
    
    return sorted(dataset_names)


def _load_dataset(dataset_name: str) -> None:
    """Load a specific dataset"""
    global dataset_info, questions_df
    
    file_path = Path(_output_directory) / f"{dataset_name}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract basic info
        stats = data.get('statistics', {})
        metadata = data.get('metadata', {})
        
        dataset_info = f"Dataset: {dataset_name} | Questions: {stats.get('total_questions', 0)} | Answered: {stats.get('answered_questions', 0)} | Avg Score: {stats.get('score_statistics', {}).get('average', 0):.1f}"
        
        # Convert questions to DataFrame
        questions = data.get('questions', [])
        df_data = []
        
        for q in questions:
            df_data.append({
                'ID': q.get('question_id', ''),
                'Title': q.get('title', '')[:80] + ('...' if len(q.get('title', '')) > 80 else ''),
                'Score': q.get('score', 0),
                'Views': q.get('view_count', 0),
                'Answers': q.get('answer_count', 0),
                'Answered': '✅' if q.get('is_answered', False) else '❌',
            })
        
        questions_df = pd.DataFrame(df_data)
        logger.info(f"Loaded dataset: {dataset_name} with {len(df_data)} questions")
        
    except Exception as e:
        logger.error(f"Failed to load dataset {dataset_name}: {e}")
        dataset_info = f"Error loading dataset: {dataset_name}"
        questions_df = pd.DataFrame()


def on_dataset_change(state):
    """Handle dataset selection change"""
    global dataset_info, questions_df
    if hasattr(state, 'selected_dataset') and state.selected_dataset:
        _load_dataset(state.selected_dataset)
        state.dataset_info = dataset_info
        state.questions_df = questions_df


def on_send_message(state):
    """Handle chat message sending"""
    global chat_display
    if hasattr(state, 'current_message') and state.current_message.strip():
        user_msg = state.current_message.strip()
        
        # Simple mock responses
        if 'hello' in user_msg.lower() or 'hi' in user_msg.lower():
            bot_response = "👋 Hello! I'm your Flink assistant. I can help with Apache Flink questions!"
        elif 'flink' in user_msg.lower():
            bot_response = "Apache Flink is a powerful stream processing framework. What specific aspect would you like to know about?"
        elif 'help' in user_msg.lower():
            bot_response = "I can help you with:\n• Flink concepts\n• Stream processing\n• Window operations\n• Watermarks\n\nWhat interests you?"
        else:
            bot_response = f"Interesting question about '{user_msg}'. The full RAG system will provide detailed answers based on Stack Exchange data!"
        
        # Update chat display
        if chat_display == "Welcome! Ask me about Apache Flink.":
            chat_display = ""
        
        new_chat = f"You: {user_msg}\n\nFlink Assistant: {bot_response}"
        if chat_display:
            chat_display = f"{chat_display}\n\n---\n\n{new_chat}"
        else:
            chat_display = new_chat
            
        state.chat_display = chat_display
        state.current_message = ""


# Define the page at module level with proper Taipy syntax
page = """
# 🔍 Tendance Analytics

## Dataset Information

<|text|>Dataset Count: {dataset_count}</|text|>

<|text|>{dataset_info}</|text|>

<|{questions_df}|table|>
"""


def run_taipy_app(host: str = "localhost", port: int = 8501):
    """Run the Taipy application at module level"""
    logger.info(f"Starting Taipy app on {host}:{port}")
    logger.info(f"Available datasets: {available_datasets}")
    
    # Create GUI and pass variables explicitly
    gui = Gui(page)
    gui.run(
        host=host,
        port=port,
        debug=True,
        title="Tendance - Stack Exchange Analytics",
        dataset_count=dataset_count,
        dataset_info=dataset_info,
        questions_df=questions_df,
        available_datasets=available_datasets,
        selected_dataset=selected_dataset,
        current_message=current_message,
        chat_display=chat_display
    )


class SimpleTendanceApp:
    """Simple Tendance Taipy Application for testing"""
    
    def __init__(self, output_directory: str = "./output", host: str = "localhost", port: int = 8501):
        global _output_directory, available_datasets, selected_dataset, dataset_count
        
        self.host = host
        self.port = port
        _output_directory = output_directory
        
        # Initialize state
        available_datasets = _scan_datasets(output_directory)
        selected_dataset = available_datasets[0] if available_datasets else ""
        dataset_count = len(available_datasets)
        
        # Load first dataset if available
        if selected_dataset:
            _load_dataset(selected_dataset)
    
    def run(self):
        """Run the simple Taipy application"""
        run_taipy_app(self.host, self.port)
