# 虚拟 IP 角色设定卡：Luna v1

## 基础定位

```text
角色名称：Luna
角色身份：虚拟歌手 / 个人音乐频道主角
年龄感：20 岁左右
气质关键词：清冷、温柔、克制、舞台感、略带距离感
音乐风格：抒情流行、电子流行、夜晚氛围感歌曲
整体画风：半写实二次元，精致干净，不要过度幼态
```

## 固定视觉特征

```text
发型：银白色长发，柔顺，有轻微层次感
刘海：空气感齐刘海，略微偏分
眼睛：浅蓝色眼睛，清澈，有高光
脸型：小巧鹅蛋脸，五官精致但自然
妆容：淡妆，轻微腮红，眼妆干净
服装：黑色短款舞台夹克，内搭深色上衣
配饰：银色耳返，小型银色耳饰
禁止变化：不要短发，不要红眼，不要夸张礼服，不要多人同框
```

## 视频友好约束

```text
构图：9:16 竖屏，中近景或胸像
角度：正脸或轻微侧脸，不超过 15 度
嘴部：清晰无遮挡，适合后续 lip-sync
手部：第一阶段不要靠近脸，不要挡嘴
背景：简洁舞台、棚拍、直播间，不能太乱
表情：自然唱歌表情，轻微微笑或专注感
```

## 角色候选图 Positive Prompt

用于第一轮 8 张小批量测试，粘贴到正向 `CLIP文本编码`：

```text
single virtual singer, original character design, Luna, elegant young female vocalist, silver white long hair, soft airy bangs, slightly side-parted bangs, pale blue eyes, clear sparkling eyes, delicate oval face, refined natural facial features, natural light makeup, subtle blush, clean eye makeup, black short stage jacket, dark inner top, silver in-ear monitors, small silver earrings, calm and gentle expression, slightly distant mood, semi-realistic anime style, medium close-up portrait, facing camera, clear visible mouth, natural singing expression, soft stage lighting, clean studio background, high quality, stable face, detailed eyes, polished character design, 9:16 vertical composition
```

## 角色候选图 Negative Prompt

用于负向 `CLIP文本编码`：

```text
multiple people, short hair, red eyes, exaggerated dress, childish face, overly young, hand covering face, hand near mouth, microphone covering mouth, distorted face, asymmetric eyes, deformed mouth, teeth artifacts, bad hands, extra fingers, missing fingers, heavy motion blur, crowded background, low quality, cropped face, extreme side view, watermark, text, logo
```

## 视频首帧 Positive Prompt

等选出角色方向后，用于生成 9:16 视频首帧：

```text
single virtual singer, Luna, silver white long hair, soft airy bangs, pale blue eyes, black short stage jacket, dark inner top, silver in-ear monitors, small silver earrings, semi-realistic anime style, medium close-up, 9:16 vertical composition, facing camera, clear visible mouth, natural singing expression, subtle smile, calm stage presence, soft stage lighting, clean simple stage background, face well lit, stable face, detailed eyes, high quality, suitable for lip sync video, no hand near face
```

## 视频首帧 Negative Prompt

```text
multiple people, hand covering face, hand near mouth, microphone covering mouth, extreme close-up, extreme side view, cropped head, cropped mouth, distorted face, deformed mouth, teeth artifacts, asymmetric eyes, bad hands, extra fingers, heavy motion blur, crowded background, low quality, watermark, text, logo
```

## 第一轮测试参数

```text
model：flux1-dev.safetensors
weight_dtype：fp8_e4m3fn
clip_name1：t5xxl_fp16.safetensors
clip_name2：clip_l.safetensors
vae：ae.safetensors
分辨率：768x1024
steps：24
KSampler cfg：1.0
FluxGuidance：3.5
sampler：euler
scheduler：simple
batch_size：1
seed：randomize
右上角运行数量：8
```

## 筛选标准

```text
[ ] 脸部辨识度高
[ ] 银白长发、浅蓝眼、黑色舞台夹克稳定
[ ] 嘴部清晰无遮挡
[ ] 没有明显眼睛、牙齿、手部错误
[ ] 角色气质符合清冷、温柔、舞台感
[ ] 后续适合做轻微唱歌表情和 lip-sync
```

## Nova Orange XL 构图调整 Prompt

用于 Nova Orange XL / Illustrious 工作流。目标是保留当前喜欢的画风、光影、人物和服装质感，但把镜头从脸部特写拉远到舞台高机位构图，接近“舞台自拍 / 高角度俯拍 / 半身到全身”的感觉。

### Positive Prompt：高机位舞台构图

粘贴到 Nova Orange XL 工作流的正向 `CLIP文本编码`：

```text
masterpiece, best quality, amazing quality, 4k, very aesthetic, high resolution, ultra-detailed, absurdres, newest, 1girl, solo, original character, virtual singer, silver white long hair, pale blue eyes, delicate oval face, natural light makeup, black short stage jacket, dark inner top, silver in-ear monitors, small silver earrings, detailed glossy hair, detailed clothing texture, dramatic soft stage lighting, concert stage, stage spotlights, depth of field, volumetric lighting, high-angle shot, overhead camera angle, wide-angle perspective, selfie-like stage photo, looking up at viewer, upper body and waist visible, three-quarter body composition, stage floor visible, one hand holding a microphone above the camera, relaxed singing pose, gentle performance pose, calm smile, natural expression, clear visible mouth, elegant idol stage presence
```

### Negative Prompt：避免脸部大特写

粘贴到负向 `CLIP文本编码`：

```text
extreme close-up, close-up face, face filling frame, only face, only head, cropped body, cropped shoulders, cropped mouth, cropped head, no body, portrait closeup, looking straight at camera in close-up, exaggerated action, overdramatic pose, open mouth too wide, screaming, crazy expression, multiple people, short hair, red eyes, childish face, overly young, hand covering face, hand near mouth, microphone covering mouth, distorted face, asymmetric eyes, deformed mouth, teeth artifacts, bad hands, extra fingers, missing fingers, heavy motion blur, crowded background, low quality, watermark, text, logo
```

### 参数建议

```text
model：novaOrangeXL_exV20.safetensors
分辨率：832x1216
steps：28
cfg：4.0
sampler：euler_ancestral
scheduler：normal
clip skip：2
batch_size：1
seed：randomize
右上角运行数量：8
```

### 如果还太近

在正向 prompt 里追加：

```text
full body visible, head-to-toe composition, more distance from camera, small face in frame, full outfit visible
```

在负向 prompt 里加强：

```text
close portrait, bust shot, face close-up, headshot
```

### 如果动作太夸张

把正向 prompt 里的：

```text
one hand holding a microphone above the camera
```

替换为：

```text
holding a microphone naturally, relaxed arm pose, subtle stage gesture
```
