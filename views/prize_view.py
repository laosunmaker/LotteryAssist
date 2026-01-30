from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QDialog, QDialogButtonBox, QShortcut
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence


class PrizeView(QWidget):
    """奖品管理视图
    """
    
    def __init__(self, prize_view_model, probability_view_model):
        """初始化奖品管理视图
        
        Args:
            prize_view_model: 奖品视图模型
            probability_view_model: 中奖概率视图模型
        """
        super().__init__()
        self.prize_view_model = prize_view_model
        self.probability_view_model = probability_view_model
        self.init_ui()
        self.prize_id_map = {}  # 存储行索引到奖品ID的映射
        self.refresh_prize_list()
        
        # 添加快捷键，Ctrl+H 隐藏/显示中奖概率管理按钮
        self.shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        self.shortcut.activated.connect(self.toggle_probability_button)
    
    def init_ui(self):
        """初始化奖品管理界面
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建添加奖品区域
        add_layout = QHBoxLayout()
        add_layout.setSpacing(10)
        
        add_layout.addWidget(QLabel("奖品名称:"))
        self.name_input = QLineEdit()
        add_layout.addWidget(self.name_input)
        
        add_layout.addWidget(QLabel("奖品等级:"))
        self.level_input = QLineEdit()
        add_layout.addWidget(self.level_input)
        
        add_layout.addWidget(QLabel("奖品数量:"))
        self.quantity_input = QLineEdit()
        add_layout.addWidget(self.quantity_input)
        
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_prize)
        add_layout.addWidget(self.add_button)
        
        main_layout.addLayout(add_layout)
        
        # 创建查询区域
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        search_layout.addWidget(QLabel("奖品名称查询:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("查询")
        self.search_button.clicked.connect(self.search_prize)
        search_layout.addWidget(self.search_button)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_prize_list)
        search_layout.addWidget(self.refresh_button)
        
        # 添加中奖概率管理按钮
        self.probability_button = QPushButton("中奖概率管理")
        self.probability_button.clicked.connect(self.show_probability_view)
        search_layout.addWidget(self.probability_button)
        # 默认隐藏中奖概率管理按钮
        self.probability_button.setVisible(False)
        
        main_layout.addLayout(search_layout)
        
        # 创建批量操作区域
        batch_layout = QHBoxLayout()
        batch_layout.setSpacing(10)
        
        self.generate_template_button = QPushButton("生成模板")
        self.generate_template_button.clicked.connect(self.generate_prize_template)
        batch_layout.addWidget(self.generate_template_button)
        
        self.import_csv_button = QPushButton("批量导入")
        self.import_csv_button.clicked.connect(self.import_prizes_from_csv)
        batch_layout.addWidget(self.import_csv_button)
        
        self.batch_delete_button = QPushButton("批量删除")
        self.batch_delete_button.clicked.connect(self.batch_delete_prizes)
        batch_layout.addWidget(self.batch_delete_button)
        
        main_layout.addLayout(batch_layout)
        
        # 创建奖品列表
        self.prize_table = QTableWidget()
        self.prize_table.setColumnCount(4)
        self.prize_table.setHorizontalHeaderLabels(["奖品名称", "奖品等级", "奖品数量", "操作"])
        self.prize_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.prize_table)
    
    def add_prize(self):
        """添加奖品
        """
        name = self.name_input.text().strip()
        level = self.level_input.text().strip()
        quantity = self.quantity_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "奖品名称不能为空")
            return
        
        if not level:
            QMessageBox.warning(self, "警告", "奖品等级不能为空")
            return
        
        try:
            quantity = int(quantity) if quantity else 0
        except ValueError:
            QMessageBox.warning(self, "警告", "奖品数量必须是整数")
            return
        
        success = self.prize_view_model.add_prize(name, level, quantity)
        if success:
            QMessageBox.information(self, "提示", "添加成功")
            self.name_input.clear()
            self.level_input.clear()
            self.quantity_input.clear()
            self.refresh_prize_list()
        else:
            QMessageBox.error(self, "错误", "添加失败")
    
    def search_prize(self):
        """查询奖品
        """
        name = self.search_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入奖品名称")
            return
        
        prizes = self.prize_view_model.search_prizes_by_name(name)
        if prizes:
            # 清空表格
            self.prize_table.setRowCount(0)
            self.prize_id_map.clear()  # 清空映射
            
            # 添加查询结果
            for prize in prizes:
                row = self.prize_table.rowCount()
                self.prize_table.insertRow(row)
                self.prize_table.setItem(row, 0, QTableWidgetItem(prize['name']))
                self.prize_table.setItem(row, 1, QTableWidgetItem(prize['level']))
                self.prize_table.setItem(row, 2, QTableWidgetItem(str(prize['quantity'])))
                
                # 存储行索引到奖品ID的映射
                self.prize_id_map[row] = prize['id']
                
                # 添加操作按钮
                button_layout = QHBoxLayout()
                button_layout.setSpacing(5)
                
                edit_button = QPushButton("修改")
                edit_button.setFixedHeight(30)
                edit_button.clicked.connect(lambda checked, pid=prize['id']: self.edit_prize(pid))
                button_layout.addWidget(edit_button)
                
                delete_button = QPushButton("删除")
                delete_button.setFixedHeight(30)
                delete_button.clicked.connect(lambda checked, pid=prize['id']: self.delete_prize(pid))
                button_layout.addWidget(delete_button)
                
                button_widget = QWidget()
                button_widget.setLayout(button_layout)
                self.prize_table.setCellWidget(row, 3, button_widget)
                
                # 设置行高
                self.prize_table.setRowHeight(row, 70)
        else:
            QMessageBox.information(self, "提示", "未找到奖品")
    
    def refresh_prize_list(self):
        """刷新奖品列表
        """
        prizes = self.prize_view_model.get_all_prizes()
        
        # 清空表格
        self.prize_table.setRowCount(0)
        
        # 添加奖品数据
        self.prize_id_map.clear()  # 清空映射
        for prize in prizes:
            row = self.prize_table.rowCount()
            self.prize_table.insertRow(row)
            self.prize_table.setItem(row, 0, QTableWidgetItem(prize['name']))
            self.prize_table.setItem(row, 1, QTableWidgetItem(prize['level']))
            self.prize_table.setItem(row, 2, QTableWidgetItem(str(prize['quantity'])))
            
            # 存储行索引到奖品ID的映射
            self.prize_id_map[row] = prize['id']
            
            # 添加操作按钮
            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)
            
            edit_button = QPushButton("修改")
            edit_button.setFixedHeight(30)
            edit_button.clicked.connect(lambda checked, pid=prize['id']: self.edit_prize(pid))
            button_layout.addWidget(edit_button)
            
            delete_button = QPushButton("删除")
            delete_button.setFixedHeight(30)
            delete_button.clicked.connect(lambda checked, pid=prize['id']: self.delete_prize(pid))
            button_layout.addWidget(delete_button)
            
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.prize_table.setCellWidget(row, 3, button_widget)
            
            # 设置行高
            self.prize_table.setRowHeight(row, 70)
    
    def edit_prize(self, prize_id):
        """修改奖品
        
        Args:
            prize_id: 奖品ID
        """
        prize = self.prize_view_model.get_prize_by_id(prize_id)
        if not prize:
            QMessageBox.warning(self, "警告", "奖品不存在")
            return
        
        # 创建修改对话框
        
        dialog = QDialog(self)
        dialog.setWindowTitle("修改奖品")
        
        layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("奖品名称:"))
        name_input = QLineEdit(prize['name'])
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("奖品等级:"))
        level_input = QLineEdit(prize['level'])
        level_layout.addWidget(level_input)
        layout.addLayout(level_layout)
        
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("奖品数量:"))
        quantity_input = QLineEdit(str(prize['quantity']))
        quantity_layout.addWidget(quantity_input)
        layout.addLayout(quantity_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            level = level_input.text().strip()
            quantity_str = quantity_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "警告", "奖品名称不能为空")
                return
            
            if not level:
                QMessageBox.warning(self, "警告", "奖品等级不能为空")
                return
            
            try:
                quantity = int(quantity_str) if quantity_str else 0
            except ValueError:
                QMessageBox.warning(self, "警告", "奖品数量必须是整数")
                return
            
            success = self.prize_view_model.update_prize(prize_id, name, level, quantity)
            if success:
                QMessageBox.information(self, "提示", "修改成功")
                self.refresh_prize_list()
            else:
                QMessageBox.error(self, "错误", "修改失败")
    
    def delete_prize(self, prize_id):
        """删除奖品
        
        Args:
            prize_id: 奖品ID
        """
        reply = QMessageBox.question(
            self, "确认", "确定要删除该奖品吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.prize_view_model.delete_prize(prize_id)
            if success:
                QMessageBox.information(self, "提示", "删除成功")
                self.refresh_prize_list()
            else:
                QMessageBox.error(self, "错误", "删除失败")
    
    def batch_delete_prizes(self):
        """批量删除奖品
        """
        # 获取选中的行
        selected_rows = set()
        for item in self.prize_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请选择要删除的奖品")
            return
        
        reply = QMessageBox.question(
            self, "确认", f"确定要删除选中的 {len(selected_rows)} 个奖品吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for row in selected_rows:
                if row in self.prize_id_map:
                    prize_id = self.prize_id_map[row]
                    success = self.prize_view_model.delete_prize(prize_id)
                    if success:
                        success_count += 1
            
            QMessageBox.information(self, "提示", f"删除成功: {success_count} 个，失败: {len(selected_rows) - success_count} 个")
            self.refresh_prize_list()
    
    def generate_prize_template(self):
        """生成奖品批量导入模板
        """
        template_path = self.prize_view_model.generate_prize_template()
        QMessageBox.information(self, "提示", f"模板已生成到: {template_path}")
    
    def import_prizes_from_csv(self):
        """从CSV文件批量导入奖品
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        result = self.prize_view_model.import_prizes_from_csv(file_path)
        if "error" in result:
            QMessageBox.critical(self, "错误", f"导入失败: {result['error']}")
        else:
            QMessageBox.information(
                self, "提示", 
                f"导入成功: {result['success']} 条，失败: {result['failed']} 条"
            )
            self.refresh_prize_list()
    
    def show_probability_view(self):
        """显示中奖概率管理界面
        """
        # 查找主窗口并切换到中奖概率管理界面
        from PyQt5.QtWidgets import QMainWindow
        
        # 遍历父窗口直到找到MainWindow
        parent = self.parent()
        while parent:
            if isinstance(parent, QMainWindow):
                # 直接调用主窗口的show_view方法
                parent.show_view(2)  # 中奖概率管理界面的索引
                return
            parent = parent.parent()
    
    def toggle_probability_button(self):
        """隐藏/显示中奖概率管理按钮
        """
        # 切换按钮的可见性
        self.probability_button.setVisible(not self.probability_button.isVisible())
