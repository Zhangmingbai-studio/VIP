# 大模型上传到 AutoDL 的推荐方式

WebUI 上传 6GB 以上模型容易慢、断线、失败后重来。更推荐走 SSH/SFTP。

## 推荐方式：断点续传 SFTP 脚本

本项目已提供脚本：

```text
scripts/upload_large_model_to_autodl.py
```

用法：

```powershell
$env:AUTODL_SSH_PASSWORD="你的AutoDL密码"
python scripts\upload_large_model_to_autodl.py "D:\models\novaOrangeXL_exV20.safetensors"
```

默认上传到：

```text
/root/ComfyUI/models/checkpoints/novaOrangeXL_exV20.safetensors
```

脚本特性：

```text
[x] 通过 SSH/SFTP 传输
[x] 支持断点续传
[x] 先上传为 .part，完整后再改名
[x] 不修改 ComfyUI 端口和启动脚本
[x] 不会让 ComfyUI 误扫到半个模型文件
```

如果中途断开，重新运行同一条命令即可继续。

## 方式二：scp

Windows PowerShell 可运行：

```powershell
scp -P 41578 "D:\models\novaOrangeXL_exV20.safetensors" root@connect.bjb2.seetacloud.com:/root/ComfyUI/models/checkpoints/
```

缺点：普通 `scp` 不方便断点续传。大文件传输失败时可能需要重来。

## 方式三：对象存储或网盘中转

如果本地到 AutoDL 的 SSH 上传很慢，可以先上传到一个 AutoDL 能直接访问的对象存储或网盘，再在 AutoDL 里用 `wget/curl/aria2` 下载。

适合：

```text
阿里云 OSS
腾讯云 COS
七牛云
ModelScope
Hugging Face 私有仓库
```

当前这台 AutoDL 实例直连 Civitai 报网络不可达，所以暂时不推荐直接在服务器上 `wget` Civitai 地址。

