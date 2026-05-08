# 虚拟 IP 唱歌视频 MVP 工作流

## 目标

在 AutoDL 云服务器上搭建 3 条相互衔接的 ComfyUI/RVC 工作流，先稳定产出一条 10-15 秒的虚拟 IP 唱歌片段。

MVP 不追求完整 MV、多场景叙事或平台级精修，优先验证这个闭环：

```text
固定角色首帧 -> 目标音色歌声 -> 轻动作唱歌视频 -> 后期剪辑成片
```

建议首条成片规格：

| 项目 | MVP 建议 |
| --- | --- |
| 时长 | 10-15 秒 |
| 画幅 | 9:16 竖屏 |
| 初始生成分辨率 | 540x960 或 720x1280 |
| 最终导出 | 1080x1920 |
| 镜头数 | 1 个主镜头，最多 2 个 |
| 动作幅度 | 轻微表情、眨眼、头部律动、肩膀微动、轻微镜头运动 |
| 成片软件 | 剪映 / Premiere / DaVinci Resolve 等专业剪辑软件 |

## 总体架构

服务器上实际维护 3 条核心工作流：

```text
1. 虚拟 IP 生产工作流
   负责角色设计、角色定妆、表情参考、视频首帧。

2. RVC 音频工作流
   负责歌曲裁剪、人声分离、目标音色转换、干人声与最终混音输出。

3. LTX-2.3 视频工作流
   负责首帧动起来、音频驱动口型或后置 lip-sync、补帧、超分、视频导出。
```

推荐先让 3 条工作流保持相对独立。ComfyUI 负责图像和视频，RVC/UVR 负责音频，最终在剪辑软件中合成。等 MVP 跑稳后，再考虑把 RVC 节点也整合进 ComfyUI。

## AutoDL 环境建议

| 项目 | 建议 |
| --- | --- |
| GPU | RTX 5090 32GB |
| 磁盘 | 至少 300GB，后续建议 500GB |
| 系统 | Linux 镜像优先，Windows 也可但依赖排错成本更高 |
| ComfyUI | 最新版，优先使用 ComfyUI Manager 管理节点 |
| PyTorch/CUDA | RTX 50 系需要 CUDA 12.8+；如使用 NVFP4 加速，关注 cu130 环境 |
| 常用工具 | ffmpeg、git、aria2、huggingface-cli |

建议目录结构：

```text
project/
  00_sources/
    audio_original/
    lyrics/
    references/
  01_ip/
    prompts/
    character_sheet/
    first_frames/
    selected_refs/
  02_audio/
    vocal_raw/
    vocal_rvc/
    instrumental/
    dry_vocal_for_lipsync/
    final_mix/
  03_video/
    ltx_outputs/
    lipsync_outputs/
    upscale_outputs/
    final_exports/
  04_workflows/
    comfyui_ip/
    comfyui_ltx/
    rvc/
  05_logs/
    generation_notes.md
```

## MVP 路线

### 第 0 步：确定创意边界

先确定以下内容，避免后面反复返工：

| 项目 | 示例 |
| --- | --- |
| 歌曲片段 | 12 秒副歌 |
| 角色定位 | 18-22 岁虚拟歌姬、清冷、舞台感 |
| 视觉风格 | 写实二次元 / 半写实 / 3D 偶像 / 插画风 |
| 场景 | 舞台近景 / 直播间 / 暗色棚拍 / 城市夜景 |
| 镜头 | 胸像中近景，脸部和嘴部清晰 |
| 情绪 | 温柔、坚定、开心、伤感等 |

本阶段产出：

```text
00_sources/audio_original/clip_12s.wav
00_sources/lyrics/clip_lyrics.txt
01_ip/prompts/character_prompt_v1.md
```

## 工作流 1：虚拟 IP 生产工作流

### 目标

生成一个稳定、可复用的虚拟角色，并输出视频层可直接使用的首帧图。

MVP 阶段不强制训练 LoRA。先用 Flux 生成高质量角色定妆图和首帧，如果后续要系列化，再补角色 LoRA。

### 技术栈

| 类型 | 推荐 |
| --- | --- |
| 主模型 | FLUX.1 dev / FLUX.1 schnell / FLUX.2 klein 4B / FLUX.2 dev |
| ComfyUI 节点 | ComfyUI 原生 Flux 工作流、ComfyUI Manager |
| 可选节点 | Flux Kontext/Redux 类参考图编辑工作流、ControlNet Depth/Canny、Upscale 节点 |
| 可选训练 | Flux LoRA 训练工具，如 kohya/fluxgym/ComfyUI Flux Trainer |
| 输出格式 | PNG，保留 workflow metadata |

非商用兴趣创作可以先用 FLUX.1 dev 或 FLUX.2 dev 追求质量。如果未来要商用，提前确认模型许可，或者选择许可更宽松的模型，例如 FLUX.2 klein 4B。

### 具体做法

1. 编写角色设定卡

建议至少写清：

```text
角色名称：
年龄感：
发型发色：
眼睛特征：
服装：
妆容：
气质：
画风：
禁止变化项：
```

示例结构：

```text
角色是一个固定虚拟歌手 IP。银白色长发，浅蓝色眼睛，黑色短款舞台夹克，银色耳返，精致但自然的妆容。半写实二次元风格，脸部干净，五官稳定，舞台灯光，胸像中近景，面向镜头，嘴部清晰可见。
```

2. 生成角色候选图

建议先生成 20-40 张候选，不要一张图就进入视频。

评估标准：

| 项目 | 判断标准 |
| --- | --- |
| 脸 | 五官好记，正面识别度高 |
| 嘴 | 形状清楚，适合后续 lip-sync |
| 服装 | 不要过度复杂，避免视频生成时漂移 |
| 头发 | 不要太多细碎飞散发丝 |
| 背景 | 初期越简单越稳 |
| 构图 | 胸像或半身中近景 |

3. 固定角色参考集

从候选中选 1 张主参考图，再补充生成：

```text
01_ip/selected_refs/ref_front.png
01_ip/selected_refs/ref_smile.png
01_ip/selected_refs/ref_singing.png
01_ip/selected_refs/ref_closed_eyes.png
01_ip/selected_refs/ref_outfit.png
```

4. 生成视频首帧

首帧要为视频服务，不是单纯好看。

首帧建议：

| 项目 | 建议 |
| --- | --- |
| 构图 | 9:16，中近景，头顶和肩膀留空间 |
| 脸部 | 正脸或小角度侧脸，不超过 15 度 |
| 嘴部 | 不遮挡，不要拿麦克风挡嘴 |
| 手部 | MVP 阶段尽量不要把手放在脸旁 |
| 背景 | 舞台/直播间可以有，但不要过度复杂 |
| 光线 | 脸部清楚，嘴部不能在阴影里 |

输出：

```text
01_ip/first_frames/ip_v1_first_frame_720x1280.png
01_ip/prompts/ip_v1_prompt.md
05_logs/generation_notes.md
```

### IP 层验收标准

进入音视频层前，首帧至少满足：

```text
[ ] 角色脸部符合设定
[ ] 嘴部清晰无遮挡
[ ] 画面没有明显手指、眼睛、牙齿错误
[ ] 背景不会抢主体
[ ] 角色适合轻微运动，不依赖复杂姿势成立
[ ] prompt、seed、模型版本已记录
```

## 工作流 2：RVC 音频工作流

### 目标

把选定歌曲片段的人声转换为目标音色，并输出两个关键音频：

```text
dry_vocal.wav：干人声，用于 lip-sync
final_mix.wav：人声 + 伴奏，用于最终视频成片
```

### 技术栈

| 类型 | 推荐 |
| --- | --- |
| 人声分离 | UVR / Demucs |
| 声音转换 | RVC WebUI |
| F0 提取 | RMVPE 优先 |
| 音频处理 | Audition / Reaper / Audacity / ffmpeg |
| 可选 ComfyUI 节点 | ComfyUI-RVC、TTS-Audio-Suite |
| 输出格式 | WAV，建议 44.1kHz 或 48kHz |

MVP 阶段建议先用独立 RVC WebUI，不急着全部塞进 ComfyUI。音频链路独立调试更快，也更容易定位问题。

### 具体做法

1. 裁剪歌曲片段

裁剪一段 10-15 秒音频，尽量选择一句完整歌词或一段完整旋律。

输出：

```text
00_sources/audio_original/song_clip_12s.wav
```

2. 人声与伴奏分离

用 UVR 或 Demucs 分离：

```text
02_audio/vocal_raw/song_clip_vocal.wav
02_audio/instrumental/song_clip_instrumental.wav
```

建议检查：

```text
[ ] 人声里伴奏残留不严重
[ ] 伴奏里人声残留不明显
[ ] 音频没有爆音和明显相位问题
```

3. RVC 转换音色

RVC 推理建议：

| 参数 | MVP 建议 |
| --- | --- |
| 模型 | 先用现成 RVC 模型 |
| F0 method | RMVPE |
| transpose | 按目标音色性别和音域微调 |
| index rate | 0.5-0.8 起试 |
| protect | 0.3-0.5 起试 |
| filter radius | 3 起试 |

输出：

```text
02_audio/vocal_rvc/song_clip_rvc_vocal.wav
```

4. 制作 lip-sync 用干人声

对 RVC 后的人声做轻度处理即可：

```text
降噪 -> 音量标准化 -> 去掉明显爆音 -> 保留清晰咬字
```

不要给 lip-sync 干人声加太重混响、合唱、延迟或伴奏。

输出：

```text
02_audio/dry_vocal_for_lipsync/song_clip_dry_vocal.wav
```

5. 制作最终混音

将 RVC 人声和伴奏混合：

```text
RVC vocal + instrumental -> EQ -> compression -> light reverb -> limiter
```

输出：

```text
02_audio/final_mix/song_clip_final_mix.wav
```

### 音频层验收标准

进入视频层前，音频至少满足：

```text
[ ] dry_vocal.wav 人声清楚，伴奏残留很少
[ ] final_mix.wav 音量不过载
[ ] 歌词、节奏和原片段一致
[ ] RVC 音色没有严重电音、破音、金属感
[ ] dry_vocal.wav 和 final_mix.wav 时长完全一致
```

## 工作流 3：LTX-2.3 视频工作流

### 目标

用 IP 首帧和音频生成 10-15 秒唱歌视频，再通过 lip-sync、补帧、超分和剪辑完成成片。

MVP 阶段最稳路线：

```text
Flux 首帧 -> LTX-2.3 图生视频生成轻动作 -> lip-sync 精修 -> 补帧/超分 -> 剪辑合成
```

### 技术栈

| 类型 | 推荐 |
| --- | --- |
| 主视频模型 | LTX-2.3 |
| ComfyUI 节点 | ComfyUI-LTXVideo、VideoHelperSuite |
| 口型同步 | MuseTalk / LatentSync / Sonic / Wav2Lip，按实际效果选择 |
| 人脸修复 | CodeFormer / GFPGAN / Impact Pack，谨慎使用 |
| 补帧 | RIFE / FILM |
| 超分 | Real-ESRGAN / 4x-UltraSharp / 视频超分工具 |
| 后期 | Premiere / DaVinci Resolve / 剪映 |

### 推荐生成策略

第一条视频不要直接挑战复杂动作。建议：

```text
single female virtual singer, singing to camera, subtle facial expression, natural blinking, slight head movement, gentle shoulder rhythm, slow camera push in, stable face, clear mouth, soft stage lighting
```

避免：

```text
large dance movement
fast camera rotation
turning around
hands covering mouth
extreme close-up
crowded background
multiple people
```

### 具体做法

1. 准备输入

```text
01_ip/first_frames/ip_v1_first_frame_720x1280.png
02_audio/dry_vocal_for_lipsync/song_clip_dry_vocal.wav
02_audio/final_mix/song_clip_final_mix.wav
```

2. LTX-2.3 图生视频

使用 ComfyUI-LTXVideo 的 Image-to-Video 工作流。

MVP 建议：

| 项目 | 建议 |
| --- | --- |
| 模型 | 先用 distilled / FP8 快速迭代，满意后再尝试 full |
| 分辨率 | 540x960 或 720x1280 起步 |
| 时长 | 先测 5-8 秒，再扩到 10-15 秒 |
| 动作 | 轻动作 |
| 镜头 | 轻推近或轻微手持感 |
| 人物 | 单人中近景 |

输出：

```text
03_video/ltx_outputs/ip_v1_ltx_motion_test.mp4
```

3. 检查 LTX 输出

检查重点：

```text
[ ] 脸没有明显漂移
[ ] 嘴部区域没有崩坏
[ ] 头发和服装没有大幅变化
[ ] 动作自然，不像冻结照片
[ ] 镜头运动不会导致主体跑出画面
```

如果 LTX 输出的口型已经可用，可以直接进入后期。如果口型不准，进入 lip-sync 精修。

4. lip-sync 精修

将 LTX 生成的视频和 `dry_vocal.wav` 输入 lip-sync 节点或独立工具。

工具选择建议：

| 工具 | 适合场景 |
| --- | --- |
| MuseTalk | 脸部清楚、追求较好实时性和稳定口型 |
| LatentSync | 希望扩散式口型质量更自然，但可能更吃资源 |
| Sonic | 图像/视频唱歌口型尝试，可作为备选 |
| Wav2Lip | 老牌方案，速度快，但画质和兼容性可能需要后处理 |

输出：

```text
03_video/lipsync_outputs/ip_v1_lipsync.mp4
```

5. 补帧与超分

建议先做口型，再做补帧/超分。

```text
lip-sync video -> RIFE/FILM 补帧 -> 视频超分 -> 轻微锐化/降噪
```

输出：

```text
03_video/upscale_outputs/ip_v1_1080x1920_30fps.mp4
```

6. 剪辑软件合成

在专业剪辑软件中：

```text
导入最终视频
替换音频为 final_mix.wav
手动对齐音画
添加歌词字幕
调色
节奏点剪辑
导出 1080x1920
```

最终输出：

```text
03_video/final_exports/ip_v1_singing_clip_final.mp4
```

### 视频层验收标准

```text
[ ] 角色基本像同一个人
[ ] 口型与歌词大致同步
[ ] 没有严重脸崩、牙齿崩、眼睛乱跳
[ ] 动作有生命感，但不夸张
[ ] 音画同步
[ ] 最终音频为 final_mix.wav
[ ] 成片分辨率和平台比例正确
```

## 第一条 MVP 推荐执行清单

按这个顺序执行：

```text
1. 选 12 秒歌曲片段
2. 写角色设定卡
3. Flux 生成 20-40 张角色候选图
4. 选 1 张主参考图
5. 生成 1 张 9:16 唱歌首帧
6. UVR/Demucs 分离人声和伴奏
7. RVC 转换目标音色
8. 输出 dry_vocal.wav 和 final_mix.wav
9. LTX-2.3 生成 5-8 秒测试视频
10. 满意后扩展到 10-15 秒
11. 用 MuseTalk/LatentSync 等做 lip-sync 精修
12. 补帧、超分
13. 剪辑软件替换 final_mix.wav，加字幕和调色
14. 导出第一版成片
15. 记录问题，进入第二轮迭代
```

## 迭代方向

第一版跑通后，再按收益从高到低迭代：

| 优先级 | 方向 | 说明 |
| --- | --- | --- |
| P0 | 音频质量 | RVC 音色自然度直接影响观感 |
| P0 | 首帧质量 | 首帧越稳，视频越稳 |
| P1 | 口型工具选择 | 对同一段干人声测试 MuseTalk/LatentSync/Sonic |
| P1 | 视频 prompt | 找到最适合该角色的动作描述 |
| P1 | 镜头拆分 | 15 秒可拆成 2 个 6-8 秒镜头 |
| P2 | 角色 LoRA | 当你要连续生产同一个 IP 时再训练 |
| P2 | 舞台和运镜 | 在角色稳定后再增强视觉冲击 |
| P2 | 自动化 | 用 ComfyUI API 批量跑 seed 和参数 |

## 常见风险与处理

| 问题 | 可能原因 | 处理 |
| --- | --- | --- |
| 角色变脸 | 首帧不稳、动作太大、时长太长 | 缩短时长，减少运镜，使用更清晰正脸首帧 |
| 嘴型不准 | 伴奏干扰、干人声混响太重 | lip-sync 使用 dry_vocal，不用 final_mix |
| 牙齿崩坏 | 嘴部区域太小或模型不稳定 | 放大脸部占比，换 lip-sync 工具，做局部修复 |
| 画面像静态图 | LTX 动作提示太弱 | 增加 gentle head movement、natural blinking、subtle shoulder rhythm |
| 画面崩坏 | 动作提示太强或镜头太复杂 | 降低动作幅度，减少背景复杂度 |
| 显存不足 | full 模型/高分辨率/长帧数 | 用 FP8/distilled，降低分辨率，短段生成 |
| 磁盘爆满 | 模型和输出缓存过多 | 定期清理中间输出，模型分目录管理 |

## 每次生成必须记录

在 `05_logs/generation_notes.md` 中记录：

```text
日期：
目标：
歌曲片段：
角色版本：
首帧文件：
音频文件：
ComfyUI 工作流：
模型版本：
关键参数：
seed：
输出文件：
问题：
下一轮修改：
```

这个记录非常重要。AI 视频调参不是一次成功的事情，能复现好结果比单次碰运气更值钱。

## 参考链接

- ComfyUI LTX-2.3 官方示例：https://docs.comfy.org/tutorials/video/ltx/ltx-2-3
- LTX ComfyUI 集成文档：https://docs.ltx.video/open-source-model/integration-tools/comfy-ui
- LTX Image-to-Video 文档：https://docs.ltx.video/open-source-model/usage-guides/image-to-video
- ComfyUI RTX 5090 支持说明：https://blog.comfy.org/p/how-to-get-comfyui-running-on-your
- FLUX.2 官方仓库与许可说明：https://github.com/black-forest-labs/flux2
- RVC 官方仓库：https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- MuseTalk 官方仓库：https://github.com/TMElyralab/MuseTalk
