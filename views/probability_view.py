from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt


class ProbabilityView(QWidget):
    """中奖概率管理视图
    """
    
    def __init__(self, probability_view_model):
        """初始化中奖概率管理视图
        
        Args:
            probability_view_model: 中奖概率视图模型
        """
        super().__init__()
        self.probability_view_model = probability_view_model
        self.init_ui()
        self.prizes = []  # 存储奖品列表
        self.refresh_user_list()
    
    def init_ui(self):
        """初始化中奖概率管理界面
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建搜索和刷新区域
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_layout.addWidget(QLabel("用户名查询:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("查询")
        self.search_button.clicked.connect(self.search_user)
        search_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_user_list)
        search_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(search_layout)
        
        # 创建用户列表
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(["用户名", "工号", "中奖概率", "必中奖品", "操作"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.user_table)
    
    def refresh_user_list(self):
        """刷新用户列表
        """
        # 加载用户列表
        users = self.probability_view_model.get_all_users_with_probability()
        
        # 加载奖品列表
        from manager.prize_manager import PrizeManager
        prize_manager = PrizeManager('lottery.db')
        self.prizes = prize_manager.get_all_prizes()
        prize_manager.close()
        
        # 清空表格
        self.user_table.setRowCount(0)
        
        # 添加用户数据
        for user in users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(user['username']))
            self.user_table.setItem(row, 1, QTableWidgetItem(user['employee_id']))
            
            # 添加中奖概率下拉框
            probability_combo = QComboBox()
            probability_combo.addItem("默认", 0)
            probability_combo.addItem("必中", 1)
            probability_combo.addItem("必不中", 2)
            
            # 设置当前值
            current_probability = user.get('winning_probability', 0)
            probability_combo.setCurrentIndex(current_probability)
            
            # 连接信号
            probability_combo.currentIndexChanged.connect(
                lambda index, uid=user['id'], combo=probability_combo, row=row: self.update_probability(uid, combo.currentData(), row)
            )
            
            self.user_table.setCellWidget(row, 2, probability_combo)
            
            # 添加奖品选择下拉框
            prize_combo = QComboBox()
            prize_combo.addItem("无", None)
            for prize in self.prizes:
                prize_combo.addItem(f"{prize['name']} ({prize['level']})", prize['id'])
            
            # 获取当前奖品ID
            current_prize_id = None
            winner_info = self.probability_view_model.get_winner_by_user_id(user['id'])
            if winner_info:
                current_prize_id = winner_info.get('prize_id')
            
            # 设置当前值
            for i in range(prize_combo.count()):
                if prize_combo.itemData(i) == current_prize_id:
                    prize_combo.setCurrentIndex(i)
                    break
            
            # 连接信号
            prize_combo.currentIndexChanged.connect(
                lambda index, uid=user['id'], combo=prize_combo, row=row: self.update_prize(uid, combo.currentData(), row)
            )
            
            self.user_table.setCellWidget(row, 3, prize_combo)
            
            # 添加操作按钮
            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)
            
            reset_button = QPushButton("重置")
            reset_button.setFixedHeight(30)
            reset_button.clicked.connect(lambda checked, uid=user['id']: self.reset_probability(uid))
            button_layout.addWidget(reset_button)
            
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.user_table.setCellWidget(row, 4, button_widget)
            
            # 设置行高
            self.user_table.setRowHeight(row, 70)
    
    def update_probability(self, user_id, winning_probability, row):
        """更新中奖概率
        
        Args:
            user_id: 用户ID
            winning_probability: 中奖概率（0为默认，1为必中，2为必不中）
            row: 表格行索引
        """
        # 如果用户被设置为必不中，则自动将奖品ID设置为None
        prize_id = None
        if winning_probability != 2:
            # 获取当前选择的奖品ID
            prize_combo = self.user_table.cellWidget(row, 3)
            prize_id = prize_combo.currentData()
        else:
            # 如果用户被设置为必不中，重置奖品选择为"无"
            prize_combo = self.user_table.cellWidget(row, 3)
            prize_combo.setCurrentIndex(0)  # 0是"无"选项的索引
        
        success = self.probability_view_model.add_or_update_winner(user_id, winning_probability, prize_id)
        if not success:
            QMessageBox.critical(self, "错误", "更新中奖概率失败")
    
    def update_prize(self, user_id, prize_id, row):
        """更新必中奖品
        
        Args:
            user_id: 用户ID
            prize_id: 必中奖品ID
            row: 表格行索引
        """
        # 获取当前选择的中奖概率
        probability_combo = self.user_table.cellWidget(row, 2)
        winning_probability = probability_combo.currentData()
        
        # 如果用户被设置为必不中，则不允许设置必中奖品
        if winning_probability == 2:
            # 重置奖品选择为"无"
            prize_combo = self.user_table.cellWidget(row, 3)
            prize_combo.setCurrentIndex(0)  # 0是"无"选项的索引
            QMessageBox.warning(self, "警告", "必不中用户不能设置必中奖品")
            return
        
        success = self.probability_view_model.add_or_update_winner(user_id, winning_probability, prize_id)
        if not success:
            QMessageBox.critical(self, "错误", "更新必中奖品失败")
    
    def reset_probability(self, user_id):
        """重置中奖概率
        
        Args:
            user_id: 用户ID
        """
        success = self.probability_view_model.add_or_update_winner(user_id, 0, None)
        if success:
            QMessageBox.information(self, "提示", "重置成功")
            self.refresh_user_list()
        else:
            QMessageBox.critical(self, "错误", "重置失败")
    
    def search_user(self):
        """根据用户名搜索用户
        """
        username = self.search_input.text().strip()
        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            return
        
        # 加载所有用户数据
        users = self.probability_view_model.get_all_users_with_probability()
        
        # 过滤出匹配的用户
        filtered_users = [user for user in users if username in user['username']]
        
        if not filtered_users:
            QMessageBox.information(self, "提示", "未找到匹配的用户")
            return
        
        # 加载奖品列表
        from manager.prize_manager import PrizeManager
        prize_manager = PrizeManager('lottery.db')
        self.prizes = prize_manager.get_all_prizes()
        prize_manager.close()
        
        # 清空表格
        self.user_table.setRowCount(0)
        
        # 添加过滤后的用户数据
        for user in filtered_users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(user['username']))
            self.user_table.setItem(row, 1, QTableWidgetItem(user['employee_id']))
            
            # 添加中奖概率下拉框
            probability_combo = QComboBox()
            probability_combo.addItem("默认", 0)
            probability_combo.addItem("必中", 1)
            probability_combo.addItem("必不中", 2)
            
            # 设置当前值
            current_probability = user.get('winning_probability', 0)
            probability_combo.setCurrentIndex(current_probability)
            
            # 连接信号
            probability_combo.currentIndexChanged.connect(
                lambda index, uid=user['id'], combo=probability_combo, row=row: self.update_probability(uid, combo.currentData(), row)
            )
            
            self.user_table.setCellWidget(row, 2, probability_combo)
            
            # 添加奖品选择下拉框
            prize_combo = QComboBox()
            prize_combo.addItem("无", None)
            for prize in self.prizes:
                prize_combo.addItem(f"{prize['name']} ({prize['level']})", prize['id'])
            
            # 获取当前奖品ID
            current_prize_id = None
            winner_info = self.probability_view_model.get_winner_by_user_id(user['id'])
            if winner_info:
                current_prize_id = winner_info.get('prize_id')
            
            # 设置当前值
            for i in range(prize_combo.count()):
                if prize_combo.itemData(i) == current_prize_id:
                    prize_combo.setCurrentIndex(i)
                    break
            
            # 连接信号
            prize_combo.currentIndexChanged.connect(
                lambda index, uid=user['id'], combo=prize_combo, row=row: self.update_prize(uid, combo.currentData(), row)
            )
            
            self.user_table.setCellWidget(row, 3, prize_combo)
            
            # 添加操作按钮
            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)
            
            reset_button = QPushButton("重置")
            reset_button.setFixedHeight(30)
            reset_button.clicked.connect(lambda checked, uid=user['id']: self.reset_probability(uid))
            button_layout.addWidget(reset_button)
            
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.user_table.setCellWidget(row, 4, button_widget)
            
            # 设置行高
            self.user_table.setRowHeight(row, 70)
