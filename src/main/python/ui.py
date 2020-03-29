import sys

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QVBoxLayout,QLabel,QDesktopWidget,QWidget,QApplication, QPushButton,
    QFormLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSize


class CustomNotificationWindow(QLabel):
    def close_app(self):
        self.parent.close()

    def snooze_alarm(self):
        print("Snoozing alarm")

    def __init__(self, parent):
        self.parent = parent
        QLabel.__init__(self, parent)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        row1 = QWidget()
        row1_layout = QHBoxLayout()
        row1.setLayout(row1_layout)

        # Create widget
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        row1_layout.addWidget(label)
        alarm_icon = parent.get_resource('alarm-clock.svg')
        pixmap = QPixmap(alarm_icon)
        label.setPixmap(pixmap)
        label.resize(pixmap.width(),pixmap.height())

        row1.setStyleSheet( f"""
                font-size: 17px;
                width: 100%;
                height: 100%;
                background-color: rgba(250,250,250,0%);    
                """)

        row2 = QWidget()
        row2_layout = QFormLayout()
        row2.setLayout(row2_layout)

        label = QLabel(parent.alarm_data['message'])
        label.setAlignment(Qt.AlignCenter)
        row2_layout.addWidget(label)

        row2.setStyleSheet( f"""
                padding: 10px;
                font-size: 20px;
                background-color: rgba(250,250,250,0%);    
                """)


        row3 = QWidget()
        row3_layout = QHBoxLayout()
        row3.setLayout(row3_layout)

        button1 = QPushButton("Snooze")
        button1.clicked.connect(self.snooze_alarm)
        button1.setCursor(Qt.PointingHandCursor)

        button2 = QPushButton("Close")
        button2.clicked.connect(self.close_app)
        button2.setCursor(Qt.PointingHandCursor)
        
        buttonStyle = """
                padding: 0;
                margin: 10px;
                font-size: 25px;
                background-color: rgba(210,210,210);
                color: rgba(50,50,50);
                """
        button1.setStyleSheet(buttonStyle)
        button2.setStyleSheet(buttonStyle)

        row3_layout.addWidget(button1)
        row3_layout.addWidget(button2)

        row3.setStyleSheet( """
                padding: 10px;
                font-size: 20px;
                background-color: rgba(250,250,250,0%);    
                """)


        main_layout.addWidget(row1)
        main_layout.addWidget(row2)
        main_layout.addWidget(row3)

        # mess with border-radius, thatDarklordGuy!
        self.setStyleSheet( """
                color: black;
                background-color: rgba(240,240,240,98%);
                text-align: center;
                border-radius: 10px;
                padding: 0px;
                width: 100%;
                height: 100%;
                """)


class Notification(QWidget):
    def __init__(self, get_resource, alarm_data):
        super().__init__()
        self.get_resource = get_resource
        self.alarm_data = alarm_data
        self.initUI()

    def initUI(self):
        VBox = QVBoxLayout()
        notification_window = CustomNotificationWindow(self)
        VBox.addWidget(notification_window)

        self.setLayout(VBox)
        # transparency cannot be set for window BG in style sheets, so...
        #self.setWindowOpacity(0.5) 
        self.setWindowFlags(
                  Qt.FramelessWindowHint # hides the window controls
                | Qt.WindowStaysOnTopHint # forces window to top... maybe
                | Qt.SplashScreen # this one hides it from the task bar!
                )
        # alternative way of making base window transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True) #100% transparent

        winwidth = 1000
        winheight = 600
        self.setGeometry(0, 0, winwidth, winheight)
        self.setWindowTitle('Alarm')

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())