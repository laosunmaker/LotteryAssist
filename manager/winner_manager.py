from db.sqlite_db import SQLiteDB
from typing import Optional, List, Dict, Any


class WinnerManager:
    """中奖管理类
    
    用于管理中奖信息，包含增删改查操作
    """
    
    def __init__(self, db_path: str):
        """初始化中奖管理类
        
        Args:
            db_path: 数据库文件路径
        """
        self.db = SQLiteDB(db_path)
        self._init_winner_table()
    
    def _init_winner_table(self) -> None:
        """初始化中奖表
        """
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "user_id": "INTEGER UNIQUE NOT NULL",
            "winning_probability": "INTEGER DEFAULT 0",
            "prize_id": "INTEGER"
        }
        self.db.create_table("winners", columns)
    
    def add_winner(self, user_id: int, winning_probability: int = 0, prize_id: int = None) -> int:
        """增加中奖信息
        
        Args:
            user_id: 用户ID
            winning_probability: 中奖可能性（0为默认，1为必中，2为必不中）
            prize_id: 必中奖品ID
            
        Returns:
            新中奖信息的ID
        """
        sql = "INSERT INTO winners (user_id, winning_probability, prize_id) VALUES (?, ?, ?)"
        cursor = self.db.execute(sql, (user_id, winning_probability, prize_id))
        return cursor.lastrowid
    
    def delete_winner(self, winner_id: int) -> bool:
        """删除中奖信息
        
        Args:
            winner_id: 中奖信息ID
            
        Returns:
            是否删除成功
        """
        sql = "DELETE FROM winners WHERE id = ?"
        cursor = self.db.execute(sql, (winner_id,))
        return cursor.rowcount > 0
    
    def delete_winner_by_user_id(self, user_id: int) -> bool:
        """根据用户ID删除中奖信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        sql = "DELETE FROM winners WHERE user_id = ?"
        cursor = self.db.execute(sql, (user_id,))
        return cursor.rowcount > 0
    
    def update_winner(self, winner_id: int, winning_probability: Optional[int] = None, prize_id: Optional[int] = None) -> bool:
        """修改中奖信息
        
        Args:
            winner_id: 中奖信息ID
            winning_probability: 中奖可能性（可选）
            prize_id: 必中奖品ID（可选）
            
        Returns:
            是否修改成功
        """
        update_fields = []
        params = []
        
        if winning_probability is not None:
            update_fields.append("winning_probability = ?")
            params.append(winning_probability)
        
        if prize_id is not None:
            update_fields.append("prize_id = ?")
            params.append(prize_id)
        
        if not update_fields:
            return False
        
        params.append(winner_id)
        update_str = ", ".join(update_fields)
        sql = f"UPDATE winners SET {update_str} WHERE id = ?"
        
        cursor = self.db.execute(sql, params)
        return cursor.rowcount > 0
    
    def update_winner_by_user_id(self, user_id: int, winning_probability: int, prize_id: int = None) -> bool:
        """根据用户ID修改中奖信息
        
        Args:
            user_id: 用户ID
            winning_probability: 中奖可能性
            prize_id: 必中奖品ID
            
        Returns:
            是否修改成功
        """
        sql = "UPDATE winners SET winning_probability = ?, prize_id = ? WHERE user_id = ?"
        cursor = self.db.execute(sql, (winning_probability, prize_id, user_id))
        return cursor.rowcount > 0
    
    def get_winner_by_id(self, winner_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询中奖信息
        
        Args:
            winner_id: 中奖信息ID
            
        Returns:
            中奖信息字典
        """
        sql = "SELECT * FROM winners WHERE id = ?"
        return self.db.fetch_one(sql, (winner_id,))
    
    def get_winner_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据用户ID查询中奖信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            中奖信息字典
        """
        sql = "SELECT * FROM winners WHERE user_id = ?"
        return self.db.fetch_one(sql, (user_id,))
    
    def get_winners_by_probability(self, winning_probability: int) -> List[Dict[str, Any]]:
        """根据中奖可能性查询中奖信息
        
        Args:
            winning_probability: 中奖可能性
            
        Returns:
            中奖信息列表
        """
        sql = "SELECT * FROM winners WHERE winning_probability = ?"
        return self.db.fetch_all(sql, (winning_probability,))
    
    def get_all_winners(self) -> List[Dict[str, Any]]:
        """查询所有中奖信息
        
        Returns:
            中奖信息列表
        """
        sql = "SELECT * FROM winners"
        return self.db.fetch_all(sql)
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.db.close()