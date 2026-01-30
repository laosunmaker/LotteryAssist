import sqlite3
from typing import Optional, List, Dict, Any


class SQLiteDB:
    """SQLite3数据库封装类
    
    用于连接SQLite3数据库，不存在则创建
    提供基本的数据库操作方法
    """
    
    def __init__(self, db_path: str):
        """初始化SQLite3数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """连接数据库
        
        如果数据库不存在，则创建
        """
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def close(self) -> None:
        """关闭数据库连接
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> sqlite3.Cursor:
        """执行SQL语句
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            游标对象
        """
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        self.connection.commit()
        return cursor
    
    def fetch_all(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """获取所有查询结果
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            查询结果列表
        """
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetch_one(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """获取单个查询结果
        
        Args:
            sql: SQL语句
            params: SQL参数
            
        Returns:
            查询结果字典
        """
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """创建表
        
        Args:
            table_name: 表名
            columns: 列定义，格式为{列名: 列类型}
        """
        columns_str = ", ".join([f"{col} {col_type}" for col, col_type in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.execute(sql)