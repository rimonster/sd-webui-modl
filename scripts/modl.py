import gradio as gr
import os
import time
import shutil
import requests
import urllib
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
    def copyfileobj(fsrc, fdst, callback, length=0):
        try:
            # check for optimisation opportunity
            if "b" in fsrc.mode and "b" in fdst.mode and fsrc.readinto:
                return _copyfileobj_readinto(fsrc, fdst, callback, length)
        except AttributeError:
            # one or both file objects do not support a .mode or .readinto attribute
            pass

        if not length:
            length = shutil.COPY_BUFSIZE

        fsrc_read = fsrc.read
        fdst_write = fdst.write

        copied = 0
        while True:
            buf = fsrc_read(length)
            if not buf:
                break
            fdst_write(buf)
            copied += len(buf)
            callback(copied)

    # differs from shutil.COPY_BUFSIZE on platforms != Windows
    READINTO_BUFSIZE = 1024 * 1024

    def _copyfileobj_readinto(fsrc, fdst, callback, length=0):
        fsrc_readinto = fsrc.readinto
        fdst_write = fdst.write

        if not length:
            try:
                file_size = os.stat(fsrc.fileno()).st_size
            except OSError:
                file_size = READINTO_BUFSIZE
            length = min(file_size, READINTO_BUFSIZE)

        copied = 0
        with memoryview(bytearray(length)) as mv:
            while True:
                n = fsrc_readinto(mv)
                if not n:
                    break
                elif n < length:
                    with mv[:n] as smv:
                        fdst.write(smv)
                else:
                    fdst_write(mv)
                copied += n
                callback(copied)



    def show_progress(copied, progress, total_size):
        progress(copied/total_size, desc="Downloading...")
        if copied == total_size:
            progress(1, desc="Done!")
            
    def download_models(selected_models, progress=gr.Progress()):
        # Check if there is enough disk space
        total_size = sum(model["size"] for model in selected_models)
        available_space = shutil.disk_usage(".").free
        if total_size > available_space:
            return f"Not enough disk space. Required: {total_size/1024/1024:.2f} MB, Available: {available_space/1024/1024:.2f} MB"

        # Download the selected models
        progress(0, desc="Starting...")
        for model in selected_models:
            filename = os.path.basename(model["url"])
            path = os.path.join(model["path"], filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            response = requests.get(model["url"], stream=True)
            with open(path,"wb") as f:
                shutil.copyfileobj(response.raw, f, show_progress(copied=0, total_size=model["size"], progress=progress))
            del response
        return "All models downloaded successfully"


    def get_models():
        # Load the models list from the repo
        rep_file = os.path.join("extensions", "sd-webui-modl", "models.txt")
        with open(rep_file, "r") as f:
            modelist = f.read()

        # Parse the models list
        models = []
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
            req = urllib.request.Request(model_url.strip(), method='HEAD')
            try:
                fl = urllib.request.urlopen(req)
            except:
                continue
            if fl.status == 200:
                size = int(fl.headers['Content-Length'])
                name = model_name.strip() + " (" + format_bytes(size) + ")"
                models.append({"section": current_section[0], "name": name, "url": model_url.strip(), "size": size, "path": model_path})
        return models

    def update_sizes_table(*selected_models):
        sizes_data = []
        total_size = 0
        for i, section in enumerate(sections):
            section_models = [model for model in models if model["section"] == section]
            if i < len(selected_models):
                for selected_model in selected_models[i]:
                    model_dict = next(model for model in section_models if model["name"] == selected_model)
                    sizes_data.append([model_dict["name"], format_bytes(model_dict["size"])])
                    total_size += model_dict["size"]

        available_space = shutil.disk_usage(".").free
        available_after_downloads = available_space - total_size

        sizes_data.append(["Total", format_bytes(total_size)])
        sizes_data.append(["Available Disk Space", format_bytes(available_space)])
        sizes_data.append(["Available After Downloads", format_bytes(available_after_downloads)])

        return sizes_data


    models = get_models()
    if models is None:
        print("Error fetching models list from repo")
    else:
        with gr.Blocks(analytics_enabled=False) as modl:
            with gr.Box(elem_classes="modl_box"):
                with gr.Column():
                    gr.Markdown("### Choose models to download")
                    sections = list(set([model["section"] for model in models]))
                    sizes_table = gr.Dataframe(headers=["Model", "Size"], datatype="str", type="array", col_count=2)
                    checkboxes = {}
                    for section in sections:
                        section_models = [model for model in models if model["section"] == section]
                        checkboxes[section] = gr.Dropdown(multiselect=True, label=section, choices=[model["name"] for model in section_models], value=[])
                        checkboxes[section].change(update_sizes_table, inputs=list(checkboxes.values()), outputs=[sizes_table])

                    download_button = gr.Button(value="Download")
                    output_text = gr.Textbox(label="Result")

                    def process_download(*selected_models):
                        selected_model_dicts = []
                        for i, section in enumerate(sections):
                            section_models = [model for model in models if model["section"] == section]
                            for selected_model in selected_models[i]:
                                selected_model_dicts.append(next(model for model in section_models if model["name"] == selected_model))
                        result = download_models(selected_model_dicts)
                        return result

                    download_button.click(process_download, inputs=list(checkboxes.values()), outputs=[output_text])

    return (modl, "MoDL", "modl"),
script_callbacks.on_ui_tabs(on_ui_tabs)
