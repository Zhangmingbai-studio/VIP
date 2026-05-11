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
阶段：RVC 音频工作流
状态：Hubert/RMVPE 和 misono-mika RVC 音色模型已接入，RVC WebUI-6008 已启动
日期：2026-05-11
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
| RVC 音频脚本 | 已完成 | 已生成 `scripts/audio/*.sh` |
| RVC 音频工作流文档 | 已完成 | 已生成 `docs/rvc_audio_workflow_setup.md` |
| RVC WebUI 启动验证 | 已完成 | 临时启动 6008 并确认 HTTP 200，测试后已停止 |
| RVC 基础模型上传 | 已完成 | `hubert_base.pt`、`rmvpe.pt` 已放入 RVC assets |
| RVC 音色模型同步 | 已完成 | `misono-mika.pth/.index` 已软链接到 RVC assets |
| 首个歌曲片段转换 | 待开始 | 上传音频和音色模型后执行 |

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
2. 上传或选择 10-15 秒歌曲片段
3. 先用 Demucs 分离 vocals/no_vocals
4. 在 RVC WebUI 中用 misono-mika 转换 vocals.wav
5. 将转换后人声与 no_vocals.wav 混音
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
[ ] 跑通第一段 10-15 秒 RVC 音频转换
```
