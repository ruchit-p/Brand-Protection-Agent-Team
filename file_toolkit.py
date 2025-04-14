"""
File Toolkit for Agno Agent

This toolkit enables the agent to interact with the local file system,
allowing it to read from and write to files, as well as list files
in a directory.
"""

import os
import json
import csv
import datetime
from typing import List, Dict, Any, Optional
from agno.tools import Toolkit

class FileTools(Toolkit):
    """
    Toolkit for file system operations, allowing the agent to read, write,
    and list files.
    """

    def __init__(self, base_directory: Optional[str] = None):
        """
        Initialize the File Toolkit.
        
        Args:
            base_directory: Optional base directory to restrict file operations
                           (defaults to storage directory if None)
        """
        super().__init__(name="file_tools")
        
        # Set base directory for file operations - hardcoded to the storage folder
        self.base_directory = "/Users/ruchitpatel/Projects/agnoagent/storage"
        
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_directory, exist_ok=True)
        
        # Register the file operation functions
        self.register(self.read_file)
        self.register(self.save_file)
        self.register(self.list_files)
        self.register(self.read_csv)
        self.register(self.save_csv)
        self.register(self.read_json)
        self.register(self.save_json)
    
    def _resolve_path(self, file_path: str) -> str:
        """
        Resolve a given file path to ensure it's within the base directory.
        
        Args:
            file_path: The file path to resolve
            
        Returns:
            The resolved absolute file path
        """
        # If the path is absolute, check if it's within the base directory
        if os.path.isabs(file_path):
            if not file_path.startswith(self.base_directory):
                raise ValueError(f"Access denied: File path must be within {self.base_directory}")
            return file_path
        
        # Otherwise, join with the base directory
        return os.path.join(self.base_directory, file_path)
    
    def read_file(self, file_path: str) -> str:
        """
        Read content from a text file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Content of the file as a string
        """
        resolved_path = self._resolve_path(file_path)
        
        try:
            with open(resolved_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            return f"Successfully read file: {file_path}\n\nContent:\n{content}"
        except FileNotFoundError:
            return f"Error: File not found - {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def save_file(self, file_path: str, content: str, overwrite: bool = True) -> str:
        """
        Save content to a text file.
        
        Args:
            file_path: Path where to save the file
            content: Content to write to the file
            overwrite: Whether to overwrite the file if it exists
            
        Returns:
            Result message
        """
        resolved_path = self._resolve_path(file_path)
        
        # Check if file exists and overwrite is disabled
        if os.path.exists(resolved_path) and not overwrite:
            return f"Error: File {file_path} already exists and overwrite=False"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            
            # Write content to file
            with open(resolved_path, "w", encoding="utf-8") as file:
                file.write(content)
            
            return f"Successfully saved content to file: {file_path}"
        except Exception as e:
            return f"Error saving file: {str(e)}"
    
    def list_files(self, directory: str = "", show_full_path: bool = False) -> str:
        """
        List files in a directory relative to the base directory.
        
        Args:
            directory: Subdirectory to list (relative to base_directory)
            show_full_path: Whether to show full paths or just filenames
            
        Returns:
            List of files in the directory
        """
        target_dir = self._resolve_path(directory) if directory else self.base_directory
        
        try:
            # Get all files in the directory
            if os.path.isdir(target_dir):
                files = os.listdir(target_dir)
                
                # Format the results
                if not files:
                    return f"No files found in {directory or 'storage directory'}"
                
                result = f"Files in {directory or 'storage directory'}:\n\n"
                for item in sorted(files):
                    item_path = os.path.join(target_dir, item)
                    if os.path.isdir(item_path):
                        item_type = "📁 "  # Folder icon
                    else:
                        item_type = "📄 "  # File icon
                    
                    if show_full_path:
                        result += f"{item_type} {os.path.join(target_dir, item)}\n"
                    else:
                        result += f"{item_type} {item}\n"
                
                return result
            else:
                return f"Error: {directory} is not a valid directory"
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def read_csv(self, file_path: str, has_header: bool = True) -> str:
        """
        Read content from a CSV file and return it in a structured format.
        
        Args:
            file_path: Path to the CSV file
            has_header: Whether the CSV file has a header row
            
        Returns:
            Formatted representation of the CSV data
        """
        resolved_path = self._resolve_path(file_path)
        
        try:
            with open(resolved_path, "r", encoding="utf-8", newline="") as file:
                csv_reader = csv.reader(file)
                data = list(csv_reader)
            
            if not data:
                return f"Successfully read CSV file: {file_path}, but it contains no data"
            
            # Format the CSV data for display
            result = f"Successfully read CSV file: {file_path}\n\n"
            
            if has_header:
                headers = data[0]
                rows = data[1:]
                
                # Create a table with headers
                result += "| " + " | ".join(headers) + " |\n"
                result += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                
                # Add rows
                for row in rows:
                    result += "| " + " | ".join(row) + " |\n"
            else:
                # Create a table without headers
                for row in data:
                    result += "| " + " | ".join(row) + " |\n"
            
            return result
        except FileNotFoundError:
            return f"Error: CSV file not found - {file_path}"
        except Exception as e:
            return f"Error reading CSV file: {str(e)}"
    
    def save_csv(self, file_path: str, data: List[List[str]], overwrite: bool = True) -> str:
        """
        Save data to a CSV file.
        
        Args:
            file_path: Path where to save the CSV file
            data: List of rows, where each row is a list of values
            overwrite: Whether to overwrite the file if it exists
            
        Returns:
            Result message
        """
        resolved_path = self._resolve_path(file_path)
        
        # Check if file exists and overwrite is disabled
        if os.path.exists(resolved_path) and not overwrite:
            return f"Error: File {file_path} already exists and overwrite=False"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            
            # Write data to CSV file
            with open(resolved_path, "w", encoding="utf-8", newline="") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerows(data)
            
            return f"Successfully saved data to CSV file: {file_path}"
        except Exception as e:
            return f"Error saving CSV file: {str(e)}"
    
    def read_json(self, file_path: str) -> str:
        """
        Read content from a JSON file and return it in a structured format.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Formatted representation of the JSON data
        """
        resolved_path = self._resolve_path(file_path)
        
        try:
            with open(resolved_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            # Format the JSON data for display
            formatted_json = json.dumps(data, indent=2)
            return f"Successfully read JSON file: {file_path}\n\nContent:\n```json\n{formatted_json}\n```"
        except FileNotFoundError:
            return f"Error: JSON file not found - {file_path}"
        except json.JSONDecodeError:
            return f"Error: {file_path} contains invalid JSON"
        except Exception as e:
            return f"Error reading JSON file: {str(e)}"
    
    def save_json(self, file_path: str, data: Any, pretty: bool = True, overwrite: bool = True) -> str:
        """
        Save data to a JSON file.
        
        Args:
            file_path: Path where to save the JSON file
            data: Data to save as JSON
            pretty: Whether to format the JSON with indentation
            overwrite: Whether to overwrite the file if it exists
            
        Returns:
            Result message
        """
        resolved_path = self._resolve_path(file_path)
        
        # Check if file exists and overwrite is disabled
        if os.path.exists(resolved_path) and not overwrite:
            return f"Error: File {file_path} already exists and overwrite=False"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            
            # Write data to JSON file
            with open(resolved_path, "w", encoding="utf-8") as file:
                if pretty:
                    json.dump(data, file, indent=2)
                else:
                    json.dump(data, file)
            
            return f"Successfully saved data to JSON file: {file_path}"
        except Exception as e:
            return f"Error saving JSON file: {str(e)}"
