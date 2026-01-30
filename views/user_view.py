from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class UserView(QWidget):
    """用户管理视图
    """
    
    def __init__(self, user_view_model):
        """初始化用户管理视图
        
        Args:
            user_view_model: 用户视图模型
        """
        super().__init__()
        self.user_view_model = user_view_model
        self.user_id_map = {}  # 存储行索引到用户ID的映射
        self.init_ui()
        self.refresh_user_list()
    
    def init_ui(self):
        """初始化用户管理界面
        """
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建添加用户区域
        add_layout = QHBoxLayout()
        add_layout.setSpacing(10)
        
        add_layout.addWidget(QLabel("用户名:"))
        self.username_input = QLineEdit()
        add_layout.addWidget(self.username_input)
        
        add_layout.addWidget(QLabel("工号:"))
        self.employee_id_input = QLineEdit()
        add_layout.addWidget(self.employee_id_input)
        
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_user)
        add_layout.addWidget(self.add_button)
        
        main_layout.addLayout(add_layout)
        
        # 创建查询区域
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
        
        # 创建批量操作区域
        batch_layout = QHBoxLayout()
        batch_layout.setSpacing(10)
        
        self.generate_template_button = QPushButton("生成模板")
        self.generate_template_button.clicked.connect(self.generate_user_template)
        batch_layout.addWidget(self.generate_template_button)
        
        self.import_csv_button = QPushButton("批量导入")
        self.import_csv_button.clicked.connect(self.import_users_from_csv)
        batch_layout.addWidget(self.import_csv_button)
        
        self.batch_delete_button = QPushButton("批量删除")
        self.batch_delete_button.clicked.connect(self.batch_delete_users)
        batch_layout.addWidget(self.batch_delete_button)
        
        main_layout.addLayout(batch_layout)
        
        # 创建用户列表
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["用户名", "工号", "操作"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.user_table)
    
    def add_user(self):
        """添加用户
        """
        username = self.username_input.text().strip()
        employee_id = self.employee_id_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "警告", "用户名不能为空")
            return
        
        success = self.user_view_model.add_user(username, employee_id)
        if success:
            QMessageBox.information(self, "提示", "添加成功")
            self.username_input.clear()
            self.employee_id_input.clear()
            self.refresh_user_list()
        else:
            QMessageBox.error(self, "错误", "添加失败")
    
    def search_user(self):
        """查询用户
        """
        username = self.search_input.text().strip()
        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            return
        
        users = self.user_view_model.search_users_by_username(username)
        if users:
            # 清空表格
            self.user_table.setRowCount(0)
            self.user_id_map.clear()  # 清空映射
            
            # 添加查询结果
            for user in users:
                row = self.user_table.rowCount()
                self.user_table.insertRow(row)
                self.user_table.setItem(row, 0, QTableWidgetItem(user['username']))
                self.user_table.setItem(row, 1, QTableWidgetItem(user['employee_id']))
                
                # 存储行索引到用户ID的映射
                self.user_id_map[row] = user['id']
                
                # 添加操作按钮
                button_layout = QHBoxLayout()
                button_layout.setSpacing(5)
                
                edit_button = QPushButton("修改")
                edit_button.setFixedHeight(30)
                edit_button.clicked.connect(lambda checked, uid=user['id']: self.edit_user(uid))
                button_layout.addWidget(edit_button)
                
                delete_button = QPushButton("删除")
                delete_button.setFixedHeight(30)
                delete_button.clicked.connect(lambda checked, uid=user['id']: self.delete_user(uid))
                button_layout.addWidget(delete_button)
                
                button_widget = QWidget()
                button_widget.setLayout(button_layout)
                self.user_table.setCellWidget(row, 2, button_widget)
                
                # 设置行高
                self.user_table.setRowHeight(row, 70)
        else:
            QMessageBox.information(self, "提示", "未找到用户")
    
    def refresh_user_list(self):
        """刷新用户列表
        """
        users = self.user_view_model.get_all_users()
        
        # 清空表格
        self.user_table.setRowCount(0)
        self.user_id_map.clear()  # 清空映射
        
        # 添加用户数据
        for user in users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(user['username']))
            self.user_table.setItem(row, 1, QTableWidgetItem(user['employee_id']))
            
            # 存储行索引到用户ID的映射
            self.user_id_map[row] = user['id']
            
            # 添加操作按钮
            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)
            
            edit_button = QPushButton("修改")
            edit_button.setFixedHeight(30)
            edit_button.clicked.connect(lambda checked, uid=user['id']: self.edit_user(uid))
            button_layout.addWidget(edit_button)
            
            delete_button = QPushButton("删除")
            delete_button.setFixedHeight(30)
            delete_button.clicked.connect(lambda checked, uid=user['id']: self.delete_user(uid))
            button_layout.addWidget(delete_button)
            
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            self.user_table.setCellWidget(row, 2, button_widget)
            
            # 设置行高
            self.user_table.setRowHeight(row, 70)
    
    def edit_user(self, user_id):
        """修改用户
        
        Args:
            user_id: 用户ID
        """
        user = self.user_view_model.get_user_by_id(user_id)
        if not user:
            QMessageBox.warning(self, "警告", "用户不存在")
            return
        
        # 创建修改对话框
        
        dialog = QDialog(self)
        dialog.setWindowTitle("修改用户")
        
        layout = QVBoxLayout()
        
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        username_input = QLineEdit(user['username'])
        username_layout.addWidget(username_input)
        layout.addLayout(username_layout)
        
        employee_id_layout = QHBoxLayout()
        employee_id_layout.addWidget(QLabel("工号:"))
        employee_id_input = QLineEdit(user['employee_id'])
        employee_id_layout.addWidget(employee_id_input)
        layout.addLayout(employee_id_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            username = username_input.text().strip()
            employee_id = employee_id_input.text().strip()
            
            if not username:
                QMessageBox.warning(self, "警告", "用户名不能为空")
                return
            
            success = self.user_view_model.update_user(user_id, username, employee_id)
            if success:
                QMessageBox.information(self, "提示", "修改成功")
                self.refresh_user_list()
            else:
                QMessageBox.error(self, "错误", "修改失败")
    
    def delete_user(self, user_id):
        """删除用户
        
        Args:
            user_id: 用户ID
        """
        reply = QMessageBox.question(
            self, "确认", "确定要删除该用户吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.user_view_model.delete_user(user_id)
            if success:
                QMessageBox.information(self, "提示", "删除成功")
                self.refresh_user_list()
            else:
                QMessageBox.error(self, "错误", "删除失败")
    
    def generate_user_template(self):
        """生成用户批量导入模板
        """
        template_path = self.user_view_model.generate_user_template()
        QMessageBox.information(self, "提示", f"模板已生成到: {template_path}")
    
    def import_users_from_csv(self):
        """从CSV文件批量导入用户
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        result = self.user_view_model.import_users_from_csv(file_path)
        if "error" in result:
            QMessageBox.critical(self, "错误", f"导入失败: {result['error']}")
        else:
            QMessageBox.information(
                self, "提示", 
                f"导入成功: {result['success']} 条，失败: {result['failed']} 条"
            )
            self.refresh_user_list()
    
    def batch_delete_users(self):
        """批量删除用户
        """
        # 获取选中的行
        selected_rows = set()
        for item in self.user_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请选择要删除的用户")
            return
        
        reply = QMessageBox.question(
            self, "确认", f"确定要删除选中的 {len(selected_rows)} 个用户吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for row in selected_rows:
                if row in self.user_id_map:
                    user_id = self.user_id_map[row]
                    success = self.user_view_model.delete_user(user_id)
                    if success:
                        success_count += 1
            
            QMessageBox.information(self, "提示", f"删除成功: {success_count} 个，失败: {len(selected_rows) - success_count} 个")
            self.refresh_user_list()
