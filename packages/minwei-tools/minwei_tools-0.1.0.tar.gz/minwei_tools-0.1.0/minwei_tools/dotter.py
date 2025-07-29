# A dotter while I'm thinking

import itertools
import sys
import threading
import time

piano = ['▉▁▁▁▁▁', '▉▉▂▁▁▁', '▉▉▉▃▁▁', '▉▉▉▉▅▁', 
         '▉▉▉▉▉▇', '▉▉▉▉▉▉', '▉▉▉▉▇▅', '▉▉▉▆▃▁', 
         '▉▉▅▃▁▁', '▉▇▃▁▁▁', '▇▃▁▁▁▁', '▃▁▁▁▁▁', 
         '▁▁▁▁▁▁', '▁▁▁▁▁▉', '▁▁▁▁▃▉', '▁▁▁▃▅▉', 
         '▁▁▃▅▇▉', '▁▃▅▇▉▉', '▃▅▉▉▉▉', '▅▉▉▉▉▉',
         '▇▉▉▉▉▉', '▉▉▉▉▉▉', '▇▉▉▉▉▉', '▅▉▉▉▉▉', 
         '▃▅▉▉▉▉', '▁▃▅▉▉▉', '▁▁▃▅▉▉', '▁▁▁▃▅▉',
         '▁▁▁▁▃▅', '▁▁▁▁▁▃', '▁▁▁▁▁▁', '▁▁▁▁▁▁', 
         '▁▁▃▁▁▁', '▁▃▅▃▁▁', '▁▅▉▅▁▁', '▃▉▉▉▃▁', 
         '▅▉▁▉▅▃', '▇▃▁▃▇▅', '▉▁▁▁▉▇', '▉▅▃▁▃▅', 
         '▇▉▅▃▅▇', '▅▉▇▅▇▉', '▃▇▉▇▉▅', '▁▅▇▉▇▃', 
         '▁▃▅▇▅▁', '▁▁▃▅▃▁', '▁▁▁▃▁▁', '▁▁▁▁▁▁',
        ]

slash = ["\\","|","/", "-"]

class Dotter:
    # A dotter while I'm thinking
    def __init__(self, message: str = "Thinking", delay: float = 0.5, 
                 cycle: list[str] = ["", ".", ". .", ". . ."], 
                 show_timer: bool = False) -> None:
        
        self.spinner = itertools.cycle(cycle)
        self.delay = delay
        self.message = message
        self.show_timer = show_timer
        self.running = False
        self.dotter_thread = None
        self.start_time = None

    def format_elapsed(self, elapsed: float) -> str:
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        # elif elapsed < 60:
        #     return f"{int(elapsed)}s"
        else:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"{mins}m{secs:02d}s"

    def dot(self):
        self.start_time = time.time()
        while self.running:
            elapsed = time.time() - self.start_time
            timer_str = f" [{self.format_elapsed(elapsed)}]" if self.show_timer else ""
            text = f"{self.message} {next(self.spinner)}{timer_str}"
            sys.stdout.write(f"\r{text}")
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write(f"\r{' ' * (len(text))}\r")  # Clear line

    def update_message(self, new_message, delay=0.1):
        time.sleep(delay)
        sys.stdout.write(
            f"\r{' ' * (len(self.message) + 20)}\r"
        )  # Clear the current message
        sys.stdout.flush()
        self.message = new_message

    def __enter__(self):
        self.running = True
        self.dotter_thread = threading.Thread(target=self.dot)
        self.dotter_thread.start()

    def __exit__(self, *args) -> None:
        self.running = False
        if self.dotter_thread is not None:
            self.dotter_thread.join()
        sys.stdout.write(f"\r{' ' * (len(self.message) + 20)}\r")
        sys.stdout.flush()


if __name__ == "__main__":
    from time import sleep

    with Dotter(cycle = piano, message="Loading", delay=0.1, show_timer=1) as d:
        sleep(120)
