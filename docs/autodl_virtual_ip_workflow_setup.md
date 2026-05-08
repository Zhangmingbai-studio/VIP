# AutoDL 虚拟 IP 生产工作流搭建记录

## 当前目标

先在 AutoDL 上搭建第一条工作流：**虚拟 IP 生产工作流**。

这条工作流负责：

```text
角色设定 -> Flux 角色候选图 -> 角色参考集 -> 视频首帧 -> 记录参数与版本
```

MVP 阶段暂时不训练 LoRA，先用 Flux + 固定 prompt + seed + 参考图策略，把角色视觉方向跑通。等需要连续生产同一个 IP 的多条视频时，再进入 LoRA 固化阶段。

当前 AutoDL 实例已经是 **ComfyUI 纯净版**，实际采用 **复用现有 `/root/ComfyUI` + WebUI-6006** 的路线。不要在这台实例上运行会新装 ComfyUI 或改端口的通用脚本。

## 当前实例

| 项目 | 结果 |
| --- | --- |
| GPU | RTX 5090 32GB |
| 磁盘 | 根盘约 295GB |
| 系统 | Ubuntu 22.04.5 LTS |
| Python | `/root/miniconda3/bin/python` 3.12.3 |
| PyTorch | 2.8.0+cu128 |
| ComfyUI | `/root/ComfyUI` |
| ComfyUI 版本 | 0.3.67 |
| 访问方式 | AutoDL 页面 `WebUI-6006` |
| 启动命令 | `python main.py --port 6006 --listen 127.0.0.1` |

原则：

```text
[x] 不修改 /root/start-comfyui.sh
[x] 不修改 AutoDL 端口映射
[x] 不另开 8188
[x] 不重新安装第二套 ComfyUI
```

## 目录规划

当前项目目录：

```text
/root/autodl-tmp/vip_singing/
  assets/
    ip_refs/
    first_frames/
  outputs/
    ip_candidates/
    first_frames/
  workflows/
    ip/
  prompts/
  logs/
```

ComfyUI 模型目录：

```text
/root/ComfyUI/models/
  diffusion_models/
  text_encoders/
  vae/
  loras/
  controlnet/
  upscale_models/
```

## 实际搭建方式

这台实例使用复用现有 ComfyUI 的脚本：

```bash
cd /root/autodl-tmp/VIP
chmod +x scripts/setup_autodl_existing_comfyui_virtual_ip.sh
PROJECT_DIR=/root/autodl-tmp/vip_singing bash scripts/setup_autodl_existing_comfyui_virtual_ip.sh
```

脚本会完成：

```text
[x] 复用 /root/ComfyUI
[x] 创建项目目录、输出目录、日志目录
[x] 从 AutoDL 公共模型盘软链接 Flux 模型
[x] 不启动、不停止、不重启 ComfyUI
[x] 不改 AutoDL 端口映射
```

当前已手动完成同等操作。

## Flux 模型接入

当前采用软链接，不复制大模型文件。

已接入模型：

```text
/root/ComfyUI/models/diffusion_models/flux1-dev.safetensors
/root/ComfyUI/models/diffusion_models/flux-2-klein-base-4b.safetensors
/root/ComfyUI/models/text_encoders/clip_l.safetensors
/root/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors
/root/ComfyUI/models/vae/ae.safetensors
/root/ComfyUI/models/vae/flux2-klein-vae.safetensors
```

来源：

```text
/.autodl-model/data/black-forest-labs/FLUX.1-dev/
/.autodl-model/data/black-forest-labs/FLUX.2-klein-base-4B/
/.autodl-model/data/comfyanonymous/flux_text_encoders/
```

推荐路线：

| 路线 | 用途 |
| --- | --- |
| FLUX.1-dev | 第一版 IP 定妆，质量优先 |
| FLUX.2-klein-base-4B | 快速实验、轻量测试 |

## ComfyUI 验证结果

ComfyUI API 已识别：

```text
UNETLoader: flux1-dev.safetensors, flux-2-klein-base-4b.safetensors
DualCLIPLoader: clip_l.safetensors, t5xxl_fp16.safetensors
VAELoader: ae.safetensors, flux2-klein-vae.safetensors
FluxGuidance: available
KSampler / VAEDecode / SaveImage: available
```

已完成一次 FLUX.1-dev smoke test：

```text
Model: flux1-dev.safetensors
Weight dtype: fp8_e4m3fn
Resolution: 512x768
Steps: 8
Seed: 260508001
AutoDL output: /root/autodl-tmp/vip_singing/outputs/ip_candidates/flux1_dev_smoke_00001_.png
Local copy: remote_outputs/flux1_dev_smoke_00001_.png
```

结果：成功出图，虚拟 IP 生产链路可用。

本地和远端已保存一个 UI 起点工作流：

```text
workflows/ip/flux1_dev_virtual_ip_text2image_ui_workflow.json
/root/autodl-tmp/vip_singing/workflows/ip/flux1_dev_virtual_ip_text2image_ui_workflow.json
```

同时已经注册到 ComfyUI 前端工作流目录：

```text
/root/ComfyUI/user/default/workflows/VIP/IP/Flux1_DEV_Virtual_IP_Text2Image.json
```

注意：ComfyUI 左侧“工作流”面板不会自动扫描项目目录 `/root/autodl-tmp/vip_singing/workflows`。要让 UI 面板显示，需要保存到 `/root/ComfyUI/user/default/workflows`，或通过 `/userdata` 接口注册。

## ComfyUI 内部工作流搭建

进入 AutoDL 页面：

```text
访问实例 -> WebUI-6006
```

建议从模板开始：

```text
Template / Workflow Templates -> Image -> Flux Text-to-Image
```

也可以直接导入已保存的 UI workflow：

```text
/root/autodl-tmp/vip_singing/workflows/ip/flux1_dev_virtual_ip_text2image_ui_workflow.json
```

当前更推荐直接从左侧工作流面板打开：

```text
VIP / IP / Flux1_DEV_Virtual_IP_Text2Image.json
```

MVP 阶段先搭这条最小链路：

```text
Load Diffusion Model / UNETLoader
DualCLIPLoader
VAELoader
CLIPTextEncode
FluxGuidance
EmptyLatentImage
KSampler
VAEDecode
SaveImage
```

建议参数：

| 参数 | 起始值 |
| --- | --- |
| model | `flux1-dev.safetensors` |
| weight_dtype | `fp8_e4m3fn` |
| clip_name1 | `t5xxl_fp16.safetensors` |
| clip_name2 | `clip_l.safetensors` |
| vae | `ae.safetensors` |
| 分辨率 | 768x1024 或 832x1216 |
| steps | 20-30 |
| guidance | 3.5 |
| sampler | euler |
| scheduler | simple |

## 虚拟 IP 生产流程

### 1. 写角色设定卡

使用模板：

```text
prompts/ip_character_card_template.md
/root/autodl-tmp/vip_singing/prompts/ip_character_card_template.md
```

先明确这些固定项：

```text
发型、发色、眼睛、服装、妆容、年龄感、气质、画风、禁止变化项
```

### 2. 生成角色候选

建议第一轮生成 20-40 张。

输出保存到：

```text
/root/autodl-tmp/vip_singing/outputs/ip_candidates/
```

筛选标准：

```text
[ ] 五官稳定且有辨识度
[ ] 嘴部清楚，适合后续 lip-sync
[ ] 服装和发型不过度复杂
[ ] 背景不抢主体
[ ] 没有明显手、眼、牙齿错误
```

### 3. 建立角色参考集

从候选图中选出：

```text
assets/ip_refs/ref_front.png
assets/ip_refs/ref_smile.png
assets/ip_refs/ref_singing.png
assets/ip_refs/ref_closed_eyes.png
assets/ip_refs/ref_outfit.png
```

### 4. 生成视频首帧

首帧 prompt 重点是稳定：

```text
single virtual singer, 9:16 vertical composition, medium close-up, facing camera, clear mouth, natural singing expression, soft stage lighting, clean background, stable face, high quality
```

首帧建议：

```text
[ ] 中近景
[ ] 正脸或轻微侧脸
[ ] 嘴无遮挡
[ ] 不拿麦克风挡嘴
[ ] 手不要贴近脸
[ ] 背景简单
```

输出保存到：

```text
/root/autodl-tmp/vip_singing/outputs/first_frames/
/root/autodl-tmp/vip_singing/assets/first_frames/
```

## 每次生成记录

远端记录文件：

```text
/root/autodl-tmp/vip_singing/logs/generation_notes.md
```

本地进度文件：

```text
DEVELOPMENT_PROGRESS.md
```

记录格式：

```text
日期：
目标：
模型：
workflow：
prompt：
seed：
分辨率：
输出路径：
选择结果：
问题：
下一步：
```

## IP 工作流验收标准

当前已完成：

```text
[x] AutoDL 可打开 ComfyUI
[x] ComfyUI 使用 WebUI-6006
[x] Flux 模型已接入
[x] FLUX.1-dev smoke test 已成功出图
```

下一步验收：

```text
[ ] 已生成 20-40 张角色候选图
[ ] 已选出 1 张主参考图
[ ] 已输出 1 张 9:16 视频首帧
[ ] prompt、seed、模型版本和输出路径已记录
```
