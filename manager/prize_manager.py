from db.sqlite_db import SQLiteDB
from typing import Optional, List, Dict, Any


class PrizeManager:
    """奖品管理类
    
    用于管理奖品数据，包含增删改查功能
    """
    
    def __init__(self, db_path: str):
        """初始化奖品管理类
        
        Args:
            db_path: 数据库文件路径
        """
        self.db = SQLiteDB(db_path)
        self._init_prize_table()
    
    def _init_prize_table(self) -> None:
        """初始化奖品表
        """
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "level": "TEXT NOT NULL",
            "quantity": "INTEGER DEFAULT 0"
        }
        self.db.create_table("prizes", columns)
    
    def add_prize(self, name: str, level: str, quantity: int = 0) -> int:
        """增加奖品数据
        
        Args:
            name: 奖品名称
            level: 奖品等级
            quantity: 奖品数量，默认值为0
            
        Returns:
            新奖品的ID
        """
        sql = "INSERT INTO prizes (name, level, quantity) VALUES (?, ?, ?)"
        cursor = self.db.execute(sql, (name, level, quantity))
        return cursor.lastrowid
    
    def delete_prize(self, prize_id: int) -> bool:
        """删除奖品数据
        
        Args:
            prize_id: 奖品ID
            
        Returns:
            是否删除成功
        """
        sql = "DELETE FROM prizes WHERE id = ?"
        cursor = self.db.execute(sql, (prize_id,))
        return cursor.rowcount > 0
    
    def update_prize(self, prize_id: int, name: Optional[str] = None, level: Optional[str] = None, quantity: Optional[int] = None) -> bool:
        """修改奖品数据
        
        Args:
            prize_id: 奖品ID
            name: 奖品名称（可选）
            level: 奖品等级（可选）
            quantity: 奖品数量（可选）
            
        Returns:
            是否修改成功
        """
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
        
        if level is not None:
            update_fields.append("level = ?")
            params.append(level)
        
        if quantity is not None:
            update_fields.append("quantity = ?")
            params.append(quantity)
        
        if not update_fields:
            return False
        
        params.append(prize_id)
        update_str = ", ".join(update_fields)
        sql = f"UPDATE prizes SET {update_str} WHERE id = ?"
        
        cursor = self.db.execute(sql, params)
        return cursor.rowcount > 0
    
    def get_prize_by_id(self, prize_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询奖品数据
        
        Args:
            prize_id: 奖品ID
            
        Returns:
            奖品数据字典
        """
        sql = "SELECT * FROM prizes WHERE id = ?"
        return self.db.fetch_one(sql, (prize_id,))
    
    def get_prize_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称查询奖品数据
        
        Args:
            name: 奖品名称
            
        Returns:
            奖品数据字典
        """
        sql = "SELECT * FROM prizes WHERE name = ?"
        return self.db.fetch_one(sql, (name,))
    
    def search_prizes_by_name(self, name: str) -> List[Dict[str, Any]]:
        """根据名称模糊查询奖品数据
        
        Args:
            name: 奖品名称关键字
            
        Returns:
            奖品数据列表
        """
        sql = "SELECT * FROM prizes WHERE name LIKE ?"
        return self.db.fetch_all(sql, (f"%{name}%",))
    
    def get_prizes_by_level(self, level: str) -> List[Dict[str, Any]]:
        """根据等级查询奖品数据
        
        Args:
            level: 奖品等级
            
        Returns:
            奖品数据列表
        """
        sql = "SELECT * FROM prizes WHERE level = ?"
        return self.db.fetch_all(sql, (level,))
    
    def get_all_prizes(self) -> List[Dict[str, Any]]:
        """
        查询所有奖品数据
        Returns:
            奖品数据列表
        """
        sql = "SELECT * FROM prizes"
        return self.db.fetch_all(sql)
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.db.close()