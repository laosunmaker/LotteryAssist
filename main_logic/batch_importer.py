import os
import csv
from typing import List, Dict, Any
from db.sqlite_db import SQLiteDB
from manager.user_manager import UserManager
from manager.prize_manager import PrizeManager
from charset_normalizer import from_bytes


class BatchImporter:
    """批量导入导出类
    
    用于生成批量导入模板和批量导入数据
    """
    
    def __init__(self, db_path: str):
        """初始化批量导入导出类
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.user_manager = UserManager(db_path)
        self.prize_manager = PrizeManager(db_path)
        self.template_dir = "template"
        self._ensure_template_dir()
    
    def _ensure_template_dir(self) -> None:
        """确保模板目录存在
        """
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的编码
        """
        with open(file_path, 'rb') as f:
            content = f.read()
            result = from_bytes(content).best()
            if result:
                return result.encoding
        
        return 'utf-8'
    
    def generate_user_template(self) -> str:
        """生成用户批量导入模板
        
        Returns:
            模板文件路径
        """
        template_path = os.path.join(self.template_dir, "user_template.csv")
        
        # 模板列名
        headers = ["username", "employee_id"]
        
        # 示例数据
        sample_data = [
            ["张三", "EMP001"],
            ["李四", "EMP002"]
        ]
        
        # 写入模板文件
        with open(template_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(sample_data)
        
        return template_path
    
    def generate_prize_template(self) -> str:
        """生成奖品批量导入模板
        
        Returns:
            模板文件路径
        """
        template_path = os.path.join(self.template_dir, "prize_template.csv")
        
        # 模板列名
        headers = ["name", "level", "quantity"]
        
        # 示例数据
        sample_data = [
            ["iPhone 15", "一等奖", "5"],
            ["AirPods Pro", "二等奖", "10"]
        ]
        
        # 写入模板文件
        with open(template_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(sample_data)
        
        return template_path
    
    def import_users_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """从CSV文件批量导入用户
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            导入结果，包含成功和失败的数量
        """
        success_count = 0
        failed_count = 0
        failed_records = []
        
        try:
            # 检测文件编码
            encoding = self._detect_encoding(csv_path)
            #print(f"检测到文件编码: {encoding}")
            with open(csv_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        username = row.get("username", "").strip()
                        employee_id = row.get("employee_id", "").strip()
                        
                        if not username:
                            failed_records.append({"row": row, "error": "用户名不能为空"})
                            failed_count += 1
                            continue
                        
                        self.user_manager.add_user(username, employee_id)
                        success_count += 1
                        
                    except Exception as e:
                        failed_records.append({"row": row, "error": str(e)})
                        failed_count += 1
                        continue
        
        except Exception as e:
            return {"success": 0, "failed": 0, "error": str(e)}
        
        return {
            "success": success_count,
            "failed": failed_count,
            "failed_records": failed_records
        }
    
    def import_prizes_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """从CSV文件批量导入奖品
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            导入结果，包含成功和失败的数量
        """
        success_count = 0
        failed_count = 0
        failed_records = []
        
        try:
            # 检测文件编码
            encoding = self._detect_encoding(csv_path)
            with open(csv_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        name = row.get("name", "").strip()
                        level = row.get("level", "").strip()
                        quantity_str = row.get("quantity", "0").strip()
                        
                        if not name:
                            failed_records.append({"row": row, "error": "奖品名称不能为空"})
                            failed_count += 1
                            continue
                        
                        if not level:
                            failed_records.append({"row": row, "error": "奖品等级不能为空"})
                            failed_count += 1
                            continue
                        
                        try:
                            quantity = int(quantity_str)
                        except ValueError:
                            quantity = 0
                        
                        self.prize_manager.add_prize(name, level, quantity)
                        success_count += 1
                        
                    except Exception as e:
                        failed_records.append({"row": row, "error": str(e)})
                        failed_count += 1
                        continue
        
        except Exception as e:
            return {"success": 0, "failed": 0, "error": str(e)}
        
        return {
            "success": success_count,
            "failed": failed_count,
            "failed_records": failed_records
        }
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.user_manager.close()
        self.prize_manager.close()