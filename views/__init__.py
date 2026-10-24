import sys

if sys.platform == "win32":      # chống mờ chữ trên màn hình Windows có thu phóng
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
