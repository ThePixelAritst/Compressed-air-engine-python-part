import sys
import time
Windows_check = None
if (sys.platform).startswith("win"):
    Windows_check = True
    import msvcrt
else:
    Windows_check = False
    import select
    import termios
    import tty



if not Windows_check:
    class TerminalRaw:
        def __enter__(self):
            self.file_descriptor = sys.stdin.fileno() #returns file descriptor; 0 - in, 1 - out, 2 - error
            self.setttings = termios.tcgetattr(self.file_descriptor) # get terminal settings
            tty.setcbreak(self.file_descriptor) #swich to cbreak
        def __exit__(self, exc_type, exc, tb):
            termios.tcsetattr(self.file_descriptor, termios.TCSADRAIN, self.setttings)
else:
    class TerminalRaw:
        def __enter__(self):
            pass
        def __exit__(self, exc_type, exc, tb):
            pass


if Windows_check:
    def clear_keyboard_buffer():
        while msvcrt.kbhit():
            msvcrt.getch()

    def timeout_action(timeout=5):
        stop_time = time.monotonic() + timeout 
        while True:
         clear_keyboard_buffer()
         time.sleep(0.01)
         if msvcrt.kbhit():
             clear_keyboard_buffer() # initially I didnt have this line, but my logic was that if I read it will "reset". Didnt change anything tho
             return True
         elif time.monotonic() > stop_time: return False
    
else:
    def clear_keyboard_buffer():
        while not clear:
            clear, _, _ = select.select([sys.stdin],[],[],0)
            clear= bool(clear)
            sys.stdin.read(1)

    def timeout_action(timeout=5):
        pass