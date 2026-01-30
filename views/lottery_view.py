from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
import random


class LotteryView(QWidget):
    """抽奖视图
    """
    
    def __init__(self, lottery_view_model):
        """初始化抽奖视图
        
        Args:
            lottery_view_model: 抽奖视图模型
        """
        super().__init__()
        self.lottery_view_model = lottery_view_model
        self.init_ui()
        self.is_drawing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_lottery_display)
    
    def init_ui(self):
        """初始化抽奖界面
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建抽奖区域
        lottery_layout = QVBoxLayout()
        lottery_layout.setSpacing(20)
        
        # 创建抽奖标题
        self.lottery_title = QLabel("抽奖区域")
        self.lottery_title.setAlignment(Qt.AlignCenter)
        self.lottery_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        lottery_layout.addWidget(self.lottery_title)
        
        # 创建抽奖显示区域
        self.lottery_display = QLabel("点击开始按钮开始抽奖")
        self.lottery_display.setAlignment(Qt.AlignCenter)
        self.lottery_display.setStyleSheet("font-size: 36px; font-weight: bold; padding: 50px;")
        lottery_layout.addWidget(self.lottery_display)
        
        # 创建总轮次设置区域
        rounds_layout = QHBoxLayout()
        rounds_layout.setSpacing(10)
        
        rounds_layout.addWidget(QLabel("抽奖总轮次:"))
        self.rounds_input = QLineEdit()
        self.rounds_input.setFixedWidth(100)
        self.rounds_input.setText(str(self.lottery_view_model.get_total_rounds()))
        rounds_layout.addWidget(self.rounds_input)
        
        self.set_rounds_button = QPushButton("设置")
        self.set_rounds_button.clicked.connect(self.set_total_rounds)
        rounds_layout.addWidget(self.set_rounds_button)
        
        # 显示当前轮次信息
        self.rounds_info = QLabel(f"当前轮次: 0/{self.lottery_view_model.get_total_rounds()}")
        rounds_layout.addWidget(self.rounds_info)
        
        # 添加是否允许重复中奖的复选框
        self.duplicate_checkbox = QCheckBox("允许重复抽中相同人员")
        self.duplicate_checkbox.setChecked(self.lottery_view_model.get_allow_duplicate_winners())
        self.duplicate_checkbox.stateChanged.connect(self.toggle_duplicate_winners)
        rounds_layout.addWidget(self.duplicate_checkbox)
        
        lottery_layout.addLayout(rounds_layout)
        
        # 创建开始/停止按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.start_button = QPushButton("开始抽奖")
        self.start_button.setFixedSize(150, 50)
        self.start_button.clicked.connect(self.start_lottery)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止抽奖")
        self.stop_button.setFixedSize(150, 50)
        self.stop_button.clicked.connect(self.stop_lottery)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.reload_button = QPushButton("重新加载数据")
        self.reload_button.setFixedSize(150, 50)
        self.reload_button.clicked.connect(self.reload_data)
        button_layout.addWidget(self.reload_button)
        
        lottery_layout.addLayout(button_layout)
        
        main_layout.addLayout(lottery_layout)
        
        # 创建抽奖结果区域
        result_layout = QVBoxLayout()
        result_layout.setSpacing(10)
        
        result_layout.addWidget(QLabel("抽奖结果"))
        
        # 创建结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["用户名", "工号", "奖品名称", "奖品等级"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        result_layout.addWidget(self.result_table)
        
        # 创建结果操作按钮
        result_button_layout = QHBoxLayout()
        result_button_layout.setSpacing(10)
        
        self.export_button = QPushButton("导出结果")
        self.export_button.clicked.connect(self.export_results)
        result_button_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("清空结果")
        self.clear_button.clicked.connect(self.clear_results)
        result_button_layout.addWidget(self.clear_button)
        
        result_layout.addLayout(result_button_layout)
        
        main_layout.addLayout(result_layout)
    
    def start_lottery(self):
        """开始抽奖
        """
        # 检查当前轮次是否已达到总轮次
        current_round = self.lottery_view_model.get_current_round()
        total_rounds = self.lottery_view_model.get_total_rounds()
        
        if current_round >= total_rounds:
            QMessageBox.warning(self, "警告", "已达到抽奖总轮次，请清空结果后再开始新的抽奖")
            return
        
        # 获取可参与抽奖的用户和可用奖品
        available_users = self.lottery_view_model.get_available_users()
        available_prizes = self.lottery_view_model.get_available_prizes()
        
        if not available_users:
            QMessageBox.warning(self, "警告", "没有可参与抽奖的用户")
            return
        
        if not available_prizes:
            QMessageBox.warning(self, "警告", "没有可用的奖品")
            return
        
        # 开始抽奖动画
        self.is_drawing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # 启动定时器，更新抽奖显示
        self.timer.start(50)  # 每50毫秒更新一次
    
    def stop_lottery(self):
        """停止抽奖
        """
        if not self.is_drawing:
            return
        
        # 停止定时器
        self.timer.stop()
        
        # 执行抽奖
        result = self.lottery_view_model.draw_lottery()
        if result:
            # 更新显示
            self.lottery_display.setText(f"中奖人: {result['username']}\n奖品: {result['prize_name']}")
            
            # 更新结果表格
            self.update_result_table()
        else:
            self.lottery_display.setText("抽奖失败，请检查数据")
        
        # 重置按钮状态
        self.is_drawing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 更新当前轮次信息
        current_round = self.lottery_view_model.get_current_round()
        total_rounds = self.lottery_view_model.get_total_rounds()
        self.rounds_info.setText(f"当前轮次: {current_round}/{total_rounds}")
        
        # 检查是否已达到总轮次
        if current_round >= total_rounds:
            QMessageBox.information(self, "提示", "已达到抽奖总轮次，请清空结果后再开始新的抽奖")
    
    def update_lottery_display(self):
        """更新抽奖显示
        """
        # 获取所有用户（包括必不中奖用户）和可用奖品
        all_users = self.lottery_view_model.users
        available_prizes = self.lottery_view_model.get_available_prizes()
        
        if not all_users or not available_prizes:
            return
        
        # 随机选择用户和奖品
        random_user = random.choice(all_users)
        random_prize = random.choice(available_prizes)
        
        # 更新显示
        self.lottery_display.setText(f"中奖人: {random_user['username']}\n奖品: {random_prize['name']}")
    
    def update_result_table(self):
        """更新结果表格
        """
        results = self.lottery_view_model.get_lottery_results()
        
        # 清空表格
        self.result_table.setRowCount(0)
        
        # 添加结果数据
        for result in results:
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            self.result_table.setItem(row, 0, QTableWidgetItem(result['username']))
            self.result_table.setItem(row, 1, QTableWidgetItem(result['employee_id']))
            self.result_table.setItem(row, 2, QTableWidgetItem(result['prize_name']))
            self.result_table.setItem(row, 3, QTableWidgetItem(result['prize_level']))
    
    def export_results(self):
        """导出抽奖结果
        """
        results = self.lottery_view_model.get_lottery_results()
        if not results:
            QMessageBox.warning(self, "警告", "没有抽奖结果可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存抽奖结果", "lottery_results.csv", "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        success = self.lottery_view_model.export_results(file_path)
        if success:
            QMessageBox.information(self, "提示", f"结果已导出到: {file_path}")
        else:
            QMessageBox.critical(self, "错误", "导出失败")
    
    def clear_results(self):
        """清空抽奖结果
        """
        reply = QMessageBox.question(
            self, "确认", "确定要清空抽奖结果吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.lottery_view_model.clear_results()
            self.lottery_display.setText("点击开始按钮开始抽奖")
            self.update_result_table()
            # 更新当前轮次信息
            total_rounds = self.lottery_view_model.get_total_rounds()
            self.rounds_info.setText(f"当前轮次: 0/{total_rounds}")
            QMessageBox.information(self, "提示", "结果已清空")
    
    def set_total_rounds(self):
        """设置抽奖总轮次
        """
        try:
            rounds = int(self.rounds_input.text())
            if rounds <= 0:
                QMessageBox.warning(self, "警告", "总轮次必须大于0")
                return
            self.lottery_view_model.set_total_rounds(rounds)
            self.rounds_info.setText(f"当前轮次: 0/{rounds}")
            QMessageBox.information(self, "提示", f"总轮次已设置为: {rounds}")
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字")
    
    def toggle_duplicate_winners(self, state):
        """切换是否允许重复抽中相同人员
        
        Args:
            state: 复选框状态
        """
        allow = state == Qt.Checked
        self.lottery_view_model.set_allow_duplicate_winners(allow)
    
    def reload_data(self):
        """重新加载数据
        """
        self.lottery_view_model.reload_data()
        QMessageBox.information(self, "提示", "数据已重新加载")
