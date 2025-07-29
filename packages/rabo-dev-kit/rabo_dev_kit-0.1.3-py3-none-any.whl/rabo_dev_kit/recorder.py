import os

class DataRecorder:
    """
    一个将文本数据记录到/tmp目录下文件的工具库。

    特性：
    - 所有文件都写入到/tmp/目录下的指定子目录中
    - 自动创建不存在的目录
    - 自动处理filename中的目录部分
    - 只支持文本数据记录
    """

    def __init__(self, base_dir: str = "data_logs"):
        """
        初始化文本数据记录器

        :param base_dir: 基础目录路径（会被自动修正到/tmp下）
        """
        # 拼接/tmp目录作为根目录

        self.base_dir = os.path.abspath(os.path.join(os.getenv('RDTP_SIM_LOG_PATH', '/tmp'), base_dir))
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """确保基础目录存在，如果不存在则创建"""
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，去除目录部分并给出提醒

        :param filename: 输入的文件名
        :return: 安全的纯文件名
        """
        original = filename
        # 获取纯文件名部分
        sanitized = os.path.basename(filename)

        # 如果原始文件名包含目录，打印提醒
        if original != sanitized:
            print(f"警告：文件名 '{original}' 中包含目录路径，已自动修正为 '{sanitized}'")

        return sanitized

    def _get_full_path(self, filename: str) -> str:
        """
        获取文件的完整路径（带文件名清理）

        :param filename: 文件名（会自动清理目录部分）
        :return: 完整文件路径
        """
        safe_name = self._sanitize_filename(filename)
        return os.path.join(self.base_dir, safe_name)

    def get_file_path(self, filename: str) -> str:
        """
        获取文件将写入的绝对路径

        :param filename: 文件名
        :return: 文件的绝对路径
        """
        return self._get_full_path(filename)

    def log_text(self, filename: str, content: str, mode: str = 'a') -> None:
        """
        记录文本数据到文件

        :param filename: 文件名
        :param content: 文本内容
        :param mode: 文件打开模式 ('w' 写入, 'a' 追加)
        """
        full_path = self._get_full_path(filename)

        with open(full_path, mode, encoding='utf-8') as f:
            f.write(content + '\n')
