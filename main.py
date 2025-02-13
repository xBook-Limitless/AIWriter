from ui.iHome import create_main_window
from utils.env_checker import check_environment

def main():
    if not check_environment():
        return
    window = create_main_window()
    window.mainloop()

if __name__ == "__main__":
    main() 