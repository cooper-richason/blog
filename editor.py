"""This script creates a Streamlit app for managing blog posts, allowing users to create, update, and delete posts, as well as manage associated files."""

import streamlit as st
from editor_utils import *
from time import sleep
import yaml

st.set_page_config(layout="wide", page_title="Blog Post Editor", page_icon=":pencil:")

st.title("""Manage Blog Posts""")
st.markdown("This is a simple streamlit app designed to make it easier to manage a quarto blog. It helps with things like creating new posts, updating existing posts, and managing files related to those posts. \n\n **Note:** This is a work in progress and is not yet fully functional. If you have any suggestions or issues, please open an issue on the [GitHub repository](https://github.com/cooper-richason/blog)")
selected_post = st.selectbox('Select Post',list_posts(),index=None)

st.divider()
col1, col2= st.columns([8,2],gap='large')

with col1:
    st.markdown(""" ### Update Post:""")
    if selected_post:
        config_yml, post_text = read_post(selected_post)

        # Display in Streamlit with a text area
        updated_yaml_text = st.text_area("**Edit YAML**", pretty_print_yaml(config_yml), height=150)
        updated_text = st.text_area('**Update Post**',post_text,height=500)

        if st.button("Save Changes",type="primary",use_container_width=True):
            update_post(selected_post, yaml.safe_load(updated_yaml_text), updated_text)
            sleep(2) # Just so the user can read the msg
            st.rerun()

with col2:
    @st.dialog("Create New Post")
    def create_post():
        st.markdown(f"""Please enter a name for the new post. This will create a new directory in the `posts` folder with the name you provide. \n\n **Otherwise, click the X in the corner to cancel.**""")
        with st.form(key='create_post',clear_on_submit=True):
            post_name = st.text_input('Post Name')

            if st.form_submit_button(label='Create',type='primary'):
                create_new_post(post_name)
                sleep(1) # Just so the user can read the msg
                st.rerun()

    @st.dialog("Upload Image")
    def upload_image():
        st.markdown(f"""If you would like to upload an image to this post, please select the image file and enter a custom name for the file. \n\n **Otherwise, click the X in the corner to cancel.**""")
        with st.form(key='upload_image',clear_on_submit=True):
            uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

            # Custom file name input
            custom_name = st.text_input("Enter a name for the file (without extension):")
            custom_name = custom_name.replace(' ','_')

            if st.form_submit_button(label='Create',type='primary'):
                saved_path = save_uploaded_file(uploaded_file, selected_post, custom_name.strip())
                if saved_path:
                    st.success(f"✅ File uploaded successfully to: `{saved_path}`")
                    st.image(saved_path, caption="Uploaded Image", use_column_width=True)
                    sleep(5) # Just so the user can see the image
                    st.rerun()
                else:
                    st.error("⚠️ Error uploading file. Please try again.")

    @st.dialog("Edit Post Files",width='large')
    def edit_post_files():
        for file in get_post_content(selected_post):
            col1,col2 = st.columns(2)
            with col1:
                st.write(file)
            with col2:
                if st.button('Delete File',key=f'delete_{file}'):
                    delete_file(selected_post,file)
                    st.success(f"✅ File deleted: `{file}`")
                    sleep(2) # Just so the user can read the msg
                    st.rerun()


    @st.dialog("Are you sure?")
    def delete_post_dialog():
        st.markdown('You are about to delete all of the files related to this post. This action **cannot be undone**.  \n\n **Otherwise, click the X in the corner to cancel.**')
        
        col1,col2 = st.columns(2)
        with col1:
            if st.button('Delete Post',key='delete_post',use_container_width=True):
                delete_post(selected_post)
                st.success(f"✅ Post deleted: `{selected_post}`")
                sleep(2) # Just so the user can read the msg
                st.rerun()
        with col2:
            if st.button('Cancel',type='primary',use_container_width=True):
                st.rerun()


    st.markdown("""### Actions:""")
    col1, col2 = st.columns(2)
    
    with col1: 
        if st.button('Create New Post',on_click=create_post,use_container_width=True): pass
    with col2: 
        if st.button('Delete Post',on_click=delete_post_dialog,use_container_width=True): pass
    if selected_post:
        #st.markdown(""" #### Files Related to Post:""")
        col1, col2 = st.columns(2)
        with col1: 
            if st.button('Upload Image',use_container_width=True): upload_image()
        with col2:
            if st.button('Edit Files',use_container_width=True): edit_post_files()
        st.markdown(' ‎ \n\n##### Current Files:')
        st.write(get_post_content(selected_post))
