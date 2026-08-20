import base64
import win32api
import win32con
import win32gui
import win32ui

def get_dimensions():
    width  = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left   = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top    = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot(name='screenshot'):
    # Get handle to the entire desktop
    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    # Create a device context FROM the desktop handle
    desktop_dc = win32gui.GetWindowDC(hdesktop)

    # Create a GDI device context object from it
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # Create a memory-based device context (where we'll store the capture)
    mem_dc = img_dc.CreateCompatibleDC()

    # Create a blank bitmap object sized to the screen
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)

    # Point the memory DC at our bitmap object
    mem_dc.SelectObject(screenshot)

    # BitBlt = bit block transfer — copies pixels from screen into memory DC
    # Think of it as a GPU-level memcpy
    mem_dc.BitBlt(
        (0, 0),              # destination start point
        (width, height),     # size to copy
        img_dc,              # source (the real screen)
        (left, top),         # source start point
        win32con.SRCCOPY     # just copy, no fancy blending
    )

    # Save bitmap to file
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp')

    # Clean up GDI resources (important — GDI leaks are nasty)
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


def run():
    screenshot()
    with open('screenshot.bmp', 'rb') as f:
        img = f.read()
    return img


if __name__ == '__main__':
    screenshot()

