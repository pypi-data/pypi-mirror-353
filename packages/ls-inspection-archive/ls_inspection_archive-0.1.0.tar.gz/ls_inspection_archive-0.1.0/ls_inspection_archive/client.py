import os
from typing import List, Optional, Union, Dict, Any
import requests
from dotenv import load_dotenv
from .models import (
    InspectionData,
    InspectionDetail,
    InspectionReport,
    InspectionRecord
)


class InspectionArchiveClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        load_dotenv()
        self.base_url = base_url or os.getenv("LS_ARCHIVE_API_BASE")
        self.secret_key = secret_key or os.getenv("LS_ARCHIVE_API_KEY")

        if not base_url or not secret_key:
            raise ValueError("base_url and secret_key must be provided")

    def report_inspection(
        self,
        batch_number: str,
        result: str,
        details: Union[List[Dict[str, Any]], List[InspectionDetail]],
        image_data: Optional[Union[str, bytes]] = None
    ) -> InspectionRecord:
        """
        上报检测数据

        Args:
            batch_number: 批次号
            result: 检测结果 (PASS/FAIL/WARNING/ERROR)
            details: 检测详情列表，可以是字典列表或InspectionDetail列表
            image_data: 可选的图片数据，可以是base64字符串或bytes

        Returns:
            InspectionRecord: 创建的检测记录
        """
        data = InspectionData.create(
            batch_number=batch_number,
            result=result,
            details=details,
            image_data=image_data
        )

        report = InspectionReport(
            secretKey=self.secret_key,
            data=data
        )

        response = requests.post(
            f"{self.base_url}/robots/report",
            json=report.model_dump()
        )
        response.raise_for_status()

        result = response.json()
        if result["code"] != 0:
            raise Exception(f"API error: {result['message']}")

        return InspectionRecord(**result["data"])

    def get_inspection_records(self, limit: int = 10) -> List[InspectionRecord]:
        """
        获取检测记录列表

        Args:
            limit: 返回记录数量限制，默认10条

        Returns:
            List[InspectionRecord]: 检测记录列表
        """
        response = requests.get(
            f"{self.base_url}/inspection-record/list-by-robot-key",
            params={
                "secretKey": self.secret_key,
                "limit": limit
            }
        )
        response.raise_for_status()

        result = response.json()
        if result["code"] != 0:
            raise Exception(f"API error: {result['message']}")

        return [InspectionRecord(**record) for record in result["data"]]
