# LTX-2.3 视频工作流搭建记录

## 目标

第三条工作流负责把固定虚拟 IP 首帧和 RVC 人声合成为唱歌视频。当前采用 ComfyUI 官方 `LTX-2.3 Image Audio to Video` 模板作为 MVP 起点。

输入分两类：

```text
lip-sync / motion 驱动：RVC 转换后的人声干声
最终成片声音：RVC 人声与伴奏混好的 final_mix
```

## 当前素材

```text
首帧图：
/root/autodl-tmp/vip_singing/assets/first_frames/luna_v1_first_frame.png

LTX-2.3 驱动音频：
/root/autodl-tmp/vip_singing/audio_workflow/output/rvc_vocals/045b_clip_27s_16s_misono_mika_rvc.wav

最终混音音频：
/root/autodl-tmp/vip_singing/audio_workflow/output/final_mix/045b_clip_27s_16s_misono_mika_final_mix.wav
```

ComfyUI `LoadImage/LoadAudio` 使用的是 `ComfyUI/input` 目录，已准备脚本：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/prepare_ltx23_video_inputs.sh
```

它会创建：

```text
/root/ComfyUI/input/VIP/video/luna_v1_first_frame.png
/root/ComfyUI/input/VIP/video/045b_clip_27s_16s_misono_mika_rvc.wav
/root/ComfyUI/input/VIP/video/045b_clip_27s_16s_misono_mika_final_mix.wav
```

## 已安装内容

```text
ComfyUI：已从 0.3.67 更新到 0.21.0 / commit 20e43941
ComfyUI-LTXVideo：已安装
ComfyUI-VideoHelperSuite：已安装
ComfyMath：已安装
KJNodes：原环境已有
```

ComfyUI 仍使用 AutoDL 原有入口：

```text
127.0.0.1:6006
AutoDL WebUI-6006
```

## 模型文件

LTX-2.3 模型已下载并通过检查。放置位置如下：

```text
/root/ComfyUI/models/checkpoints/ltx-2.3-22b-dev-fp8.safetensors                         28G
/root/ComfyUI/models/text_encoders/gemma_3_12B_it_fp4_mixed.safetensors                  8.8G
/root/ComfyUI/models/loras/ltx-2.3-22b-distilled-lora-384.safetensors                    7.1G
/root/ComfyUI/models/loras/gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors        600M
/root/ComfyUI/models/latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.1.safetensors   950M
```

如需重新下载或断点续传，可以执行：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/download_ltx23_models.sh
```

脚本支持断点续传。若下载到后段出现 `403 Forbidden`，通常是 Hugging Face/Xet 的临时签名链接过期，不要删除已经下载的 `.safetensors` 文件，重新执行同一条命令即可从原 Hugging Face 地址获取新签名并继续下载。首个大模型会校验完整大小：`29145431166` bytes。

如果下载太慢，就在本地下载后上传到上述目录。

## 工作流文件

已准备两个 UI 工作流：

```text
/root/ComfyUI/user/default/workflows/VIP/Video/LTX_2_3_IA2V_Luna_Smoke_5s.json
/root/ComfyUI/user/default/workflows/VIP/Video/LTX_2_3_IA2V_Luna_Full_16s.json
```

这两个工作流已经从官方模板的 Group Node 形式展平为普通节点。若运行时出现过 `Node ID '#340:287' has no class_type`，说明画布里仍是旧版本，需要刷新工作流列表并重新打开上述工作流。

建议先跑 `Smoke_5s`，确认嘴型、脸部稳定性和人物一致性，再跑 `Full_16s`。

## 使用步骤

1. 打开 AutoDL `WebUI-6006`。
2. 左侧工作流面板刷新，打开：

```text
VIP/Video/LTX_2_3_IA2V_Luna_Smoke_5s.json
```

3. 检查输入：

```text
image：VIP/video/luna_v1_first_frame.png
audio：VIP/video/045b_clip_27s_16s_misono_mika_rvc.wav
```

4. 先运行 5 秒 smoke。
5. 如果结果可用，再打开 16 秒版本。
6. 输出视频生成后，用最终混音替换视频音频：

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/mux_final_audio.sh \
  /root/ComfyUI/output/VIP/LTX23/你的_ltx_输出.mp4 \
  /root/autodl-tmp/vip_singing/video_workflow/output/luna_ltx23_final_mix.mp4
```

## 验证

```bash
bash /root/autodl-tmp/vip_singing/video_workflow/scripts/check_ltx23_video_setup.sh
```

在模型未下载前，验证脚本会显示模型 missing，这是预期状态。
