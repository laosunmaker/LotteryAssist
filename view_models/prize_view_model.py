from manager.prize_manager import PrizeManager
from main_logic.batch_importer import BatchImporter
from typing import List, Dict, Any


class PrizeViewModel:
    """奖品视图模型
    
    负责处理奖品相关的业务逻辑，并与奖品界面进行数据绑定
    """
    
    def __init__(self, db_path: str):
        """初始化奖品视图模型
        
        Args:
            db_path: 数据库文件路径
        """
        self.prize_manager = PrizeManager(db_path)
        self.batch_importer = BatchImporter(db_path)
    
    def add_prize(self, name: str, level: str, quantity: int = 0) -> bool:
        """添加奖品
        
        Args:
            name: 奖品名称
            level: 奖品等级
            quantity: 奖品数量
            
        Returns:
            是否添加成功
        """
        try:
            self.prize_manager.add_prize(name, level, quantity)
            return True
        except Exception:
            return False
    
    def delete_prize(self, prize_id: int) -> bool:
        """删除奖品
        
        Args:
            prize_id: 奖品ID
            
        Returns:
            是否删除成功
        """
        try:
            return self.prize_manager.delete_prize(prize_id)
        except Exception:
            return False
    
    def update_prize(self, prize_id: int, name: str = None, level: str = None, quantity: int = None) -> bool:
        """更新奖品
        
        Args:
            prize_id: 奖品ID
            name: 奖品名称
            level: 奖品等级
            quantity: 奖品数量
            
        Returns:
            是否更新成功
        """
        try:
            return self.prize_manager.update_prize(prize_id, name, level, quantity)
        except Exception:
            return False
    
    def get_prize_by_id(self, prize_id: int) -> Dict[str, Any]:
        """根据ID获取奖品
        
        Args:
            prize_id: 奖品ID
            
        Returns:
            奖品信息
        """
        return self.prize_manager.get_prize_by_id(prize_id)
    
    def get_prize_by_name(self, name: str) -> Dict[str, Any]:
        """根据名称获取奖品
        
        Args:
            name: 奖品名称
            
        Returns:
            奖品信息
        """
        return self.prize_manager.get_prize_by_name(name)
    
    def search_prizes_by_name(self, name: str) -> List[Dict[str, Any]]:
        """根据名称模糊查询奖品
        
        Args:
            name: 奖品名称关键字
            
        Returns:
            奖品列表
        """
        return self.prize_manager.search_prizes_by_name(name)
    
    def get_prizes_by_level(self, level: str) -> List[Dict[str, Any]]:
        """根据等级获取奖品
        
        Args:
            level: 奖品等级
            
        Returns:
            奖品列表
        """
        return self.prize_manager.get_prizes_by_level(level)
    
    def get_all_prizes(self) -> List[Dict[str, Any]]:
        """获取所有奖品
        
        Returns:
            奖品列表
        """
        return self.prize_manager.get_all_prizes()
    
    def generate_prize_template(self) -> str:
        """生成奖品批量导入模板
        
        Returns:
            模板文件路径
        """
        return self.batch_importer.generate_prize_template()
    
    def import_prizes_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """从CSV文件批量导入奖品
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            导入结果
        """
        return self.batch_importer.import_prizes_from_csv(csv_path)
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.prize_manager.close()
        self.batch_importer.close()
