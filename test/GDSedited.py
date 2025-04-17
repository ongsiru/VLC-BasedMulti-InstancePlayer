import ctypes
import os
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QMetaObject, pyqtSlot, Q_ARG
from PyQt5.QtGui import QPixmap


class VideoWindow(QWidget):
    """VLC 기반 VideoWindow"""

    def __init__(self, title, monitor_geometry, video_files, parent=None, is_last_video=False):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(*monitor_geometry)
        self.parent = parent  # 부모 VideoPlayer 객체 저장
        self.is_last_video = is_last_video  # 마지막 비디오인지 확인

        VLC_PATH = "C:/Program Files/VideoLAN/VLC/"  # 64비트 VLC

        if VLC_PATH not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + VLC_PATH

        # libvlc.dll을 강제로 로드
        vlc_lib_path = os.path.join(VLC_PATH, "libvlc.dll")
        ctypes.CDLL(vlc_lib_path)

        import vlc  # libvlc.dll 로드 후 vlc 모듈 가져오기

        self.instance = vlc.Instance("--aout=coreaudio", "--autoscale")  # 오디오 출력 비활성화
        self.player = self.instance.media_player_new()

        # 영상 표시를 위한 QWidget
        self.video_widget = QWidget(self)
        self.video_widget.setGeometry(0, 0, self.width(), self.height())

        # 플랫폼별 VLC에 위젯 연결
        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_widget.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_widget.winId()))

        # 비디오 파일 목록
        self.video_files = video_files
        self.current_index = 0
        self.load_video(self.video_files[self.current_index])

        # 영상 종료 이벤트 연결
        self.player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached, self.handle_video_finished
        )

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def moveEvent(self, event):
        """창 이동 시 현재 화면이 88인치(3840×2160)라면 강제 조정"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        print("Screen geometry:", screen_geometry.width(), "x", screen_geometry.height())
        # 88인치 모니터(3840×2160) 감지 시 강제 조정
        if screen_geometry.width() == 3840 and screen_geometry.height() == 2160:
            print("88인치 모니터 감지됨: 해상도 강제 조정")
            self.setGeometry(0, 0, 3840, 2160)
            if self.is_last_video:
                aspect_ratio = f"{3840}:{2160}"
                self.player.video_set_aspect_ratio(aspect_ratio.encode())
                self.player.video_set_scale(0)
        super().moveEvent(event)

    def load_video(self, video_path):
        """VLC 미디어 로드 및 재생"""
        media = self.instance.media_new(video_path)
        self.player.set_media(media)
        # 종횡비 강제 해제
        self.player.video_set_aspect_ratio(None)
        if self.is_last_video:
            self.player.video_set_scale(0)  # VLC가 창 크기에 맞춰 자동 조정
        self.player.play()

    def switch_video(self, video_path):
        """비디오 경로를 받아 빠르게 전환"""
        self.load_video(video_path)

    def handle_video_finished(self, event):
        """영상 종료 시 마지막 영상만 VideoPlayer에 알림"""
        if self.is_last_video:
            print(f"마지막 영상 종료됨: {self.windowTitle()}")
            self.parent.notify_video_finished()

    def toggle_pause(self):
        """비디오 재생/일시정지 토글"""
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def resizeEvent(self, event):
        """전체화면(F11) 전환 시 비디오 위젯 크기 자동 조정 및 종횡비 강제 설정"""
        self.video_widget.setGeometry(0, 0, self.width(), self.height())
        if self.is_last_video:
            # 현재 창 크기에 맞춰 종횡비 설정 (예: "3840:2160")
            aspect_ratio = f"{self.width()}:{self.height()}"
            self.player.video_set_aspect_ratio(aspect_ratio.encode())
            self.player.video_set_scale(0)
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.instance().quit()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()


class VideoPlayer(QWidget):
    """메인 비디오 관리 패널 (VLC 기반)"""

    def __init__(self, monitors, video_sets):
        super().__init__()
        self.monitors = monitors
        self.video_sets = video_sets
        self.current_set_index = 0
        self.video_windows = []
        self.video_finished = False

        self.setWindowTitle("VLC Video Switcher")
        self.setGeometry(100, 100, 1920, 1080)

        self.initUI()
        self.init_video_windows()

    def initUI(self):
        """UI 초기화 (배경 및 버튼)"""
        background_path = os.path.join(os.getcwd(), "image", "background.jpg")
        self.background = QLabel(self)
        if os.path.exists(background_path):
            self.background.setPixmap(QPixmap(background_path))
        else:
            self.background.setStyleSheet("background-color: gray;")
        self.background.setGeometry(self.rect())
        self.background.lower()

        self.buttons = []
        button_width, button_height = 250, 380
        left_margin, right_margin = 300, 300
        total_width = self.width() - (left_margin + right_margin)
        button_spacing = (total_width - (5 * button_width)) // 4
        y_offset = self.height() - button_height - 260

        for i in range(1, 6):
            btn = QPushButton(self)
            btn.button_id = i
            btn.setFixedSize(button_width, button_height)
            btn.move(left_margin + (i - 1) * (button_width + button_spacing), y_offset)
            btn.clicked.connect(lambda _, i=i: self.switch_videos(i))
            self.buttons.append(btn)

        self.update_button_images()

    def init_video_windows(self):
        """각 모니터별 VideoWindow 생성"""
        for i, monitor_geometry in enumerate(self.monitors):
            is_last_video = (i == len(self.monitors) - 1)  # 마지막 모니터에만 True 설정
            window = VideoWindow(f"Monitor {i + 1}", tuple(monitor_geometry), self.video_sets[i], parent=self,
                                 is_last_video=is_last_video)
            if is_last_video:
                window.showFullScreen()  # 88인치 모니터는 전체화면 모드로 표시
            else:
                window.show()
            self.video_windows.append(window)

        self.switch_videos(0)

    def update_button_images(self, active_index=None):
        print("check", active_index)
        for i, btn in enumerate(self.buttons, start=1):
            button_path = os.path.join(os.getcwd(), "button", f"button{i}.png")
            if active_index == i:
                button_path = os.path.join(os.getcwd(), "button", f"button{i}-1.png")
            if os.path.exists(button_path):
                btn.setStyleSheet(f"border: none; background-image: url('{button_path.replace(os.sep, '/')}');")
            else:
                btn.setStyleSheet("border: 1px solid black; background-color: lightgray;")

    @pyqtSlot(int)
    def switch_videos(self, set_index):
        if set_index < 0 or set_index >= len(self.video_sets):
            return

        print("switch", set_index)

        if set_index == self.current_set_index:
            set_index = 0

        self.current_set_index = set_index
        self.video_finished = False
        video_set = self.video_sets[set_index]

        for i, video_path in enumerate(video_set):
            if i < len(self.video_windows):
                self.video_windows[i].switch_video(video_path)

        self.update_button_images(active_index=set_index)

    def notify_video_finished(self):
        if not self.video_finished:
            print("Video finished notification received")
            self.video_finished = True
        QMetaObject.invokeMethod(self, "switch_videos", Qt.QueuedConnection, Q_ARG(int, 0))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for window in self.video_windows:
                window.toggle_pause()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.instance().quit()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 모니터 해상도 정보 (마지막 모니터는 88인치, 3840×2160)
    monitors = [
        (0, 0, 640, 360),
        (650, 0, 640, 360),
        (0, 370, 640, 360),
        (650, 370, 3840, 2160)
    ]

    video_directory = os.path.join(os.getcwd(), "video")
    video_sets = [
        [os.path.join(video_directory, f"default{i + 1}.mp4") for i in range(4)],
        [os.path.join(video_directory, f"1-{i + 1}.mp4") for i in range(4)],
        [os.path.join(video_directory, f"2-{i + 1}.mp4") for i in range(4)],
        [os.path.join(video_directory, f"3-{i + 1}.mp4") for i in range(4)],
        [os.path.join(video_directory, f"4-{i + 1}.mp4") for i in range(4)],
        [os.path.join(video_directory, f"5-{i + 1}.mp4") for i in range(4)]
    ]

    player = VideoPlayer(monitors, video_sets)
    player.show()

    sys.exit(app.exec_())
