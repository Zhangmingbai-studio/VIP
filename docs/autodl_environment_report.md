# AutoDL 环境侦察报告

日期：2026-05-08

## 实例信息

```text
Host: autodl-pro-7782f2d5c62b
OS: Ubuntu 22.04.5 LTS
GPU: NVIDIA GeForce RTX 5090 32GB
NVIDIA Driver: 580.76.05
Driver CUDA: 13.0
PyTorch: 2.8.0+cu128
Python: /root/miniconda3/bin/python 3.12.3
ComfyUI: /root/ComfyUI
ComfyUI version: 0.3.67
ComfyUI process: /root/miniconda3/bin/python main.py --port 6006 --listen 127.0.0.1
```

## 关键结论

这台 AutoDL 实例已经是 **ComfyUI 纯净版**，无需重新安装 ComfyUI。

当前 AutoDL 页面上的 WebUI-6006 对应：

```text
127.0.0.1:6006 -> /root/ComfyUI
```

因此本实例的搭建策略是：

```text
[x] 复用 /root/ComfyUI
[x] 不修改 /root/start-comfyui.sh
[x] 不修改 AutoDL 端口映射
[x] 不另开 8188 服务
[x] 从 AutoDL 公共模型盘软链接 Flux 模型，避免复制大文件
```

## 磁盘和目录

```text
根盘：约 295GB
当前可用：约 293GB
项目目录：/root/autodl-tmp/vip_singing
公共模型盘：/.autodl-model/data
```

## 已发现公共 Flux 模型

```text
/.autodl-model/data/black-forest-labs/FLUX.1-dev/flux1-dev.safetensors
/.autodl-model/data/black-forest-labs/FLUX.1-dev/ae.safetensors
/.autodl-model/data/comfyanonymous/flux_text_encoders/clip_l.safetensors
/.autodl-model/data/comfyanonymous/flux_text_encoders/t5xxl_fp16.safetensors
/.autodl-model/data/black-forest-labs/FLUX.2-klein-base-4B/flux-2-klein-base-4b.safetensors
/.autodl-model/data/black-forest-labs/FLUX.2-klein-base-4B/vae/diffusion_pytorch_model.safetensors
```

## 已创建软链接

```text
/root/ComfyUI/models/diffusion_models/flux1-dev.safetensors
/root/ComfyUI/models/diffusion_models/flux-2-klein-base-4b.safetensors
/root/ComfyUI/models/text_encoders/clip_l.safetensors
/root/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors
/root/ComfyUI/models/vae/ae.safetensors
/root/ComfyUI/models/vae/flux2-klein-vae.safetensors
```

## ComfyUI API 验证

ComfyUI 已识别以下节点和模型：

```text
UNETLoader: flux1-dev.safetensors, flux-2-klein-base-4b.safetensors
DualCLIPLoader: clip_l.safetensors, t5xxl_fp16.safetensors
VAELoader: ae.safetensors, flux2-klein-vae.safetensors
FluxGuidance: available
KSampler / VAEDecode / SaveImage: available
```

## Smoke Test

已通过 ComfyUI API 运行 FLUX.1-dev 小图 smoke test：

```text
Model: flux1-dev.safetensors
Weight dtype: fp8_e4m3fn
Resolution: 512x768
Steps: 8
Seed: 260508001
Output on AutoDL: /root/autodl-tmp/vip_singing/outputs/ip_candidates/flux1_dev_smoke_00001_.png
Local copy: remote_outputs/flux1_dev_smoke_00001_.png
```

结果：成功出图，工作流链路可用。

## 收尾状态

Smoke test 后调用过 ComfyUI `/free` 接口，接口返回成功；但 ComfyUI 进程仍保留约 21GB CUDA 显存缓存。为了保持 AutoDL WebUI-6006 访问稳定，没有重启 ComfyUI。

后续如果需要完全释放显存，可以在确认不影响操作时手动重启 ComfyUI 或重启实例。
