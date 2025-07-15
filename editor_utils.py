"""This module provides utility functions for managing blog posts in the Streamlit editor"""

import streamlit as st
import os, yaml, json, shutil, re
from pathlib import Path
from datetime import datetime
import pytz

ct_timezone = pytz.timezone('America/Chicago')

__all__ = ['list_posts', 'get_post_content', 'read_post','update_post','get_directory_files','read_quarto_document', 'update_quarto_document','pretty_print_yaml', 'create_new_post', 'save_uploaded_file','delete_file','delete_post']

base_path = os.getcwd()

def list_posts():
    post_path = os.path.join(base_path,'posts')

    if not os.path.exists(post_path):
        print(f"⚠️ Post directory '{post_path}' does not exist. Skipping sync.")
        return

    post_directories = [f for f in os.listdir(post_path) if os.path.isdir(os.path.join(post_path, f))]
    return post_directories


def get_directory_files(folder_path = base_path):

    if not os.path.exists(folder_path):
        print(f"⚠️ Post directory '{folder_path}' does not exist. Skipping sync.")
        return

    post_content = os.listdir(folder_path)
    return post_content

def get_post_content(post):
    return get_directory_files(os.path.join(base_path,'posts', post))

def read_quarto_document(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expression to match the YAML header
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)

    if not match:
        raise ValueError("Invalid Quarto document format: Missing or incorrect YAML metadata")

    yaml_content, markdown_content = match.groups()

    # Parse YAML metadata safely
    yaml_data = yaml.safe_load(yaml_content)
    text_data = markdown_content.strip()  # Trim any extra whitespace

    return yaml_data, text_data

def read_post(post):
    post_files = get_post_content(post)
    qmd_file = [f for f in post_files if f.endswith('.qmd')][0]
    post_path = os.path.join(base_path,'posts', post, qmd_file)
    return read_quarto_document(post_path)


def update_quarto_document(path, yaml_data, text_data,message=True):
    """
    Updates a Quarto (.qmd) document with new YAML metadata and text content.

    Parameters:
        file_path (str): The path to the Quarto document.
        yaml_data (dict): The updated YAML metadata.
        text_data (str): The updated markdown content.

    Returns:
        None (writes updates to the file).
    """
    try:
        yaml_data['date-modified'] = datetime.now(ct_timezone).strftime('%Y-%m-%d')
        # Convert the dictionary to a properly formatted YAML string
        yaml_str = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)

        # Construct the new file content
        new_content = f"---\n{yaml_str}---\n\n{text_data.strip()}\n"
        
        # Write the updated content back to the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    except Exception as e:
        st.error(f"Error updating Quarto document: {e}")
    else:
        if message: st.success("Post updated successfully!")

def update_post(post, yaml_data, text_data,message=True):
    """
    Updates a Quarto (.qmd) document with new YAML metadata and text content.

    Parameters:
        file_path (str): The path to the Quarto document.
        yaml_data (dict): The updated YAML metadata.
        text_data (str): The updated markdown content.

    Returns:
        None (writes updates to the file).
    """

    post_files = get_post_content(post)
    qmd_file = [f for f in post_files if f.endswith('.qmd')][0]
    file_path = os.path.join(base_path,'posts', post, qmd_file)
    update_quarto_document(file_path, yaml_data, text_data,message)


def pretty_print_yaml(yaml_data):
    """Convert a YAML dictionary to a nicely formatted string for editing."""
    return yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, indent=4)

def _next_post_number():
    post_directories = list_posts()

    # Extract numbers before the dash
    numbers = []
    for directory in post_directories:
        match = re.match(r'^(\d+)-', directory)  # Matches "XX- Name"
        if match:
            numbers.append(int(match.group(1)))  # Convert to integer

    max_number = max(numbers) if numbers else 0  # Get max number or default to 0
    return max_number + 1  # Return the next number

def _new_post_data(post,post_name):
    yaml, text = read_post(post)
    yaml['date'] = datetime.now(ct_timezone).strftime('%Y-%m-%d')
    yaml['title'] = post_name
    update_post(post, yaml, text, message=False)


def create_new_post(post_name, template_dir=os.path.join(base_path,'posts',"template")):
    create_success = False
    try:
        post_number = _next_post_number()
        post_directory = f"{post_number}- {post_name}"
        post_path = os.path.join(base_path,'posts', post_directory)
        
        # Ensure template exists before copying
        template_path = Path(template_dir)
        if not template_path.exists():
            print(f"⚠️ Template directory '{template_path}' does not exist. Cannot create new post.")
            return None

        # Copy the template to the new post directory
        shutil.copytree(template_path, post_path)
        create_success = True
    except Exception as e:
        st.error(f"⚠️ Error creating new post:': {e}")
        print(f"⚠️ Error creating new post: {e}")

    if create_success:
        try:
            _new_post_data(post_directory,post_name)
        except Exception as e:
            print(f"⚠️ Error updating new post: {e}")
        else:
            st.success("New post created successfully!")
            print(f"✅ New post created: {post_name}")

def save_uploaded_file(uploaded_file, post_file, custom_name):
    """Save the uploaded file to the selected post directory with a custom name"""
    post_path = Path(os.path.join(base_path,'posts', post_file))

    if not post_path.exists():
        st.error(f"⚠️ Post directory '{post_file}' does not exist!")
        return None

    # Get file extension
    file_extension = Path(uploaded_file.name).suffix

    # Use the custom name if provided, otherwise use the original filename
    file_name = f"{custom_name}{file_extension}" if custom_name else uploaded_file.name
    file_path = post_path / file_name

    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def delete_file(selected_post,selected_file):
    file_path = Path(os.path.join(base_path,'posts', selected_post, selected_file))
    try:
        os.remove(file_path)
    except OSError as e:
        st.error(f"⚠️ Error deleting file '{file_path}': {e}")

def delete_post(selected_post):
    post_path = os.path.join(base_path,'posts', selected_post)
    try:
        shutil.rmtree(post_path)
    except OSError as e:
        st.error(f"⚠️ Error deleting post '{post_path}': {e}")