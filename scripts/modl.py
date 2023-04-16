import gradio as gr
import os
import sys
import shutil
import requests
import modules
from modules import script_callbacks

def on_ui_tabs():

    def download_models(selected_models):
        # Check if there is enough disk space
        total_size = sum(model["size"] for model in selected_models)
        available_space = shutil.disk_usage(".").free
        if total_size > available_space:
            return f"Not enough disk space. Required: {total_size/1024/1024:.2f} MB, Available: {available_space/1024/1024:.2f} MB"

        # Download the selected models
        for model in selected_models:
            filename = os.path.basename(model["url"])
            path = os.path.join("extensions", "sd-webui-controlnet", "models", filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            response = requests.get(model["url"], stream=True)
            with open(path,"wb") as f:
                shutil.copyfileobj(response.raw, f)
            del response
        return "All models downloaded successfully"


    def get_models():
        # Load the models list from the repo

        rep_file = os.path.join("extensions", "sd-webui-modl", "models.txt")
        with open(rep_file, "r") as f:
            modelist = f.read()

        # Parse the models list
        models = []
        for line in modelist.split("\n"):
            if line.strip() == "":
                continue
            model_name, model_url = line.strip().split(",")
            models.append({"name": model_name.strip(), "url": model_url.strip()})

            # Get file size
            size_request = requests.head(model_url.strip())
            size = int(size_request.headers.get("content-length", 0))
            models[-1]["size"] = size

        return models



    models = get_models()
    if models is None:
        print("Error fetching models list from repo")
    else:
        with gr.Blocks(analytics_enabled=False) as modl:
            with gr.Box(elem_classes="modl_box"):
                with gr.Column():
                    gr.Markdown("### Choose models to download")
                    checkboxes = gr.Dropdown(multiselect=True, label="Controlnet models", choices=[(model["name"]) for model in models], value=[])
                    download_button = gr.Button(value="Download")
                    output_text = gr.Textbox(label="Result") 

                    def process_download(selected_models):
                        selected_model_dicts = [model for model in models if model["name"] in selected_models]
                        result = download_models(selected_model_dicts)

                    download_button.click(process_download, inputs=[checkboxes], outputs=[output_text])
        
    return (modl , "MoDL", "modl"),
script_callbacks.on_ui_tabs(on_ui_tabs)
