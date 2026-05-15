# 开发进度记录

## 项目目标

搭建一个虚拟 IP 唱歌视频 MVP 生产链路，先完成 10-15 秒非商用兴趣向歌曲片段。

核心工作流：

```text
1. 虚拟 IP 生产工作流
2. RVC 音频工作流
3. LTX-2.3 + lip-sync 视频工作流
```

## 当前阶段

```text
阶段：RVC 专属音色训练
状态：第一版 qtfy_v1_40min 已完成 100 epochs 训练并生成模型/index；RVC WebUI-6008 已启动，下一步用该模型跑 16 秒转换试听，满意后继续 LTX-2.3 视频 smoke/full
日期：2026-05-15
```

## 进度总览

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| MVP 路线文档 | 已完成 | 已生成 `virtual_ip_singing_video_mvp.md` |
| AutoDL 虚拟 IP 搭建文档 | 已完成 | 已生成 `docs/autodl_virtual_ip_workflow_setup.md` |
| AutoDL 环境侦察报告 | 已完成 | 已生成 `docs/autodl_environment_report.md` |
| AutoDL 通用安装脚本 | 已完成 | 已生成 `scripts/setup_autodl_virtual_ip.sh`，当前实例不使用 |
| AutoDL 现有 ComfyUI 配置脚本 | 已完成 | 已生成 `scripts/setup_autodl_existing_comfyui_virtual_ip.sh` |
| AutoDL 验证脚本 | 已完成 | 已生成 `scripts/verify_autodl_virtual_ip.sh` |
| 角色设定卡模板 | 已完成 | 已生成 `prompts/ip_character_card_template.md` |
| AutoDL 实例侦察 | 已完成 | Ubuntu 22.04 / RTX 5090 / ComfyUI 0.3.67 |
| ComfyUI 启动验证 | 已完成 | 使用 AutoDL WebUI-6006，不改端口 |
| Flux 模型接入 | 已完成 | 使用公共模型盘软链接，不复制大文件 |
| Flux 出图 smoke test | 已完成 | 已生成 `remote_outputs/flux1_dev_smoke_00001_.png` |
| 示例角色设定卡 | 已完成 | 已生成 `prompts/ip_character_card_luna_v1.md` |
| Nova Orange XL 调研 | 已完成 | 确认为 Illustrious Checkpoint Merge，不是 Flux |
| Nova Orange XL 工作流骨架 | 已完成 | 已生成 `workflows/ip/nova_orange_xl_illustrious_text2image_ui_workflow.json` |
| 大模型上传脚本 | 已完成 | 已生成 `scripts/upload_large_model_to_autodl.py`，支持 SFTP 断点续传 |
| 角色候选图生成 | 已完成初版 | 用户已用 Nova Orange XL 得到满意候选图 |
| 角色首帧输出 | 已完成初版 | 可作为后续视频首帧基准 |
| RVC 音频环境 | 已完成 | AutoDL 已创建 `rvc` conda 环境并安装 RVC / Demucs / ffmpeg |
| RVC 音频脚本 | 已完成 | 已生成 `scripts/audio/*.sh` 和歌曲片段裁剪工具 |
| RVC 音频工作流文档 | 已完成 | 已生成 `docs/rvc_audio_workflow_setup.md` |
| RVC WebUI 启动验证 | 已完成 | 临时启动 6008 并确认 HTTP 200，测试后已停止 |
| RVC 基础模型上传 | 已完成 | `hubert_base.pt`、`rmvpe.pt` 已放入 RVC assets |
| RVC 音色模型同步 | 已完成 | `misono-mika.pth/.index` 已软链接到 RVC assets |
| 首个歌曲片段分离 | 已完成 | Demucs 已输出 `vocals.wav` 和 `no_vocals.wav` |
| 首个歌曲片段 RVC 转换 | 已完成 | 已从 Gradio 临时输出归档 RVC 人声 |
| 第一版音频混音 | 已完成 | 已输出 16 秒 `final_mix.wav` |
| 第一版专属 RVC 模型 | 已完成 | `qtfy_v1_40min.pth` 和配套 index 已训练完成并放入 RVC assets |
| LTX-2.3 custom nodes | 已完成 | 已安装 ComfyUI-LTXVideo / VideoHelperSuite / ComfyMath |
| ComfyUI 更新 | 已完成 | 已更新到支持 LTX-2.3 AV 节点的版本 |
| LTX-2.3 视频工作流 | 已完成骨架 | 已生成 5 秒 smoke 和 16 秒 full 两个工作流 |
| LTX-2.3 模型下载 | 已完成 | checkpoint、Gemma text encoder、LoRA、latent upscaler 均已就位 |
| 第一段唱歌视频生成 | 待开始 | 先跑 5 秒 smoke，再跑 16 秒 full |
| 工作流使用手册 | 已完成初版 | 已生成 `docs/vip_singing_workflow_usage_guide.md`，视频章节待 smoke 跑通后补全 |

## 本次开发记录

### 2026-05-08

目标：

```text
开始准备并实际搭建 AutoDL 虚拟 IP 生产工作流。
```

完成：

```text
[x] 明确三条工作流仍然是：虚拟 IP、RVC、LTX-2.3 视频
[x] 先从虚拟 IP 生产工作流开始
[x] 创建 AutoDL 搭建资料与脚本
[x] 登录 AutoDL 并只读侦察环境
[x] 确认实例自带 /root/ComfyUI
[x] 确认 ComfyUI 正在 WebUI-6006 对应的 127.0.0.1:6006 运行
[x] 未修改启动脚本和端口映射
[x] 创建远端项目目录 /root/autodl-tmp/vip_singing
[x] 从 AutoDL 公共模型盘软链接 Flux 模型
[x] 通过 ComfyUI API 确认 Flux 节点和模型可见
[x] 通过 FLUX.1-dev 跑通 512x768 smoke test
[x] 下载 smoke test 图到本地 remote_outputs/
[x] 调用 ComfyUI `/free` 尝试释放模型缓存；未重启服务，ComfyUI 进程仍保留约 21GB CUDA 显存
[x] 创建可导入 ComfyUI UI 的 Flux 文生图 workflow 起点
[x] 通过 ComfyUI `/userdata` 接口注册 workflow 到 UI 工作流面板
[x] 创建 Luna v1 示例角色设定卡，并提炼候选图/首帧 prompt
[x] 调研 Civitai Nova Orange XL 模型类型和推荐参数
[x] 创建 Nova Orange XL / Illustrious 专用 ComfyUI 工作流骨架
[x] 创建大模型上传到 AutoDL 的断点续传脚本和说明文档
[x] 用户决定稍后自行上传 Nova Orange XL，已停止上传并清理远端 `.part/.scp.part` 半成品
[x] 为 Luna v1 增加 Nova Orange XL 高机位舞台构图 prompt
```

生成和更新文件：

```text
virtual_ip_singing_video_mvp.md
docs/autodl_virtual_ip_workflow_setup.md
docs/autodl_environment_report.md
scripts/setup_autodl_virtual_ip.sh
scripts/setup_autodl_existing_comfyui_virtual_ip.sh
scripts/verify_autodl_virtual_ip.sh
prompts/ip_character_card_template.md
prompts/ip_character_card_luna_v1.md
workflows/ip/flux1_dev_virtual_ip_text2image_ui_workflow.json
workflows/ip/nova_orange_xl_illustrious_text2image_ui_workflow.json
docs/civitai_nova_orange_xl_setup.md
docs/large_model_upload_to_autodl.md
scripts/upload_large_model_to_autodl.py
DEVELOPMENT_PROGRESS.md
remote_outputs/flux1_dev_smoke_00001_.png
```

远端关键文件：

```text
/root/autodl-tmp/vip_singing/README.md
/root/autodl-tmp/vip_singing/prompts/ip_character_card_template.md
/root/autodl-tmp/vip_singing/logs/generation_notes.md
/root/autodl-tmp/vip_singing/workflows/ip/flux1_dev_smoke_api_workflow.json
/root/ComfyUI/user/default/workflows/VIP/IP/Flux1_DEV_Virtual_IP_Text2Image.json
/root/autodl-tmp/vip_singing/outputs/ip_candidates/flux1_dev_smoke_00001_.png
```

下一步：

```text
1. 通过 AutoDL WebUI-6006 打开 ComfyUI
2. 在左侧“工作流”面板刷新，打开 `VIP/IP/Flux1_DEV_Virtual_IP_Text2Image.json`
3. 如果改用 Nova Orange XL，先上传 `novaOrangeXL_exV20.safetensors` 到 `/root/ComfyUI/models/checkpoints/`
4. 在左侧“工作流”面板打开 `VIP/IP/Nova_Orange_XL_Illustrious_Text2Image.json`
5. 根据角色设定卡生成第一轮 20-40 张 IP 候选
6. 选出 1 张主参考图
7. 生成 9:16 视频首帧
8. 记录 prompt、seed、模型、输出路径
```

### 2026-05-09

目标：

```text
搭建第二条 RVC 音频工作流，并整理成可复用脚本和文档。
```

完成：

```text
[x] 登录 AutoDL 并复查实例状态、磁盘空间、ComfyUI 6006 进程
[x] 未修改 ComfyUI 启动脚本，未修改 AutoDL 端口映射
[x] 创建 /root/autodl-tmp/vip_singing/audio_workflow
[x] 克隆 RVC-Project/Retrieval-based-Voice-Conversion-WebUI
[x] 创建 conda 环境 rvc，Python 3.10.20
[x] 安装 torch 2.11.0+cu128，并确认 RTX 5090 CUDA 可用
[x] 安装 RVC requirements，保留 pip 23.3.2 以兼容旧依赖
[x] 安装 Demucs 4.0.1 和 ffmpeg
[x] 修正 gradio 3.34.0 与 gradio_client 的兼容问题，固定 gradio_client 0.2.9
[x] 创建 RVC WebUI 6008 启动脚本
[x] 创建 RVC 音色模型软链接同步脚本
[x] 创建 Demucs 人声/伴奏分离脚本
[x] 创建 RVC 人声与伴奏混音脚本
[x] 创建音频工作流 smoke check 脚本
[x] 生成 RVC 音频工作流搭建文档
[x] 临时启动 RVC WebUI 6008 并确认 HTTP 200，测试后已停止进程
```

生成和更新文件：

```text
docs/rvc_audio_workflow_setup.md
scripts/audio/start_rvc_webui.sh
scripts/audio/sync_rvc_model_assets.sh
scripts/audio/separate_vocals_demucs.sh
scripts/audio/mix_rvc_with_instrumental.sh
scripts/audio/rvc_audio_smoke_check.sh
DEVELOPMENT_PROGRESS.md
```

远端关键文件：

```text
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI
/root/autodl-tmp/vip_singing/audio_workflow/scripts/start_rvc_webui.sh
/root/autodl-tmp/vip_singing/audio_workflow/scripts/sync_rvc_model_assets.sh
/root/autodl-tmp/vip_singing/audio_workflow/scripts/separate_vocals_demucs.sh
/root/autodl-tmp/vip_singing/audio_workflow/scripts/mix_rvc_with_instrumental.sh
/root/autodl-tmp/vip_singing/audio_workflow/scripts/rvc_audio_smoke_check.sh
```

下一步：

```text
1. 用户下载并上传 hubert_base.pt
2. 用户下载并上传 rmvpe.pt
3. 用户上传一个可测试的 RVC 音色模型 .pth 和 .index
4. 执行 sync_rvc_model_assets.sh
5. 启动 WebUI-6008，跑通首个 10-15 秒音频片段
```

### 2026-05-11

目标：

```text
接入用户已上传的 RVC 基础模型和音色模型，启动 RVC WebUI。
```

完成：

```text
[x] 确认 `hubert_base.pt` 已存在于 `assets/hubert/`
[x] 确认 `rmvpe.pt` 已存在于 `assets/rmvpe/`
[x] 确认用户已上传 `misono-mika.pth` 和 `misono-mika.index`
[x] 修正 `sync_rvc_model_assets.sh`，同时支持模型直接放在 `input/rvc_models/` 根目录和子目录
[x] 将 `misono-mika.pth` 软链接到 `assets/weights/`
[x] 将 `misono-mika.index` 软链接到 `assets/indices/`
[x] 运行 RVC smoke check：Hubert present，RMVPE present，voice pth count 1，voice index count 1
[x] 重启 RVC WebUI-6008，确认 HTTP ready
[x] 新增本地歌曲片段裁剪工具 `scripts/audio/prepare_song_clip.py`，可将完整歌曲转为 10-15 秒 WAV
[x] 更新 `docs/rvc_audio_workflow_setup.md`，补充裁剪歌曲片段的使用方式
[x] 远端修复当前 shell 的 TorchCodec 动态库加载：设置 `LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH`
[x] Demucs 已成功分离 `045b_5553_0309_3129f6561cb9489b66e84c5eb53c3a4d_clip_27s_16s.wav`
[x] 已生成 16 秒 `vocals.wav` 和 `no_vocals.wav`
[x] 修正本地 `start_rvc_webui.sh`，强制使用 `/root/miniconda3/envs/rvc/bin/python`，避免误用 base Python
[x] 远端已用 rvc 绝对 Python 路径启动 RVC WebUI-6008，HTTP 200
[x] 远端修复 PyTorch 2.6+ `weights_only=True` 与 fairseq HuBERT 加载不兼容问题
[x] 远端重启 RVC WebUI-6008，确认 HTTP 200
[x] 用户通过 RVC WebUI 成功生成 misono-mika 转换后人声
[x] 将 Gradio 临时音频归档为 `/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/045b_clip_27s_16s_misono_mika_rvc.wav`
[x] 已将 RVC 人声与 Demucs 伴奏混音为 `/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/045b_clip_27s_16s_misono_mika_final_mix.wav`
[x] 确认 RVC 人声时长 15.98 秒，最终混音时长 16.00 秒
[x] 新增并上传 `archive_latest_rvc_and_mix.sh`，用于自动归档最新 RVC WebUI 输出并混音
```

当前 RVC WebUI：

```text
端口：6008
进程：python infer-web.py --port 6008 --pycmd python --noautoopen
音色模型：misono-mika
```

下一步：

```text
1. 打开 AutoDL WebUI-6008
2. 用 `scripts/audio/prepare_song_clip.py` 将完整歌曲裁成 10-15 秒 WAV
3. 上传或选择 10-15 秒歌曲片段
4. Demucs 已分离 vocals/no_vocals
5. RVC WebUI 已完成 misono-mika 转换
6. 已将转换后人声与 no_vocals.wav 混音
7. 下载或试听 `final_mix.wav`，判断音色自然度和伴奏/人声音量比例
8. 如果音频可接受，进入 LTX-2.3 视频工作流
```

### 2026-05-12

目标：

```text
搭建第三条 LTX-2.3 + lip-sync 视频工作流，使用首帧图和 RVC 人声生成唱歌视频。
```

完成：

```text
[x] 确认 ComfyUI 6006 仍按 AutoDL 原入口运行
[x] 确认首帧图、RVC dry vocal、final_mix 三个素材已在服务器
[x] 下载官方 LTX-2.3 Image Audio to Video 工作流模板
[x] 安装 ComfyUI-LTXVideo、ComfyUI-VideoHelperSuite、ComfyMath
[x] 更新 ComfyUI 到支持 LTX-2.3 AV 节点的版本
[x] 重启 ComfyUI，仍使用 127.0.0.1:6006
[x] 确认 LTX-2.3 IA2V 所需核心节点已加载
[x] 生成 Luna 专用 5 秒 smoke 工作流
[x] 生成 Luna 专用 16 秒 full 工作流
[x] 创建 LTX-2.3 模型下载脚本
[x] 创建视频输入素材软链接脚本
[x] 创建最终混音替换视频音频脚本
[x] 创建 LTX-2.3 视频环境检查脚本
[x] 创建三层工作流统一使用手册初版
[x] 展平 LTX-2.3 视频工作流，修复 Group Node 执行时报 `#340:287 has no class_type`
```

生成和更新文件：

```text
docs/ltx23_video_workflow_setup.md
docs/vip_singing_workflow_usage_guide.md
scripts/video/prepare_ltx23_video_inputs.sh
scripts/video/download_ltx23_models.sh
scripts/video/mux_final_audio.sh
scripts/video/check_ltx23_video_setup.sh
workflows/video/ltx_2_3_image_audio_to_video_official.json
workflows/video/ltx_2_3_ia2v_smoke_5s_workflow.json
workflows/video/ltx_2_3_ia2v_full_16s_workflow.json
workflows/video/ltx_2_3_ia2v_luna_smoke_5s_workflow.json
workflows/video/ltx_2_3_ia2v_luna_full_16s_workflow.json
DEVELOPMENT_PROGRESS.md
```

远端关键文件：

```text
/root/autodl-tmp/vip_singing/video_workflow/scripts/
/root/autodl-tmp/vip_singing/video_workflow/workflows/
/root/ComfyUI/user/default/workflows/VIP/Video/LTX_2_3_IA2V_Smoke_5s.json
/root/ComfyUI/user/default/workflows/VIP/Video/LTX_2_3_IA2V_Full_16s.json
```

下一步：

```text
1. 将选中的首帧图放入 `/root/autodl-tmp/vip_singing/assets/first_frames/`
2. 执行 `prepare_ltx23_video_inputs.sh`，同步首帧图和音频到 ComfyUI input 目录
3. 打开 `VIP/Video/LTX_2_3_IA2V_Smoke_5s.json`
4. 在 `Load Image` 和 `Load Audio` 节点中选择本次 IP 首帧和 RVC dry vocal
5. 先跑 5 秒 smoke
6. 再跑 16 秒 full
7. 用 final_mix 替换 LTX 输出视频中的驱动人声音频
```

### 2026-05-15

目标：

```text
整理 30-50 分钟专属人声训练集，并完成第一版自有 RVC 音色模型训练。
```

完成：

```text
[x] 本地从视频素材分离并整理出约 41 分钟干净人声训练集
[x] 将训练集上传到 AutoDL 的 RVC 训练数据目录
[x] 本地下载 pretrained_v2/f0G40k.pth 和 f0D40k.pth，并上传到远端 RVC assets
[x] 远端修复 Matplotlib FigureCanvasAgg.tostring_rgb() 兼容问题
[x] 使用 RVC v2 / 40k / f0 / rmvpe / batch size 12 / 100 epochs 完成训练
[x] 构建 qtfy_v1_40min 配套 FAISS index
[x] 最终模型和 index 已放入 RVC WebUI assets
[x] 重启 RVC WebUI-6008，并确认可用于加载新模型
[x] 新增本地视频提取 RVC-ready WAV 的脚本 `scripts/audio/prepare_video_audio_clip.py`
[x] 更新 RVC 音频工作流文档，补充视频提取音频和专属模型训练结果
```

生成和更新文件：

```text
docs/rvc_audio_workflow_setup.md
scripts/audio/prepare_video_audio_clip.py
DEVELOPMENT_PROGRESS.md
```

远端关键文件：

```text
/root/autodl-tmp/vip_singing/audio_workflow/input/rvc_train_datasets/qtfy_v1_40min
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/weights/qtfy_v1_40min.pth
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/assets/indices/qtfy_v1_40min_IVF2618_Flat_nprobe_1_qtfy_v1_40min_v2.index
/root/autodl-tmp/vip_singing/audio_workflow/tools/Retrieval-based-Voice-Conversion-WebUI/logs/qtfy_v1_40min/
/root/autodl-tmp/vip_singing/audio_workflow/logs/qtfy_v1_40min_train_pipeline.log
```

下一步：

```text
1. 打开 AutoDL WebUI-6008
2. 点击 Refresh voice list and index path
3. 选择 `qtfy_v1_40min.pth` 和对应 `.index`
4. 用同一段 16 秒 vocals.wav 做转换试听
5. 与 no_vocals.wav 混音，对比 misono-mika 与 qtfy_v1_40min 的自然度
6. 如果音色稳定，将 qtfy_v1_40min 作为后续 LTX-2.3 dry vocal 驱动音频
```

## 决策记录

| 日期 | 决策 | 原因 |
| --- | --- | --- |
| 2026-05-08 | MVP 阶段暂不训练 LoRA | 10-15 秒片段先验证闭环，首帧质量比训练更关键 |
| 2026-05-08 | 三条工作流相对独立 | 降低排错难度，先把图像、音频、视频分别跑通 |
| 2026-05-08 | 当前 AutoDL 实例复用 `/root/ComfyUI` | 实例已自带 ComfyUI 纯净版并映射到 WebUI-6006 |
| 2026-05-08 | 不修改端口和启动脚本 | 保持 AutoDL 页面访问方式稳定 |
| 2026-05-08 | Flux 模型使用公共模型盘软链接 | 节省磁盘空间并减少下载时间 |
| 2026-05-08 | FLUX.1-dev 作为首轮 IP 质量路线 | 非商用兴趣创作，优先定妆质量 |
| 2026-05-08 | 不重启 ComfyUI 释放显存 | 避免影响 AutoDL WebUI-6006 的访问稳定性 |
| 2026-05-08 | 工作流需注册到 ComfyUI 用户目录 | 前端“工作流”面板不会自动扫描项目目录 `/root/autodl-tmp/vip_singing/workflows` |
| 2026-05-08 | Nova Orange XL 使用 Checkpoint 工作流 | 该模型是 Illustrious Checkpoint Merge，不适合放入 Flux 的 UNETLoader |
| 2026-05-08 | 暂停本次本地到 AutoDL 的大模型上传 | 当前网络链路上传 6.46GB 文件过慢，用户决定回家后再上传 |
| 2026-05-09 | RVC 使用独立 conda 环境 `rvc` | 避免污染 ComfyUI 自带 Python 环境 |
| 2026-05-09 | RVC WebUI 预留使用 6008 | AutoDL 页面已有 WebUI-6008 入口，不改现有 6006 ComfyUI |
| 2026-05-09 | 音频分离优先使用 Demucs | 比先折腾 UVR5 更适合作为 MVP 人声/伴奏分离起点 |
| 2026-05-09 | 暂不训练自有 RVC 音色 | 先用现成模型跑通歌曲片段闭环，再替换成自训练音色 |
| 2026-05-11 | RVC 音色模型同步脚本同时支持根目录和子目录 | 用户实际将 `.pth/.index` 直接放在 `input/rvc_models/` 根目录，脚本需兼容这种轻量测试方式 |
| 2026-05-12 | lip-sync 驱动使用 RVC dry vocal，最终发布音频使用 final_mix | 干声驱动口型更稳，成片仍保留伴奏混音 |
| 2026-05-12 | LTX-2.3 先跑 5 秒 smoke，再跑 16 秒 full | 降低首次视频生成的排错成本和显存/时间风险 |
| 2026-05-12 | 为 LTX-2.3 更新 ComfyUI，但保留 6006 访问方式 | 原 ComfyUI 版本缺 LTX-AV 核心模块，更新是运行 IA2V 的必要条件 |
| 2026-05-12 | 将 LTX-2.3 工作流从 Group Node 展平为普通节点 | 当前 ComfyUI 前端提交 Group Node 时会把内部节点作为缺少 `class_type` 的执行节点，导致 `#340:287` 报错 |
| 2026-05-13 | 视频工作流改为通用输入目录 | 支持 Luna、Zeta、Alpha 等多 IP 首帧在 `Load Image` 下拉选择，不再绑定固定 `luna_v1_first_frame.png` |
| 2026-05-15 | 第一版自训练 RVC 使用约 41 分钟干净人声、RVC v2 / 40k / rmvpe / 100 epochs | 先得到稳定可用的专属音色基线，再决定是否继续清洗素材或增加 epochs |

## 待确认事项

```text
[x] AutoDL 镜像版本：ComfyUI 纯净版
[x] CUDA / PyTorch 版本：Driver CUDA 13.0，PyTorch 2.8.0+cu128
[x] 是否能正常访问 ComfyUI：WebUI-6006
[x] 首选 Flux 版本：FLUX.1-dev 作为 IP 质量路线，FLUX.2-klein-base-4B 作为轻量备选
[x] 模型接入方式：AutoDL 公共模型盘软链接
[ ] ComfyUI 进程当前仍可能保留 FLUX.1-dev 显存缓存，后续如需完全释放再手动重启 ComfyUI
[x] 第一轮虚拟 IP 角色设定
[x] 第一轮角色候选图已得到满意候选
[x] 第一张 9:16 唱歌视频首帧已有初版基准
[x] 上传 RVC `hubert_base.pt`
[x] 上传 RVC `rmvpe.pt`
[x] 上传一个 RVC 音色模型 `.pth/.index`
[x] RVC WebUI-6008 启动并可访问
[x] 跑通第一段歌曲片段 Demucs 人声/伴奏分离
[x] 跑通第一段 RVC 音色转换
[x] 输出第一版 RVC dry vocal 和 `final_mix.wav`
[x] 试听第一版 RVC 音频，决定进入视频工作流
[x] 整理 30-50 分钟 RVC 专属训练素材
[x] 跑通第一版专属 RVC 模型训练
[ ] 使用 `qtfy_v1_40min` 跑通第一段 16 秒 RVC 转换试听
[x] 进入 LTX-2.3 + lip-sync 视频工作流
[x] 安装 LTX-2.3 视频 custom nodes
[x] 更新 ComfyUI 以支持 LTX-2.3 AV 节点
[x] 下载 LTX-2.3 模型文件
[ ] 跑通 5 秒 LTX-2.3 IA2V smoke 视频
[ ] 跑通 16 秒 LTX-2.3 IA2V 完整视频
```
