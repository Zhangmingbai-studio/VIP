# RVC 音频工作流搭建记录

## 目标

在 AutoDL 实例上搭建第二条工作流：歌曲片段输入 -> 人声/伴奏分离 -> RVC 音色转换 -> 与伴奏混音，先服务 10-15 秒 MVP 片段。

本次不修改 ComfyUI 的 WebUI-6006，也不修改 AutoDL 端口映射。RVC WebUI 预留使用 AutoDL 已提供的 WebUI-6008。

## 远端目录

```text
/root/autodl-tmp/vip_singing/audio_workflow/
├── input/
│   ├── song_clips/      # 原始歌曲片段
│   └── rvc_models/      # 你上传的 RVC 音色模型，每个模型一个子目录
├── output/
│   ├── separated/       # Demucs 分离结果
│   ├── rvc_vocals/      # RVC 转换后的人声
│   └── final_mix/       # 重新混音后的成品音频
├── scripts/             # 远端执行脚本
├── logs/                # 启动和运行日志
└── tools/
    └── Retrieval-based-Voice-Conversion-WebUI/
```

RVC 仓库内部关键模型目录：

```text
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/hubert/
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/rmvpe/
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/weights/
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/indices/
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/uvr5_weights/
```

## 已安装内容

```text
Conda 环境：rvc
Python：3.10.20
RVC 仓库：RVC-Project/Retrieval-based-Voice-Conversion-WebUI
PyTorch：2.11.0+cu128
GPU：RTX 5090，CUDA 可用
Demucs：4.0.1
ffmpeg：已安装在 rvc 环境
Gradio：3.34.0
gradio_client：0.2.9
```

注意：RVC 旧依赖对 pip 比较敏感，当前环境已将 pip 固定在 `23.3.2`。不要直接升级 pip，否则 `omegaconf/fairseq` 这类旧依赖可能再次安装失败。

## 你需要下载并上传的模型

必需：

```text
1. hubert_base.pt
上传到：
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/hubert/hubert_base.pt

2. rmvpe.pt
上传到：
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/rmvpe/rmvpe.pt

3. RVC 音色模型 .pth
建议上传到：
/root/autodl-tmp/vip_singing/audio_workflow/input/rvc_models/<voice_name>/<voice_name>.pth

4. 与该音色模型配套的 .index
建议上传到：
/root/autodl-tmp/vip_singing/audio_workflow/input/rvc_models/<voice_name>/<voice_name>.index
```

上传 RVC 音色模型后，执行：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/sync_rvc_model_assets.sh
```

这个脚本会把 `input/rvc_models/<voice_name>/` 里的 `.pth` 和 `.index` 软链接到 RVC WebUI 能自动识别的目录。

可选：

```text
UVR5 人声分离模型：
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/uvr5_weights/
```

当前优先用 Demucs 做人声/伴奏分离。Demucs 第一次运行 `htdemucs` 时可能会自动下载分离模型；如果 AutoDL 网络失败，再单独处理 Demucs 模型缓存或改走 UVR5。

## 启动 RVC WebUI

确认模型上传后，启动：

```bash
nohup bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/start_rvc_webui.sh 6008 \
  > /root/autodl-tmp/vip_singing/audio_workflow/logs/rvc_webui_6008.log 2>&1 &
```

然后在 AutoDL 页面点击 `WebUI-6008`。

如果只是临时前台启动，使用：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/start_rvc_webui.sh 6008
```

## MVP 使用流程

1. 上传 10-15 秒原始歌曲片段到：

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/
```

2. 用 Demucs 分离人声和伴奏：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/separate_vocals_demucs.sh \
  /root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/demo.wav
```

输出一般在：

```text
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/vocals.wav
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav
```

3. 打开 RVC WebUI，选择你的 `.pth` 模型和 `.index`，输入 `vocals.wav` 做转换。

建议第一轮参数：

```text
f0 method：rmvpe
transpose：先用 0，男女声跨度明显时再试 +/-12
index rate：0.5-0.75
protect：0.33
resample sr：0
```

4. 将转换后的人声保存到：

```text
/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/
```

5. 与伴奏重新混音：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/mix_rvc_with_instrumental.sh \
  /root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/demo_rvc.wav \
  /root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav \
  /root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/demo_final.wav
```

## 验证命令

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/rvc_audio_smoke_check.sh
```

目前没有上传 `hubert_base.pt`、`rmvpe.pt` 和具体音色模型前，验证脚本会显示这些模型 missing，这是预期状态。Python 包、CUDA、Demucs、ffmpeg 正常即可。

## 合规提醒

即使是兴趣项目，也建议只使用你有权使用的歌曲片段和音色模型。后续如果换成自己训练的音色，训练素材也尽量使用本人授权或自有素材。
