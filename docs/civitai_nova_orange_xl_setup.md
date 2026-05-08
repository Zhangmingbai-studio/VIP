# Civitai 模型接入：Nova Orange XL

## 模型判断

用户提供链接：

```text
https://civitai.com/models/967405/nova-orange-xl
```

结论：

```text
类型：Checkpoint / Checkpoint Merge
Base Model：Illustrious
不是 Flux 模型
不放入 UNETLoader
不放入 models/diffusion_models
```

正确接入方式：

```text
模型文件 -> /root/ComfyUI/models/checkpoints/
工作流 -> CheckpointLoaderSimple
```

## 推荐版本

官方 Civitai API 查询到的最新版本：

```text
Version: EX v2.0
ModelVersionId: 2784048
File: novaOrangeXL_exV20.safetensors
Size: about 6.46 GB
Download URL: https://civitai.com/api/download/models/2784048
Base Model: Illustrious
Published: 2026-03-18
```

镜像页面曾显示的版本：

```text
Version: EX v1.0
ModelVersionId: 2672639
File: novaOrangeXL_exV10.safetensors
Download URL: https://civitai.com/api/download/models/2672639
```

默认建议先用 EX v2.0。如果你特别喜欢 EX v1.0 示例图，也可以改用 EX v1.0。

## 当前 AutoDL 状态

AutoDL 实例直接访问 `civitai.com` 失败，错误为网络不可达。因此当前没有自动下载模型。

需要将模型文件放到：

```text
/root/ComfyUI/models/checkpoints/novaOrangeXL_exV20.safetensors
```

可选方式：

```text
1. 本地浏览器从 Civitai 下载后，通过 AutoDL/JupyterLab 上传
2. 下载到本地后用 scp/rsync 上传
3. 后续找到可访问的镜像源后再从 AutoDL 端下载
```

## 已创建工作流

本地：

```text
workflows/ip/nova_orange_xl_illustrious_text2image_ui_workflow.json
```

AutoDL 项目目录：

```text
/root/autodl-tmp/vip_singing/workflows/ip/nova_orange_xl_illustrious_text2image_ui_workflow.json
```

ComfyUI 前端工作流目录：

```text
/root/ComfyUI/user/default/workflows/VIP/IP/Nova_Orange_XL_Illustrious_Text2Image.json
```

打开方式：

```text
AutoDL WebUI-6006 -> 左侧工作流 -> 刷新 -> VIP / IP / Nova_Orange_XL_Illustrious_Text2Image.json
```

## 推荐参数

作者推荐：

```text
Sampler: Euler a
Steps: 20-30
CFG Scale: 3-5
Clip Skip: 1-2
```

当前工作流起始参数：

```text
sampler_name: euler_ancestral
scheduler: normal
steps: 28
cfg: 4.0
clip skip: 2
resolution: 832x1216
batch_size: 1
seed: randomize
```

## 起始 Positive Prompt

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres, newest, 1girl, solo, original character, virtual singer, silver white long hair, soft airy bangs, pale blue eyes, delicate oval face, natural light makeup, black short stage jacket, dark inner top, silver in-ear monitors, small silver earrings, medium close-up portrait, facing viewer, clear visible mouth, natural singing expression, calm and gentle expression, dramatic soft stage lighting, depth of field, volumetric lighting, detailed skin, detailed clothing texture
```

## 起始 Negative Prompt

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digits, fewer digits, cropped, very displeasing, worst quality, bad quality, sketch, jpeg artifacts, signature, watermark, username, simple background, conjoined, bad ai-generated, multiple people, hand covering face, microphone covering mouth, cropped mouth, extreme side view
```

## 注意事项

这个模型是 Illustrious 系，不是 Flux 系。它的 prompt 风格更偏 Danbooru/tag 体系，可以使用 `1girl, solo, masterpiece, best quality` 这类质量词和标签。

后续如果要给这个模型加 LoRA，也要优先选择 Illustrious/SDXL 兼容 LoRA，不要直接混用 Flux LoRA。

