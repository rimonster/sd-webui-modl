import gradio as gr
import os
import os.path
import time
import shutil
import urllib
import torch
import torch.hub
import math
import modules
from modules import script_callbacks
def on_ui_tabs():
    

    def format_bytes(size):
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0 : ' bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        return str (round(size,2)) + power_labels[n]

    def download_models(selected_models, progress=gr.Progress()):
        # Check if there is enough disk space
        total_size = sum(model["size"] for model in selected_models)
        available_space = shutil.disk_usage(".").free
        if total_size > available_space:
            return f"Not enough disk space. Required: {total_size/1024/1024:.2f} MB, Available: {available_space/1024/1024:.2f} MB"

        # Download the selected models
        for model in selected_models:
            filename = os.path.basename(model["url"])
            path = os.path.join(model["path"], filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            torch.hub.download_url_to_file(model["url"], path, progress=True)
        return "All models downloaded successfully"

    def get_models():
        # Load the models list from the repo
        rep_file = os.path.join("extensions", "sd-webui-modl", "models.txt")
        with open(rep_file, "r") as f:
            modelist = f.read()

        # Parse the models list
        models = []
        preloaded = []
        current_section = None
        for line in modelist.split("\n"):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("###"):
                break
            if not "http://" in line and not "https://" in line:
                current_section = line.split(",")
                continue
            model_name, model_url = line.split(",")
            model_path = current_section[1].strip()
            if os.path.isfile(model_path):
                filesize = os.stat(model_path).st_size
                preloaded.append({"name": model_name.strip(), "size": format_bytes(filesize)})
            else:
                req = urllib.request.Request(model_url.strip(), method='HEAD')
                try:
                    fl = urllib.request.urlopen(req)
                except:
                    continue
                if fl.status == 200:
                    size = int(fl.headers['Content-Length'])
                    name = model_name.strip() + " (" + format_bytes(size) + ")"
                    models.append({"section": current_section[0], "name": name, "url": model_url.strip(), "size": size, "path": model_path})

        return models, preloaded

    def update_sizes_table(*selected_models):
        sizes_data = []
        total_size = 0
        selected_models_flat = [model for sublist in selected_models for model in sublist]

        for model_name in selected_models_flat:
            model_dict = next(model for model in models if model["name"] == model_name)
            sizes_data.append([model_dict["name"], format_bytes(model_dict["size"])])
            total_size += model_dict["size"]

        available_space = shutil.disk_usage(".").free
        available_after_downloads = available_space - total_size

        sizes_data.append(["Total", format_bytes(total_size)])
        sizes_data.append(["Available Disk Space", format_bytes(available_space)])
        sizes_data.append(["Available After Downloads", format_bytes(available_after_downloads)])

        return sizes_data

    models_and_preloaded = get_models()
    models = models_and_preloaded[0]
    preloaded_models = models_and_preloaded[1]
    if models is None:
        print("Error fetching models list from repo")
    else:
        with gr.Blocks(analytics_enabled=False) as modl:
            with gr.Box(elem_classes="modl_box"):
                with gr.Column():
                    sizes_table = gr.Dataframe(headers=["Model", "Size"], datatype="str", type="array", col_count=2)
                with gr.Column():
                    gr.Markdown("### Choose models to download")
                    sections = []
                    for model in models:
                        if model["section"] not in sections:
                            sections.append(model["section"])
                    checkboxes = {}
                    for section in sections:
                        section_models = [model for model in models if model["section"] == section]
                        with gr.Row():
                            checkboxes[section] = gr.CheckboxGroup(choices=[model["name"] for model in section_models], label=section)
                            checkboxes[section].change(update_sizes_table, inputs=list(checkboxes.values()), outputs=[sizes_table])

                    download_button = gr.Button(value="Download")
                    output_text = gr.Textbox(label="Result")
#                    preloaded_models_table = gr.Dataframe(headers=["Downloaded Models", "Size"], datatype="str", type="array", col_count=2)
#                    preloaded_models_table.value = preloaded_models

                    def process_download(*selected_models, progress=gr.Progress()):
                        selected_model_dicts = []
                        for i, section in enumerate(sections):
                            section_models = [model for model in models if model["section"] == section]
                            for selected_model in selected_models[i]:
                                selected_model_dicts.append(next(model for model in section_models if model["name"] == selected_model))
                        result = download_models(selected_model_dicts, progress=progress)
#                        progress.close()
                        return result

                    download_button.click(process_download, inputs=list(checkboxes.values()), outputs=[output_text])


    return (modl, "MoDL", "modl"),
script_callbacks.on_ui_tabs(on_ui_tabs)
