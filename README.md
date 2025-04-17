# 🎬 VLC-BasedMulti-InstancePlayer

PyQt5와 VLC를 활용하여 구현한 고해상도의 멀티 모니터용 비디오 재생기이다. 최대 88인치 UHD 모니터를 포함한 여러 화면에서 각기 다른 영상을 동시에 재생한다.

---
## 📸 스크린샷

[![Image](https://github.com/user-attachments/assets/8606962d-ccf3-4162-aaec-13e88cf960ad)](https://www.youtube.com/watch?v=gkz1PFBG4NE)

---

## 📌 주요 기능

- 모니터 개별 영상 재생 (멀티 인스턴스 구조)
- 88인치 UHD 모니터 대응 및 자동 전체화면 처리
- 버튼 UI를 통한 5가지 영상 세트 동적 전환
- 마지막 영상 종료 감지 후 자동 초기 영상 복귀
- 오디오 출력 비활성화 및 VLC 종횡비/크기 설정
- `ctypes.CDLL`을 사용한 `libvlc.dll` 수동 로딩

---

## 🛠 기술 스택

- **Python**
- **PyQt5** // UI 구성 및 멀티윈도우 제어
- **libVLC** // 고성능 영상 재생
- **ctypes** // Windows에서 DLL 동적 로딩 처리

---

## 📁 프로젝트 구조

```
VLC-BasedMulti-InstancePlayer/
├── video/                # 영상 파일 디렉터리
├── button/               # 버튼 이미지 디렉터리
├── image/
│   └── background.jpg    # 메인 UI 배경 이미지
├── main.py               # 실행 파일 (전체 GUI 및 로직 포함)
└── README.md             # 프로젝트 설명 문서
```

---

## 🖥️ 설치 및 실행 방법

1. **VLC Media Player** (64비트) 설치  
   [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)

2. `video/`, `button/`, `image/` 디렉터리 구성

3. `main.py` 실행  
   ```bash
   python main.py
   ```
