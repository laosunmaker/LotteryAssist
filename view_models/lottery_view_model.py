import random
import csv
import os
from manager.user_manager import UserManager
from manager.prize_manager import PrizeManager
from manager.winner_manager import WinnerManager
from typing import List, Dict, Any


class LotteryViewModel:
    """抽奖视图模型
    
    负责处理抽奖相关的业务逻辑，并与抽奖界面进行数据绑定
    """
    
    def __init__(self, db_path: str):
        """初始化抽奖视图模型
        
        Args:
            db_path: 数据库文件路径
        """
        self.user_manager = UserManager(db_path)
        self.prize_manager = PrizeManager(db_path)
        self.winner_manager = WinnerManager(db_path)
        self.lottery_results = []
        self.total_rounds = 10  # 默认总轮次
        self.current_round = 0  # 当前轮次
        self.must_win_users_won = set()  # 记录已中奖的必中奖用户
        self.allow_duplicate_winners = True  # 是否允许重复抽中相同人员，默认允许
        self.winners_history = set()  # 记录已中奖的所有用户ID
        self._load_data()
    
    def _load_data(self):
        """加载数据到字典
        """
        # 加载用户数据
        self.users = self.user_manager.get_all_users()
        
        # 加载奖品数据
        self.prizes = self.prize_manager.get_all_prizes()
        
        # 加载中奖概率数据
        self.winners = {}
        for winner in self.winner_manager.get_all_winners():
            self.winners[winner['user_id']] = winner['winning_probability']
        
        # 初始化奖品数量本地缓存
        self.prize_quantities = {}
        for prize in self.prizes:
            self.prize_quantities[prize['id']] = prize['quantity']
    
    def reload_data(self):
        """重新加载数据
        """
        self._load_data()
    
    def set_total_rounds(self, rounds: int):
        """设置抽奖总轮次
        
        Args:
            rounds: 总轮次数
        """
        if rounds > 0:
            self.total_rounds = rounds
    
    def get_total_rounds(self) -> int:
        """获取抽奖总轮次
        
        Returns:
            总轮次数
        """
        return self.total_rounds
    
    def get_current_round(self) -> int:
        """获取当前轮次
        
        Returns:
            当前轮次数
        """
        return self.current_round
    
    def set_allow_duplicate_winners(self, allow: bool):
        """设置是否允许重复抽中相同人员
        
        Args:
            allow: 是否允许重复抽中相同人员
        """
        self.allow_duplicate_winners = allow
    
    def get_allow_duplicate_winners(self) -> bool:
        """获取是否允许重复抽中相同人员
        
        Returns:
            是否允许重复抽中相同人员
        """
        return self.allow_duplicate_winners
    
    def get_available_users(self) -> List[Dict[str, Any]]:
        """获取可参与抽奖的用户
        
        Returns:
            可参与抽奖的用户列表
        """
        available_users = []
        for user in self.users:
            # 必不中奖用户不参与
            if self.winners.get(user['id'], 0) != 2:
                # 检查是否允许重复中奖，如果不允许，则排除已经中奖的用户
                if self.allow_duplicate_winners or user['id'] not in self.winners_history:
                    available_users.append(user)
        return available_users
    
    def get_must_win_users(self) -> List[Dict[str, Any]]:
        """获取必中奖用户
        
        Returns:
            必中奖用户列表，每个用户包含user_id和prize_id（如果有）
        """
        must_win_users = []
        for user in self.users:
            if self.winners.get(user['id'], 0) == 1:
                # 检查是否允许重复中奖，如果不允许，则排除已经中奖的用户
                if self.allow_duplicate_winners or user['id'] not in self.winners_history:
                    # 获取用户的必中奖品信息
                    winner_info = self.winner_manager.get_winner_by_user_id(user['id'])
                    user_with_prize = user.copy()
                    if winner_info:
                        user_with_prize['prize_id'] = winner_info.get('prize_id')
                    must_win_users.append(user_with_prize)
        return must_win_users
    
    def get_available_prizes(self) -> List[Dict[str, Any]]:
        """获取可用奖品
        
        Returns:
            可用奖品列表
        """
        available_prizes = []
        for prize in self.prizes:
            # 检查本地缓存中的奖品数量是否大于0
            if self.prize_quantities.get(prize['id'], 0) > 0:
                available_prizes.append(prize)
        return available_prizes
    
    def draw_lottery(self) -> Dict[str, Any]:
        """执行一次抽奖
        
        Returns:
            抽奖结果
        """
        # 检查当前轮次是否已达到总轮次
        if self.current_round >= self.total_rounds:
            return None
        
        # 增加当前轮次计数
        self.current_round += 1
        
        # 获取可参与抽奖的用户
        available_users = self.get_available_users()
        
        # 获取必中奖用户
        must_win_users = self.get_must_win_users()
        
        # 获取可用奖品
        available_prizes = self.get_available_prizes()
        
        if not available_users or not available_prizes:
            return None
        
        # 计算剩余轮次
        remaining_rounds = self.total_rounds - self.current_round + 1
        
        # 计算还未中奖的必中奖用户
        not_won_must_win_users = [user for user in must_win_users if user['id'] not in self.must_win_users_won]
        
        # 优先从必中奖用户中选择的条件
        # 1. 还有未中奖的必中奖用户
        # 2. 剩余轮次大于等于未中奖的必中奖用户数量，确保每个必中奖用户都有机会中奖
        should_choose_must_win = len(not_won_must_win_users) > 0 and remaining_rounds >= len(not_won_must_win_users)
        
        # 选择用户
        selected_user = None
        selected_prize = None
        
        if should_choose_must_win:
            # 从还未中奖的必中奖用户中选择
            selected_user = random.choice(not_won_must_win_users)
            # 标记该用户已中奖
            self.must_win_users_won.add(selected_user['id'])
            
            # 检查是否有指定必中奖品
            if 'prize_id' in selected_user and selected_user['prize_id']:
                # 查找指定的奖品
                for prize in available_prizes:
                    if prize['id'] == selected_user['prize_id']:
                        selected_prize = prize
                        break
            
            # 如果没有找到指定的奖品或没有指定奖品，则随机选择一个奖品
            if not selected_prize:
                selected_prize = random.choice(available_prizes)
        else:
            # 从所有可用用户中随机选择
            if available_users:
                selected_user = random.choice(available_users)
                # 随机选择一个奖品
                selected_prize = random.choice(available_prizes)
        
        # 检查是否成功选择了用户和奖品
        if not selected_user or not selected_prize:
            return None
        
        # 记录抽奖结果
        result = {
            'user_id': selected_user['id'],
            'username': selected_user['username'],
            'employee_id': selected_user['employee_id'],
            'prize_id': selected_prize['id'],
            'prize_name': selected_prize['name'],
            'prize_level': selected_prize['level']
        }
        
        self.lottery_results.append(result)
        
        # 减少本地缓存中的奖品数量
        if selected_prize['id'] in self.prize_quantities:
            self.prize_quantities[selected_prize['id']] -= 1
        
        # 记录中奖用户到历史记录
        self.winners_history.add(selected_user['id'])
        
        return result
    
    def get_lottery_results(self) -> List[Dict[str, Any]]:
        """获取抽奖结果
        
        Returns:
            抽奖结果列表
        """
        return self.lottery_results
    
    def export_results(self, export_path: str) -> bool:
        """导出抽奖结果
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['用户名', '工号', '奖品名称', '奖品等级'])
                # 写入数据
                for result in self.lottery_results:
                    writer.writerow([
                        result['username'],
                        result['employee_id'],
                        result['prize_name'],
                        result['prize_level']
                    ])
            return True
        except Exception:
            return False
    
    def clear_results(self):
        """清空抽奖结果
        """
        self.lottery_results = []
        self.current_round = 0  # 重置当前轮次
        self.must_win_users_won.clear()  # 重置已中奖的必中奖用户集合
        self.winners_history.clear()  # 重置已中奖的所有用户记录
        
        # 重新从数据库中加载数据，确保奖品数量是最新的
        self._load_data()
    
    def close(self) -> None:
        """关闭数据库连接
        """
        self.user_manager.close()
        self.prize_manager.close()
        self.winner_manager.close()
