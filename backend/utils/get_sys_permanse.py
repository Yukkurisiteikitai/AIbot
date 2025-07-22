#!/usr/bin/env python3
"""
クロスプラットフォーム システムモニター（JSON関数版）
Windows・macOS対応、標準モジュールのみ使用
GPU使用率、CPU使用率、VRAM、RAMを取得してJSON形式で返す
"""

import platform
import subprocess
import json
import time
import re
from typing import Dict, Optional, Union


def get_cpu_usage() -> float:
    """CPU使用率を取得（%）"""
    os_type = platform.system()
    
    if os_type == "Windows":
        try:
            # PowerShellでCPU使用率を取得
            cmd = ['powershell', '-Command', 
                   'Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
            
    elif os_type == "Darwin":  # macOS
        try:
            # topコマンドでCPU使用率を取得
            cmd = ['top', '-l', '1', '-n', '0']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # "CPU usage: 12.34% user, 5.67% sys, 81.99% idle" の形式から解析
                cpu_line = [line for line in result.stdout.split('\n') if 'CPU usage' in line]
                if cpu_line:
                    # idle以外の使用率を合計
                    idle_match = re.search(r'(\d+\.?\d*)%\s+idle', cpu_line[0])
                    if idle_match:
                        idle_percent = float(idle_match.group(1))
                        return 100.0 - idle_percent
        except Exception:
            pass
            
    return 0.0


def get_memory_info() -> Dict[str, Union[int, float]]:
    """メモリ情報を取得（MB単位）"""
    os_type = platform.system()
    
    if os_type == "Windows":
        try:
            # 物理メモリ情報
            cmd = ['wmic', 'OS', 'get', 'TotalVisibleMemorySize,AvailableMemorySize', '/format:value']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                total_kb = 0
                available_kb = 0
                for line in result.stdout.split('\n'):
                    if 'TotalVisibleMemorySize' in line:
                        total_kb = int(line.split('=')[1].strip())
                    elif 'AvailableMemorySize' in line:
                        available_kb = int(line.split('=')[1].strip())
                
                total_mb = total_kb / 1024
                available_mb = available_kb / 1024
                used_mb = total_mb - available_mb
                usage_percent = (used_mb / total_mb) * 100
                
                return {
                    'total_mb': int(total_mb),
                    'used_mb': int(used_mb),
                    'available_mb': int(available_mb),
                    'usage_percent': round(usage_percent, 2)
                }
        except Exception:
            pass
            
    elif os_type == "Darwin":  # macOS
        try:
            # vm_statコマンドでメモリ情報を取得
            cmd = ['vm_stat']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # ページサイズを取得
                page_size = 4096  # 通常は4KB
                
                # 各メモリタイプのページ数を解析
                free_pages = 0
                for line in result.stdout.split('\n'):
                    if 'Pages free:' in line:
                        free_pages = int(line.split(':')[1].strip().rstrip('.'))
                
                # 物理メモリ総量を取得
                cmd2 = ['sysctl', '-n', 'hw.memsize']
                result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=10)
                if result2.returncode == 0:
                    total_bytes = int(result2.stdout.strip())
                    total_mb = total_bytes / (1024 * 1024)
                    
                    free_mb = (free_pages * page_size) / (1024 * 1024)
                    used_mb = total_mb - free_mb
                    usage_percent = (used_mb / total_mb) * 100
                    
                    return {
                        'total_mb': int(total_mb),
                        'used_mb': int(used_mb),
                        'available_mb': int(free_mb),
                        'usage_percent': round(usage_percent, 2)
                    }
        except Exception:
            pass
            
    return {'total_mb': 0, 'used_mb': 0, 'available_mb': 0, 'usage_percent': 0.0}


def get_gpu_info() -> Dict[str, Union[str, int, float]]:
    """GPU情報を取得"""
    os_type = platform.system()
    
    if os_type == "Windows":
        try:
            # NVIDIA GPU情報（nvidia-smi）
            cmd = ['nvidia-smi', '--query-gpu=name,utilization.gpu,memory.total,memory.used,memory.free', 
                   '--format=csv,noheader,nounits']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0].strip():
                    parts = lines[0].split(', ')
                    if len(parts) >= 5:
                        return {
                            'name': parts[0].strip(),
                            'usage_percent': float(parts[1].strip()),
                            'vram_total_mb': int(parts[2].strip()),
                            'vram_used_mb': int(parts[3].strip()),
                            'vram_free_mb': int(parts[4].strip())
                        }
            
            # NVIDIA失敗時、WMIでGPU情報を取得
            cmd = ['wmic', 'path', 'win32_VideoController', 'get', 'name,AdapterRAM', '/format:value']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                name = ""
                adapter_ram = 0
                for line in result.stdout.split('\n'):
                    if 'Name=' in line and line.split('=')[1].strip():
                        name = line.split('=')[1].strip()
                    elif 'AdapterRAM=' in line and line.split('=')[1].strip():
                        adapter_ram = int(line.split('=')[1].strip())
                        break
                
                if name:
                    return {
                        'name': name,
                        'usage_percent': 0.0,  # WMIでは使用率取得不可
                        'vram_total_mb': adapter_ram // (1024 * 1024) if adapter_ram > 0 else 0,
                        'vram_used_mb': 0,
                        'vram_free_mb': adapter_ram // (1024 * 1024) if adapter_ram > 0 else 0
                    }
                    
        except Exception:
            pass
            
    elif os_type == "Darwin":  # macOS
        try:
            # system_profilerでGPU情報を取得
            cmd = ['system_profiler', 'SPDisplaysDataType', '-json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'SPDisplaysDataType' in data and data['SPDisplaysDataType']:
                    gpu_info = data['SPDisplaysDataType'][0]
                    name = gpu_info.get('sppci_model', 'Unknown GPU')
                    
                    # VRAMサイズを解析
                    vram_str = gpu_info.get('sppci_vram', '0 MB')
                    vram_mb = 0
                    if 'MB' in vram_str:
                        vram_mb = int(re.search(r'(\d+)', vram_str).group(1))
                    elif 'GB' in vram_str:
                        vram_gb = float(re.search(r'(\d+(?:\.\d+)?)', vram_str).group(1))
                        vram_mb = int(vram_gb * 1024)
                    
                    return {
                        'name': name,
                        'usage_percent': 0.0,  # macOSでは標準で使用率取得困難
                        'vram_total_mb': vram_mb,
                        'vram_used_mb': 0,
                        'vram_free_mb': vram_mb
                    }
                    
        except Exception:
            pass
            
    return {
        'name': 'Unknown',
        'usage_percent': 0.0,
        'vram_total_mb': 0,
        'vram_used_mb': 0,
        'vram_free_mb': 0
    }


def get_system_info() -> str:
    """全システム情報を取得してJSON文字列で返す"""
    info = {
        'os': platform.system(),
        'cpu_usage_percent': get_cpu_usage(),
        'memory': get_memory_info(),
        'gpu': get_gpu_info(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    return json.dumps(info, indent=2, ensure_ascii=False)


def get_system_info_dict() -> Dict:
    """全システム情報を取得して辞書形式で返す"""
    return {
        'os': platform.system(),
        'cpu_usage_percent': get_cpu_usage(),
        'memory': get_memory_info(),
        'gpu': get_gpu_info(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }


def main():
    """使用例"""
    print("=== JSON文字列形式 ===")
    json_result = get_system_info()
    print(json_result)
    
    print("\n=== 辞書形式 ===")
    dict_result = get_system_info_dict()
    print(dict_result)
    
    print("\n=== 個別取得例 ===")
    print(f"CPU使用率: {get_cpu_usage():.1f}%")
    print(f"メモリ情報: {get_memory_info()}")
    print(f"GPU情報: {get_gpu_info()}")


if __name__ == "__main__":
    main()