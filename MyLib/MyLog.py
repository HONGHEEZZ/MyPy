import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) #모든 레벨의 로그를 Hander들에게 전달해야 합니다.
formatter = logging.Formatter('%(asctime)s:%(module)s:%(levelname)s:%(message)s', '%Y-%m-%d %H:%M:%S')

# INFO 레벨 이상의 로그를 콘솔에 출력하는 handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_debug_handler = logging.FileHandler('debug.log')
file_debug_handler.setLevel(logging.DEBUG)
file_debug_handler.setFormatter(formatter)
logger.addHandler(file_debug_handler)

file_error_handler = logging.FileHandler('error.log')
file_error_handler.setLevel(logging.ERROR)
file_error_handler.setFormatter(formatter)
logger.addHandler(file_debug_handler)


class LogStringHandler(logging.Handler):
    def __init__(self, target_widget):
        super().__init__()
        self.target_widget = target_widget

    def emit(self, record):
        self.target_widget.append(f'{record.asctime}:{record.module}:{record.levelname}:{record.getMessage()}')
