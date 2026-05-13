# 虚拟 IP 唱歌视频工作流使用手册

本文档记录已经搭好的工作流如何使用。目标是下次直接照流程生产，不再重新推理目录、端口和脚本。

## 总览

当前 MVP 分三层：

```text
1. 虚拟 IP 图像层：ComfyUI / WebUI-6006
2. RVC 音频层：RVC WebUI / WebUI-6008 + Demucs 脚本
3. LTX-2.3 视频层：ComfyUI / WebUI-6006
```

远端项目根目录：

```text
/root/autodl-tmp/vip_singing/
```

重要原则：

```text
ComfyUI 固定使用 127.0.0.1:6006，对应 AutoDL WebUI-6006
RVC WebUI 固定使用 127.0.0.1:6008，对应 AutoDL WebUI-6008
不要改 AutoDL 端口映射
不要另开一套 ComfyUI
大文件模型不要提交到 GitHub
```

推荐每次产出后记录：

```text
模型、workflow、prompt、seed、输入文件、输出文件、是否采用、问题
```

本地进度文件：

```text
DEVELOPMENT_PROGRESS.md
```

远端记录文件：

```text
/root/autodl-tmp/vip_singing/logs/generation_notes.md
```

## 工作流一：虚拟 IP 图像层

### 入口

打开 AutoDL 页面：

```text
WebUI-6006
```

当前主要使用 Nova Orange XL 工作流：

```text
左侧工作流 -> VIP / IP / Nova_Orange_XL_Illustrious_Text2Image.json
```

备用 Flux 工作流：

```text
左侧工作流 -> VIP / IP / Flux1_DEV_Virtual_IP_Text2Image.json
```

### 模型位置

Nova Orange XL：

```text
/root/ComfyUI/models/checkpoints/novaOrangeXL_exV20.safetensors
```

Flux 模型为 AutoDL 公共模型盘软链接：

```text
/root/ComfyUI/models/diffusion_models/flux1-dev.safetensors
/root/ComfyUI/models/text_encoders/clip_l.safetensors
/root/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors
/root/ComfyUI/models/vae/ae.safetensors
```

### 推荐使用 Nova Orange XL

当前角色 `Luna v1` 的设定和 prompt 在：

```text
prompts/ip_character_card_luna_v1.md
```

第一轮抽图建议：

```text
model：novaOrangeXL_exV20.safetensors
分辨率：832x1216
steps：28
cfg：4.0
sampler：euler_ancestral
scheduler：normal
clip skip：2
seed：randomize
右上角运行数量：8
```

如果画面离镜头太近，用 `prompts/ip_character_card_luna_v1.md` 里的：

```text
Nova Orange XL 构图调整 Prompt
```

### 抽图流程

1. 打开 `Nova_Orange_XL_Illustrious_Text2Image.json`。
2. 将正向 prompt 和负向 prompt 粘贴进对应 `CLIP文本编码`。
3. 设置 seed 为 `randomize`。
4. 右上角运行数量先设为 `8`，小批量测试。
5. 满意后再扩到 `20-40` 张。
6. 每张图保留 prompt、seed、模型、输出路径。

ComfyUI 输出目录通常为：

```text
/root/ComfyUI/output/VIP/NovaOrangeXL/
```

如果忘了 seed，可以把生成的 PNG 拖回 ComfyUI，通常能从图片 metadata 还原 workflow 和 seed。

### 选图标准

```text
[ ] 角色辨识度强
[ ] 银白长发、浅蓝眼、黑色舞台服稳定
[ ] 嘴部清楚，无遮挡
[ ] 不要麦克风挡嘴
[ ] 手不要靠近脸
[ ] 不要多人同框
[ ] 适合后续 lip-sync
```

### 固化首帧

选定最终图后，建议保留 ComfyUI 原始输出文件，同时复制一份到资产库：

```text
/root/autodl-tmp/vip_singing/assets/ip_refs/<ip_name>_v1_ref_front.png
/root/autodl-tmp/vip_singing/assets/first_frames/<ip_name>_v1_first_frame.png
```

例如：

```text
/root/autodl-tmp/vip_singing/assets/first_frames/luna_v1_first_frame.png
/root/autodl-tmp/vip_singing/assets/first_frames/zeta_v1_first_frame.png
/root/autodl-tmp/vip_singing/assets/first_frames/alpha_v1_first_frame.png
```

视频层不会直接扫描 `assets/first_frames`，而是通过同步脚本把这些图片链接到 ComfyUI 的 input 目录。执行：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/prepare_ltx23_video_inputs.sh
```

之后在视频工作流的 `Load Image` 节点中，从下拉列表选择：

```text
VIP/video/first_frames/<ip_name>_v1_first_frame.png
```

## 工作流二：RVC 音频层

### 入口

RVC WebUI 使用：

```text
AutoDL WebUI-6008
```

启动命令：

```bash
nohup bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/start_rvc_webui.sh 6008 \
  > /root/autodl-tmp/vip_singing/audio_workflow/logs/rvc_webui_6008.log 2>&1 &
```

检查环境：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/rvc_audio_smoke_check.sh
```

### 模型位置

RVC 基础模型：

```text
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/hubert/hubert_base.pt
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/rmvpe/rmvpe.pt
```

音色模型上传目录：

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/rvc_models/
```

当前音色：

```text
misono-mika.pth
misono-mika.index
```

上传或替换音色模型后执行：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/sync_rvc_model_assets.sh
```

### 音频目录

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/     # 原始歌曲片段
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/     # Demucs 分离
/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/    # RVC dry vocal
/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/     # 最终混音
```

### 步骤 1：准备 10-15 秒歌曲片段

如果已经知道高潮开始时间，用本地或远端脚本裁切。

本地 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\audio\extract_song_clip.ps1 `
  "D:\music\full_song.mp3" `
  ".\demo.wav" `
  --start 01:12 `
  --duration 15
```

远端 Python：

```bash
python3 /root/autodl-tmp/vip_singing/audio_workflow/scripts/prepare_song_clip.py "/path/to/full_song.mp3" \
  --start 01:12 \
  --duration 12 \
  --out "/path/to/song_clip_12s.wav"
```

如果不知道高潮在哪，本地可生成候选：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\audio\extract_song_clip.ps1 `
  "D:\music\full_song.mp3" `
  ".\demo.wav" `
  --auto `
  --duration 15 `
  --candidate-dir ".\clip_candidates"
```

将选中的片段上传到：

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/
```

### 步骤 2：Demucs 分离人声和伴奏

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/separate_vocals_demucs.sh \
  /root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/demo.wav
```

输出：

```text
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/vocals.wav
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav
```

### 步骤 3：RVC 转换人声

打开 `WebUI-6008`。

界面设置：

```text
Inferencing voice：misono-mika.pth
Transpose：0
audio file：填 vocals.wav 的完整服务器路径
feature index：选择或填写 misono-mika.index
pitch extraction algorithm：rmvpe
resample：0
volume envelope：0.25
protect：0.33
filter radius：3
index rate：0.5-0.75
```

点击 `Convert`。

注意：RVC WebUI 的输出通常在：

```text
/tmp/gradio/<hash>/audio.wav
```

### 步骤 4：归档 RVC 人声并混音

推荐使用一键归档和混音脚本：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/archive_latest_rvc_and_mix.sh \
  /root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav \
  demo_misono_mika
```

输出：

```text
/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/demo_misono_mika_rvc.wav
/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/demo_misono_mika_final_mix.wav
```

视频层需要两条音频：

```text
RVC dry vocal：用于 lip-sync / motion 驱动
final_mix：用于最终成片声音
```

### 当前已完成音频样例

```text
RVC dry vocal：
/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/045b_clip_27s_16s_misono_mika_rvc.wav

final mix：
/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/045b_clip_27s_16s_misono_mika_final_mix.wav
```

## 工作流三：LTX-2.3 视频层

当前状态：工作流骨架已经搭好，LTX-2.3 模型已下载并通过环境检查。下一步先跑 5 秒 smoke，确认口型、人物稳定性和基础运动质量。

当前已准备：

```text
AutoDL WebUI-6006
ComfyUI-LTXVideo
ComfyUI-VideoHelperSuite
ComfyMath
VIP/Video/LTX_2_3_IA2V_Smoke_5s.json
VIP/Video/LTX_2_3_IA2V_Full_16s.json
```

输入素材链接脚本：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/prepare_ltx23_video_inputs.sh
```

环境检查：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/check_ltx23_video_setup.sh
```

模型下载：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/download_ltx23_models.sh
```

如果下载快结束时出现 `403 Forbidden`，一般是 Hugging Face/Xet 临时签名链接过期。不要删除半截模型文件，重新执行同一条命令即可续传；脚本会校验首个大模型是否达到 `29145431166` bytes。

模型确认完成后，先打开：

```text
VIP/Video/LTX_2_3_IA2V_Smoke_5s.json
```

如果旧画布运行时报 `Node ID '#340:287' has no class_type`，刷新左侧工作流列表后重新打开该工作流。当前远端版本已经展平 Group Node。

在 `Load Image` 节点中选择首帧：

```text
VIP/video/first_frames/<ip_name>_v1_first_frame.png
```

在 `Load Audio` 节点中选择 RVC dry vocal：

```text
VIP/video/audio/rvc_vocals/<name>_rvc.wav
```

每次新增或替换首帧图、RVC 人声、final mix 后，先执行：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/prepare_ltx23_video_inputs.sh
```

确认 5 秒视频没有明显崩脸、口型可接受，再运行：

```text
VIP/Video/LTX_2_3_IA2V_Full_16s.json
```

最后将视频音频替换为 final mix：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/mux_final_audio.sh \
  /root/ComfyUI/output/VIP/LTX23/你的_ltx_输出.mp4 \
  /root/autodl-tmp/vip_singing/video_workflow/output/<ip_name>_<song_clip>_final_mix.mp4 \
  /root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/<name>_final_mix.wav
```

## 一次完整生产的文件链

```text
IP 首帧：
/root/autodl-tmp/vip_singing/assets/first_frames/<ip_name>_v1_first_frame.png

歌曲片段：
/root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/<clip>.wav

Demucs 人声：
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/<clip>/vocals.wav

Demucs 伴奏：
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/<clip>/no_vocals.wav

RVC 人声：
/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/<name>_rvc.wav

最终混音：
/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/<name>_final_mix.wav

LTX 视频：
/root/ComfyUI/output/VIP/LTX23/<video>.mp4

替换 final_mix 后的最终视频：
/root/autodl-tmp/vip_singing/video_workflow/output/<name>_final_mix.mp4
```

## 常用检查命令

检查 ComfyUI：

```bash
pgrep -af 'main.py --port 6006'
```

检查 RVC：

```bash
pgrep -af 'infer-web.py --port 6008'
```

检查磁盘：

```bash
df -h /
```

检查 GPU：

```bash
nvidia-smi
```

检查 RVC 环境：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/rvc_audio_smoke_check.sh
```

检查 LTX-2.3 视频环境：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/check_ltx23_video_setup.sh
```
