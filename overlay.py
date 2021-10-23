from PIL import ImageTk
import tkinter
import threading
import win32gui


class Overlay(threading.Thread):
    _root: tkinter.Tk
    _canvas: tkinter.Canvas
    _should_be_showing: bool
    _showing: bool

    _image_to_show = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self) -> None:
        self._root = tkinter.Tk()
        self._root.title('AutoPlayerOverlay')
        self._root.geometry('1920x995+0+44')
        self._root.attributes('-disabled', True)
        self._root.attributes('-transparentcolor','#f0f0f0')
        self._root.attributes('-topmost', True)
        self._root.overrideredirect(True)

        self._canvas = tkinter.Canvas(self._root, bd=0, highlightthickness=0)
        self._canvas.pack(expand=True, fill=tkinter.BOTH)

        self._should_be_showing = True
        self._showing = True
        self._image_to_show = None

        while True:
            handle = win32gui.GetForegroundWindow()

            if 'VisualBoyAdvance' not in win32gui.GetWindowText(handle):
                self._should_be_showing = False

            # print('Should be showing:', self._should_be_showing)
            # print('Showing:', self._showing)
            if not self._should_be_showing:
                if self._showing:
                    self._hide()
                continue
            elif not self._showing:
                self._show()

            if self._image_to_show is not None:
                self._canvas.delete('all')
                self._root.img = ImageTk.PhotoImage(self._image_to_show)
                self._canvas.create_image(0, 0, anchor=tkinter.NW, image=self._root.img)
                self._image_to_show = None

            self._root.update()

    def set(self, image) -> None:
        self._image_to_show = image

    def show(self) -> None:
        self._should_be_showing = True

    def _show(self) -> None:
        self._root.deiconify()
        self._showing = True

    def hide(self) -> None:
        self._should_be_showing = False

    def _hide(self) -> None:
        self._root.withdraw()
        self._showing = False
