import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon

from view_models.user_view_model import UserViewModel
from view_models.prize_view_model import PrizeViewModel
from view_models.probability_view_model import ProbabilityViewModel
from view_models.lottery_view_model import LotteryViewModel
from views.user_view import UserView
from views.prize_view import PrizeView
from views.probability_view import ProbabilityView
from views.lottery_view import LotteryView


class LotteryApp(QMainWindow):
    """抽奖应用程序主类
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("抽奖助手")
        self.setGeometry(100, 100, 1000, 800)
        
        # 加载样式
        self.load_styles()
        
        # 数据库路径
        self.db_path = "lottery.db"
        
        # 初始化视图模型
        self.user_view_model = UserViewModel(self.db_path)
        self.prize_view_model = PrizeViewModel(self.db_path)
        self.probability_view_model = ProbabilityViewModel(self.db_path)
        self.lottery_view_model = LotteryViewModel(self.db_path)
        
        # 初始化视图
        self.user_view = UserView(self.user_view_model)
        self.prize_view = PrizeView(self.prize_view_model, self.probability_view_model)
        self.probability_view = ProbabilityView(self.probability_view_model)
        self.lottery_view = LotteryView(self.lottery_view_model)
        
        # 初始化主界面
        self.init_ui()
    
    def load_styles(self):
        """加载样式文件
        """
        try:
            with open("style.qss", "r", encoding="utf-8") as f:
                style_sheet = f.read()
            self.setStyleSheet(style_sheet)
        except Exception as e:
            # print(f"加载样式文件失败: {e}")
            pass
    
    def init_ui(self):
        """初始化主界面
        """
        # 创建主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建左侧导航栏
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(10)
        
        # 创建导航按钮
        self.user_btn = QPushButton("人员管理")
        self.user_btn.setFixedSize(150, 50)
        self.user_btn.clicked.connect(lambda: self.show_view(0))
        
        self.prize_btn = QPushButton("奖品管理")
        self.prize_btn.setFixedSize(150, 50)
        self.prize_btn.clicked.connect(lambda: self.show_view(1))
        
        self.lottery_btn = QPushButton("开始抽奖")
        self.lottery_btn.setFixedSize(150, 50)
        self.lottery_btn.clicked.connect(lambda: self.show_view(3))
        
        # 添加按钮到导航布局
        nav_layout.addWidget(self.user_btn)
        nav_layout.addWidget(self.prize_btn)
        nav_layout.addWidget(self.lottery_btn)
        nav_layout.addStretch()
        
        # 创建右侧内容区域
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.user_view)
        self.stacked_widget.addWidget(self.prize_view)
        self.stacked_widget.addWidget(self.probability_view)
        self.stacked_widget.addWidget(self.lottery_view)
        
        # 添加导航栏和内容区域到主布局
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.stacked_widget, 1)
    
    def show_view(self, index):
        """显示指定的视图
        
        Args:
            index: 视图索引
        """
        self.stacked_widget.setCurrentIndex(index)
    
    def event(self, event):
        """事件处理
        
        Args:
            event: 事件
            
        Returns:
            是否处理了事件
        """
        if event.type() == QEvent.User and hasattr(event, 'view_index'):
            self.show_view(event.view_index)
            return True
        return super().event(event)
    
    def closeEvent(self, event):
        """关闭事件处理
        
        Args:
            event: 关闭事件
        """
        # 关闭数据库连接
        self.user_view_model.close()
        self.prize_view_model.close()
        self.probability_view_model.close()
        self.lottery_view_model.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryApp()
    window.setWindowIcon(QIcon('./cat.ico'))
    window.show()
    sys.exit(app.exec())
