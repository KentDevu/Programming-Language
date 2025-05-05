from threading import Thread
from typing import List
from interpreter import Interpreter

class ParallelExecutor:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter

    def execute_parallel(self, blocks: List['Node']):
        threads = []
        for block in blocks:
            thread = Thread(target=self.interpreter.evaluate, args=(block,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()