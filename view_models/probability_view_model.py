from manager.winner_manager import WinnerManager
from manager.user_manager import UserManager
from typing import List, Dict, Any


class ProbabilityViewModel:
    """中奖概率视图模型
    
    负责处理中奖概率相关的业务逻辑，并与中奖概率界面进行数据绑定
    """
    
    def __init__(self, db_path: str):
        """初始化中奖概率视图模型
        
        Args:
            db_path: 数据库文件路径
        """
        self.winner_manager = WinnerManager(db_path)
        self.user_manager = UserManager(db_path)
    
    def add_or_update_winner(self, user_id: int, winning_probability: int, prize_id: int = None) -> bool:
        """添加或更新中奖概率
        
        Args:
            user_id: 用户ID
            winning_probability: 中奖概率（0为默认，1为必中，2为必不中）
            prize_id: 必中奖品ID
            
        Returns:
            是否操作成功
        """
        try:
            # 先检查是否已存在
            existing_winner = self.winner_manager.get_winner_by_user_id(user_id)
            if existing_winner:
                # 更新
                return self.winner_manager.update_winner_by_user_id(user_id, winning_probability, prize_id)
            else:
                # 添加
                self.winner_manager.add_winner(user_id, winning_probability, prize_id)
                return True
        except Exception:
            return False
    
    def delete_winner(self, winner_id: int) -> bool:
        """删除中奖信息
        
        Args:
            winner_id: 中奖信息ID
            
        Returns:
            是否删除成功
        """
        try:
            return self.winner_manager.delete_winner(winner_id)
        except Exception:
            return False
    
    def get_winner_by_user_id(self, user_id: int) -> Dict[str, Any]:
        """根据用户ID获取中奖信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            中奖信息
        """
        return self.winner_manager.get_winner_by_user_id(user_id)
    
    def get_all_winners(self) -> List[Dict[str, Any]]:
        """获取所有中奖信息
        
        Returns:
            中奖信息列表
        """
        return self.winner_manager.get_all_winners()
    
    def get_must_win_users(self) -> List[Dict[str, Any]]:
        """获取必中奖用户
        
        Returns:
            必中奖用户列表
        """
        winners = self.winner_manager.get_winners_by_probability(1)
        users = []
        for winner in winners:
            user = self.user_manager.get_user_by_id(winner['user_id'])
            if user:
                user['winning_probability'] = winner['winning_probability']
                users.append(user)
        return users
    
    def get_cannot_win_users(self) -> List[Dict[str, Any]]:
        """获取必不中奖用户
        
        Returns:
            必不中奖用户列表
        """
        winners = self.winner_manager.get_winners_by_probability(2)
        users = []
        for winner in winners:
            user = self.user_manager.get_user_by_id(winner['user_id'])
            if user:
                user['winning_probability'] = winner['winning_probability']
                users.append(user)
        return users
    
    def get_all_users_with_probability(self) -> List[Dict[str, Any]]:
        """获取所有用户及其中奖概率
        
        Returns:
            用户及其中奖概率列表
        """
        users = self.user_manager.get_all_users()
        for user in users:
            winner = self.winner_manager.get_winner_by_user_id(user['id'])
            if winner:
                user['winning_probability'] = winner['winning_probability']
            else:
                user['winning_probability'] = 0  # 默认值
        return users
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.winner_manager.close()
        self.user_manager.close()
