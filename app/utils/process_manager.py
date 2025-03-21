import os
import signal
import psutil
import atexit
from typing import List, Dict

class ProcessManager:
    def __init__(self):
        self._cleanup_in_progress = False
        self.processes: Dict[str, int] = {}
        atexit.register(self.cleanup_all)
    
    def register_process(self, name: str, pid: int):
        """注册一个新进程"""
        self.processes[name] = pid
        
    def cleanup_process(self, name: str) -> bool:
        """清理特定进程"""
        if name not in self.processes:
            return False
            
        pid = self.processes[name]
        try:
            process = psutil.Process(pid)
            process.terminate()
            try:
                process.wait(timeout=3)  # 等待进程终止
            except psutil.TimeoutExpired:
                # 如果进程没有及时终止，强制结束
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            return True
        except (psutil.NoSuchProcess, ProcessLookupError):
            return False
        finally:
            self.processes.pop(name, None)
            
    def cleanup_all(self):
        """清理所有注册的进程"""
        if self._cleanup_in_progress:  # 防止重复清理
            return
            
        self._cleanup_in_progress = True
        try:
            for name in list(self.processes.keys()):
                self.cleanup_process(name)
        finally:
            self._cleanup_in_progress = False
            
    def get_running_processes(self) -> List[str]:
        """获取当前运行的进程列表"""
        return list(self.processes.keys())

# 创建全局进程管理器实例
process_manager = ProcessManager() 