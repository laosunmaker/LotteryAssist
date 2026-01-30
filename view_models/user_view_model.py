from manager.user_manager import UserManager
from main_logic.batch_importer import BatchImporter
from typing import List, Dict, Any


class UserViewModel:
    """用户视图模型
    
    负责处理用户相关的业务逻辑，并与用户界面进行数据绑定
    """
    
    def __init__(self, db_path: str):
        """初始化用户视图模型
        
        Args:
            db_path: 数据库文件路径
        """
        self.user_manager = UserManager(db_path)
        self.batch_importer = BatchImporter(db_path)
    
    def add_user(self, username: str, employee_id: str) -> bool:
        """添加用户
        
        Args:
            username: 用户名
            employee_id: 工号
            
        Returns:
            是否添加成功
        """
        try:
            self.user_manager.add_user(username, employee_id)
            return True
        except Exception:
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        try:
            return self.user_manager.delete_user(user_id)
        except Exception:
            return False
    
    def update_user(self, user_id: int, username: str = None, employee_id: str = None) -> bool:
        """更新用户
        
        Args:
            user_id: 用户ID
            username: 用户名
            employee_id: 工号
            
        Returns:
            是否更新成功
        """
        try:
            return self.user_manager.update_user(user_id, username, employee_id)
        except Exception:
            return False
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息
        """
        return self.user_manager.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户信息
        """
        return self.user_manager.get_user_by_username(username)
    
    def search_users_by_username(self, username: str) -> List[Dict[str, Any]]:
        """根据用户名模糊查询用户
        
        Args:
            username: 用户名关键字
            
        Returns:
            用户列表
        """
        return self.user_manager.search_users_by_username(username)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户
        
        Returns:
            用户列表
        """
        return self.user_manager.get_all_users()
    
    def generate_user_template(self) -> str:
        """生成用户批量导入模板
        
        Returns:
            模板文件路径
        """
        return self.batch_importer.generate_user_template()
    
    def import_users_from_csv(self, csv_path: str) -> Dict[str, Any]:
        """从CSV文件批量导入用户
        
        Args:
            csv_path: CSV文件路径
            
        Returns:
            导入结果
        """
        return self.batch_importer.import_users_from_csv(csv_path)
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.user_manager.close()
        self.batch_importer.close()
