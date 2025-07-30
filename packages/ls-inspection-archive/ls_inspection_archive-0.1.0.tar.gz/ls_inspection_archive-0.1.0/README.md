# LS Inspection Archive SDK

这是一个用于与检测档案系统交互的Python SDK。

## 安装

```bash
pip install ls_inspection_archive
```

## 使用方法

### 基本使用

```python
from ls_inspection_archive import InspectionArchiveClient, InspectionDetail

# 从环境变量读取配置
client = InspectionArchiveClient()

# 或者直接指定配置
client = InspectionArchiveClient(
    base_url="http://localhost:7001",
    secret_key="your-secret-key"
)

# 方式1：使用字典方式上报检测数据
result = client.report_inspection(
    batch_number="BATCH-2025-001",
    result="PASS",
    details=[
        {
            "itemId": "937911d6-ea90-4a05-9445-548fe714e674",
            "value": 0,
            "isQualified": True,
            "description": "检测正常"
        }
    ],
    image_data=b"binary_image_data"  # 直接传入bytes，会自动转换为base64
)

# 方式2：使用类型化对象方式上报检测数据
detail = InspectionDetail(
    itemId="937911d6-ea90-4a05-9445-548fe714e674",
    value=0,
    isQualified=True,
    description="检测正常"
)

result = client.report_inspection(
    batch_number="BATCH-2025-001",
    result="PASS",
    details=[detail],
    image_data="base64_encoded_string"  # 传入base64字符串
)

# 获取检测记录
records = client.get_inspection_records(limit=10)
```

### 图片处理

SDK提供了多种图片格式转换功能：

```python
# 获取检测记录
records = client.get_inspection_records(limit=1)
record = records[0]

# 获取PIL格式的图片（用于显示或保存）
pil_image = record.get_image_as_pil()
if pil_image:
    # 显示图片
    pil_image.show()
    # 保存图片
    pil_image.save("inspection.jpg")

# 获取numpy数组格式的图片（用于图像处理）
numpy_image = record.get_image_as_numpy()
if numpy_image is not None:
    # 使用numpy进行图像处理
    import cv2
    # 转换为灰度图
    gray = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2GRAY)
    # 保存处理后的图片
    cv2.imwrite("processed.jpg", gray)

# 获取原始bytes格式的图片
image_bytes = record.get_image_as_bytes()
if image_bytes:
    # 直接写入文件
    with open("raw_image.jpg", "wb") as f:
        f.write(image_bytes)
```

### 环境变量配置

SDK支持通过环境变量配置：

- `LS_ARCHIVE_API_BASE`: API基础URL
- `LS_ARCHIVE_API_KEY`: 机器人密钥

### 特性

1. **类型安全**
   - 使用Pydantic进行数据验证
   - 完整的类型提示支持
   - 支持IDE自动补全

2. **灵活的数据输入**
   - 支持字典和类型化对象两种方式
   - 图片数据支持bytes和base64字符串
   - 自动进行数据转换和验证

3. **图片处理**
   - 支持PIL格式（适合显示和保存）
   - 支持numpy数组格式（适合图像处理）
   - 支持原始bytes格式（适合直接存储）
   - 自动的格式转换

4. **错误处理**
   - 完整的异常处理
   - 清晰的错误信息

5. **配置灵活**
   - 支持环境变量配置
   - 支持运行时配置
   - 支持.env文件配置

## 类型提示

SDK提供完整的类型提示支持，可以在IDE中获得更好的开发体验。主要类型包括：

- `InspectionDetail`: 检测详情
- `InspectionData`: 检测数据
- `InspectionRecord`: 检测记录
- `InspectionResponse`: API响应
