from db.sqlite_db import SQLiteDB
from manager.winner_manager import WinnerManager
from typing import Optional, List, Dict, Any


class UserManager:
    """用户信息管理类
    
    用于管理用户数据，包含增删改查功能
    """
    
    def __init__(self, db_path: str):
        """初始化用户管理类
        
        Args:
            db_path: 数据库文件路径
        """
        self.db = SQLiteDB(db_path)
        self.winner_manager = WinnerManager(db_path)
        self._init_user_table()
    
    def _init_user_table(self) -> None:
        """初始化用户表
        """
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "username": "TEXT NOT NULL",
            "employee_id": "TEXT"
        }
        self.db.create_table("users", columns)
    
    def add_user(self, username: str, employee_id: str) -> int:
        """增加用户数据
        
        Args:
            username: 用户名
            employee_id: 工号
            
        Returns:
            新用户的ID
        """
        sql = "INSERT INTO users (username, employee_id) VALUES (?, ?)"
        cursor = self.db.execute(sql, (username, employee_id))
        return cursor.lastrowid
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        # 先删除对应的中奖信息
        self.winner_manager.delete_winner_by_user_id(user_id)
        
        # 再删除用户
        sql = "DELETE FROM users WHERE id = ?"
        cursor = self.db.execute(sql, (user_id,))
        return cursor.rowcount > 0
    
    def update_user(self, user_id: int, username: Optional[str] = None, employee_id: Optional[str] = None) -> bool:
        """修改用户数据
        
        Args:
            user_id: 用户ID
            username: 用户名（可选）
            employee_id: 工号（可选）
            
        Returns:
            是否修改成功
        """
        update_fields = []
        params = []
        
        if username is not None:
            update_fields.append("username = ?")
            params.append(username)
        
        if employee_id is not None:
            update_fields.append("employee_id = ?")
            params.append(employee_id)
        
        if not update_fields:
            return False
        
        params.append(user_id)
        update_str = ", ".join(update_fields)
        sql = f"UPDATE users SET {update_str} WHERE id = ?"
        
        cursor = self.db.execute(sql, params)
        return cursor.rowcount > 0
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查询用户数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户数据字典
        """
        sql = "SELECT * FROM users WHERE id = ?"
        return self.db.fetch_one(sql, (user_id,))
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """查询所有用户数据
        
        Returns:
            用户数据列表
        """
        sql = "SELECT * FROM users"
        return self.db.fetch_all(sql)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名查询用户数据
        
        Args:
            username: 用户名
            
        Returns:
            用户数据字典
        """
        sql = "SELECT * FROM users WHERE username = ?"
        return self.db.fetch_one(sql, (username,))
    
    def search_users_by_username(self, username: str) -> List[Dict[str, Any]]:
        """根据用户名模糊查询用户数据
        
        Args:
            username: 用户名关键字
            
        Returns:
            用户数据列表
        """
        sql = "SELECT * FROM users WHERE username LIKE ?"
        return self.db.fetch_all(sql, (f"%{username}%",))
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.winner_manager.close()
        self.db.close()