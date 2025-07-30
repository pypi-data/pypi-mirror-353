from typing import List, Optional, Literal, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import base64

def base64_to_bytes(base64_str: str) -> bytes:
    """
    将base64字符串转换为bytes

    Args:
        base64_str: base64编码的图片字符串

    Returns:
        bytes: 原始图片数据
    """
    if not base64_str:
        raise ValueError("Base64 string cannot be empty")

    try:
        return base64.b64decode(base64_str)
    except Exception as e:
        raise ValueError(f"Failed to convert base64 to bytes: {str(e)}")

def bytes_to_base64(image_bytes: bytes) -> str:
    """
    将bytes转换为base64字符串

    Args:
        image_bytes: 原始图片数据

    Returns:
        str: base64编码的图片字符串
    """
    if not image_bytes:
        raise ValueError("Image bytes cannot be empty")

    try:
        return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to convert bytes to base64: {str(e)}")

class InspectionDetail(BaseModel):
    itemId: str
    value: float
    isQualified: bool
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InspectionDetail":
        """从字典创建InspectionDetail实例"""
        return cls(**data)

class InspectionData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    batchNumber: str
    result: Literal["PASS", "FAIL", "WARNING", "ERROR"]
    imageData: Optional[str] = None
    details: List[InspectionDetail]

    @classmethod
    def create(
        cls,
        batch_number: str,
        result: str,
        details: Union[List[Dict[str, Any]], List[InspectionDetail]],
        image_data: Optional[Union[str, bytes]] = None
    ) -> "InspectionData":
        """
        创建InspectionData实例

        Args:
            batch_number: 批次号
            result: 检测结果
            details: 检测详情列表，可以是字典列表或InspectionDetail列表
            image_data: 图片数据，可以是base64字符串或bytes
        """
        # 处理图片数据
        processed_image_data = None
        if image_data is not None:
            if isinstance(image_data, bytes):
                processed_image_data = bytes_to_base64(image_data)
            else:
                processed_image_data = image_data

        # 处理details
        processed_details = []
        for detail in details:
            if isinstance(detail, InspectionDetail):
                processed_details.append(detail)
            else:
                processed_details.append(InspectionDetail.from_dict(detail))

        return cls(
            batchNumber=batch_number,
            result=result,
            imageData=processed_image_data,
            details=processed_details
        )

    def get_image(self) -> Optional[bytes]:
        """
        获取原始bytes格式的图片

        Returns:
            Optional[bytes]: 原始图片数据，如果没有图片数据则返回None
        """
        if not self.imageData:
            return None
        return base64_to_bytes(self.imageData)

    def model_dump(self) -> Dict[str, Any]:
        """
        将模型转换为可JSON序列化的字典

        Returns:
            Dict[str, Any]: 可JSON序列化的字典
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "batchNumber": self.batchNumber,
            "result": self.result,
            "imageData": self.imageData,
            "details": [detail.model_dump() for detail in self.details]
        }

class InspectionReport(BaseModel):
    secretKey: str
    data: InspectionData

    def model_dump(self) -> Dict[str, Any]:
        """
        将模型转换为可JSON序列化的字典

        Returns:
            Dict[str, Any]: 可JSON序列化的字典
        """
        return {
            "secretKey": self.secretKey,
            "data": self.data.model_dump()
        }

class InspectionRecord(BaseModel):
    id: str
    robotId: str
    batchNumber: str
    operatorId: str
    result: str
    imageData: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    isDeleted: bool

    def get_image(self) -> Optional[bytes]:
        """
        获取原始bytes格式的图片

        Returns:
            Optional[bytes]: 原始图片数据，如果没有图片数据则返回None
        """
        if not self.imageData:
            return None
        return base64_to_bytes(self.imageData)

    def model_dump(self) -> Dict[str, Any]:
        """
        将模型转换为可JSON序列化的字典

        Returns:
            Dict[str, Any]: 可JSON序列化的字典
        """
        return {
            "id": self.id,
            "robotId": self.robotId,
            "batchNumber": self.batchNumber,
            "operatorId": self.operatorId,
            "result": self.result,
            "imageData": self.imageData,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
            "isDeleted": self.isDeleted
        }

class InspectionResponse(BaseModel):
    code: int
    message: str
    data: List[InspectionRecord]
    timestamp: datetime

    def model_dump(self) -> Dict[str, Any]:
        """
        将模型转换为可JSON序列化的字典

        Returns:
            Dict[str, Any]: 可JSON序列化的字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": [record.model_dump() for record in self.data],
            "timestamp": self.timestamp.isoformat()
        }
