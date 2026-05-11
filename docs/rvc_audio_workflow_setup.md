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

如果只是临时测试，也可以直接把 `.pth` 和 `.index` 放到：

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/rvc_models/
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

1. 将下载好的完整歌曲裁成 10-15 秒 WAV 片段：

```bash
python3 scripts/audio/prepare_song_clip.py "/path/to/full_song.mp3" \
  --start 01:12 \
  --duration 12 \
  --out "/path/to/song_clip_12s.wav"
```

说明：

```text
--start 支持秒数、MM:SS、HH:MM:SS
--duration MVP 推荐 10-15 秒，默认 12 秒
--out 可以是完整 wav 路径，也可以是目录；例如 `--out .` 表示输出到当前目录
输出格式为 44.1kHz / pcm_s16le / wav
```

2. 上传 10-15 秒原始歌曲片段到：

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/
```

3. 用 Demucs 分离人声和伴奏：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/separate_vocals_demucs.sh \
  /root/autodl-tmp/vip_singing/audio_workflow/input/song_clips/demo.wav
```

输出一般在：

```text
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/vocals.wav
/root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav
```

4. 打开 RVC WebUI，选择你的 `.pth` 模型和 `.index`，输入 `vocals.wav` 做转换。

建议第一轮参数：

```text
f0 method：rmvpe
transpose：先用 0，男女声跨度明显时再试 +/-12
index rate：0.5-0.75
protect：0.33
resample sr：0
```

5. 将转换后的人声归档，并与伴奏重新混音。

RVC WebUI 只负责音色转换，不负责把人声和伴奏混回一条歌。点击 Convert 后，输出音频通常先保存在服务器的 Gradio 临时目录，例如：

```text
/tmp/gradio/<hash>/audio.wav
```

不需要先下载到本地再上传回服务器。推荐直接在服务器上执行一键归档和混音脚本：

```bash
bash /root/autodl-tmp/vip_singing/audio_workflow/scripts/archive_latest_rvc_and_mix.sh \
  /root/autodl-tmp/vip_singing/audio_workflow/output/separated/htdemucs/demo/no_vocals.wav \
  demo_misono_mika
```

它会自动：

```text
1. 找到 /tmp/gradio 里最新的 RVC WebUI 输出音频
2. 复制到 output/rvc_vocals/<name>_rvc.wav
3. 与 no_vocals.wav 混音
4. 输出到 output/final_mix/<name>_final_mix.wav
```

如果你已经手动知道 RVC 人声路径，也可以直接调用底层混音脚本：

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

## 常见问题

### Demucs 保存 wav 时报 TorchCodec 缺失

如果 Demucs 已经跑到 100%，但最后报：

```text
ModuleNotFoundError: No module named 'torchcodec'
ImportError: TorchCodec is required for save_with_torchcodec
```

说明分离计算已经完成，失败点在 `torchaudio.save()` 写出 wav 文件。新版 TorchAudio 将音频保存转向 TorchCodec，需要给 `rvc` 环境补装一次：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate rvc
python -m pip install --no-cache-dir "torchcodec==0.11.*" --index-url https://download.pytorch.org/whl/cpu
python - <<'PY'
from torchcodec.encoders import AudioEncoder
print("torchcodec ok")
PY
```

安装成功后重新执行 `separate_vocals_demucs.sh` 即可。

如果 `torchcodec` 已显示 installed，但验证时报：

```text
Could not load libtorchcodec
GLIBCXX_3.4.31 not found
```

说明 `torchcodec` 找到了 FFmpeg，但加载时撞上了系统较旧的 `libstdc++.so.6`。先让当前 shell 优先使用 conda 环境里的运行库：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate rvc
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"
python - <<'PY'
from torchcodec.encoders import AudioEncoder
print("torchcodec ok")
PY
```

如果仍然失败，再补装较新的 conda C++ 运行库：

```bash
conda install -y -c conda-forge libstdcxx-ng
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"
python - <<'PY'
from torchcodec.encoders import AudioEncoder
print("torchcodec ok")
PY
```

验证通过后，在同一个 shell 里重新执行 Demucs 分离命令。

### RVC WebUI 启动时报 soundfile 缺失

如果 `soundfile` 在 `rvc` 环境里已经安装，但启动 WebUI 仍报：

```text
ModuleNotFoundError: No module named 'soundfile'
```

通常是启动脚本里的 `python` 走到了 base conda 环境，而不是 `rvc` 环境。新版 `start_rvc_webui.sh` 已经改为使用绝对路径：

```text
/root/miniconda3/envs/rvc/bin/python
```

临时手动启动也可以这样做：

```bash
cd /root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI
export LD_LIBRARY_PATH="/root/miniconda3/envs/rvc/lib:${LD_LIBRARY_PATH:-}"
nohup /root/miniconda3/envs/rvc/bin/python infer-web.py \
  --port 6008 \
  --pycmd /root/miniconda3/envs/rvc/bin/python \
  --noautoopen \
  > /root/autodl-tmp/vip_singing/audio_workflow/logs/rvc_webui_6008.log 2>&1 &
```

### RVC Convert 时报 HuBERT weights_only 加载失败

如果 WebUI 只显示 `Error`，日志中出现：

```text
_pickle.UnpicklingError: Weights only load failed
Unsupported global: GLOBAL fairseq.data.dictionary.Dictionary
```

这是 PyTorch 2.6+ 将 `torch.load()` 的默认 `weights_only` 改为 `True` 后，与旧版 fairseq/RVC 加载 `hubert_base.pt` 的方式不兼容。确认 `hubert_base.pt` 来源可信后，可在 `rvc` 环境里的 fairseq 做兼容补丁：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate rvc
python - <<'PY'
from pathlib import Path

p = Path("/root/miniconda3/envs/rvc/lib/python3.10/site-packages/fairseq/checkpoint_utils.py")
backup = p.with_suffix(".py.rvc_bak")
if not backup.exists():
    backup.write_text(p.read_text())

text = p.read_text()
old = 'state = torch.load(f, map_location=torch.device("cpu"))'
new = 'state = torch.load(f, map_location=torch.device("cpu"), weights_only=False)'
if old in text:
    p.write_text(text.replace(old, new, 1))
elif new not in text:
    raise SystemExit("expected torch.load line not found")
print("fairseq checkpoint loader patched")
PY
```

补丁后需要重启 RVC WebUI-6008，再刷新浏览器页面。

## 合规提醒

即使是兴趣项目，也建议只使用你有权使用的歌曲片段和音色模型。后续如果换成自己训练的音色，训练素材也尽量使用本人授权或自有素材。
