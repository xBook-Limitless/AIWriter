from ui.iHome import create_main_window
from utils.env_checker import check_environment

def main():
    if not check_environment():
        return
    window = create_main_window()
    window.mainloop()

if __name__ == "__main__":
    root = create_main_window()
    if root:
        root.mainloop()
    else:
        print("窗口初始化失败，请检查错误日志") 