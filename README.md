# MoDL - Model Downloader
Stable Diffusion Web UI Extension for easily downloading controlnet, instruct pix2pix, SAM and other model files.  

1. Extensions - Install from url: https://github.com/rimonster/sd-webui-modl
2. Click MoDL tab
3. Select models
4. Click download 

## Works with these extensions:
* https://github.com/Mikubill/sd-webui-controlnet
* https://github.com/continue-revolution/sd-webui-segment-anything
* Instruct pix2pix (built into Automatic1111 img2img): https://www.timothybrooks.com/instruct-pix2pix/

# Change Log

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
* Show % of DL for each file and for total download with ETA
* Add gdrivbe support for personal models
