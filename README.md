# MoDL - Model Downloader
Stable Diffusion Web UI Extension for easily downloading controlnet, instruct pix2pix, Segment Anything and other model files.  

# Installation
1. Click 'Extensions' tab and then 'Install from url': https://github.com/rimonster/sd-webui-modl
2. Extensions -> Installed -> Apply and restart UI
3. Click 'MoDL' tab
4. Select models for download, see the table to consider your available disk space before hitting download
5. Click download 

* Now includes links to Controlnet v1.1 models

## Supports the following extensions:
* Mikubill / Controlnet: https://github.com/Mikubill/sd-webui-controlnet
* Continue revolution / Segment anything: https://github.com/continue-revolution/sd-webui-segment-anything
* Timothy Brooks / Instruct pix2pix (automatically enabled in Automatic1111's img2img tab when you select this model): https://www.timothybrooks.com/instruct-pix2pix/

# What? Why?
Because many extensions like controlnet and segment anything and others are relying on you to transfer heavy model files from specific urls to specific local paths. For some people who work on many/temporary machines of various OS it's handy to have a tool to download their favorite models for controlnet etc painlessly for every new installation.
You can clone and then use your own models.txt for your favorite models and then also include your private models for easy access.


# Change Log

## v0.6
* Better UI
* Shorter models.txt
* Well sorted sections

## v0.5
* Using urlretrieve now. How do I create a decent gradio progress bar for the downloads?

## v0.4
* Display of model files with sizes
* total file size of models selected and free disk space available

## v0.3
* Display file sizes and free space on disk before download 

## v0.2
* download controlnet sd15 and fp16, pix2pix, segment anything and inpainting models

## v0.1
* hello modl: offering basic fp16 controlnet models from hugginface

## TODO
* Check if models already downloaded and then disable in choice list
* Show % of DL for each file and for total download with ETA (happens in terminal not in gradio GUI)
* Add git repos as full sections in models.txt so they refresh with new models
* Add gdrive support for personal models
* add remove/merge models features for a full model manager 
