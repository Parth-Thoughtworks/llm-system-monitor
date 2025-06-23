#!/usr/bin/env python3
"""
System Information Collector
Handles all system information gathering using psutil
"""

import psutil
import platform
import datetime
from typing import Dict, Any, List


class SystemInfoCollector:
    """
    Handles all system information collection.
    Pure system monitoring without any LLM dependencies.
    """

    def __init__(self):
        """Initialize the system info collector"""
        self.available_functions = {
            'get_battery_info': self.get_battery_info,
            'get_cpu_info': self.get_cpu_info,
            'get_memory_info': self.get_memory_info,
            'get_disk_info': self.get_disk_info,
            'get_network_info': self.get_network_info,
            'get_processes_info': self.get_processes_info,
            'get_system_info': self.get_system_info,
            'get_uptime_info': self.get_uptime_info,
            'get_temperature_info': self.get_temperature_info
        }
        print("📊 SystemInfoCollector initialized")
        self._test_core_functions()

    def _test_core_functions(self):
        """Test core system functions"""
        try:
            self.get_battery_info()
            self.get_cpu_info()
            self.get_memory_info()
            print("✅ Core system functions working")
        except Exception as e:
            print(f"⚠️  Warning: {e}")

    def get_function_list(self) -> List[str]:
        """Return list of available system functions"""
        return list(self.available_functions.keys())

    def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call a system function by name"""
        if function_name in self.available_functions:
            try:
                return self.available_functions[function_name](**kwargs)
            except Exception as e:
                return {'error': f'Error calling {function_name}: {str(e)}'}
        else:
            return {'error': f'Unknown function: {function_name}'}

    def call_multiple_functions(self, function_names: List[str]) -> Dict[str, Any]:
        """Call multiple system functions and return combined results"""
        results = {}
        for func_name in function_names:
            results[func_name] = self.call_function(func_name)
        return results

    def get_battery_info(self) -> Dict[str, Any]:
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percentage': battery.percent,
                    'plugged_in': battery.power_plugged,
                    'time_left_seconds': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                    'time_left_formatted': f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Charging/Unknown"
                }
            else:
                return {'error': 'Battery information not available (desktop system?)'}
        except Exception as e:
            return {'error': f'Error getting battery info: {str(e)}'}

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_per_core = psutil.cpu_percent(percpu=True, interval=1)

            result = {
                'usage_percent': cpu_percent,
                'cores': cpu_count,
                'per_core_usage': cpu_per_core
            }

            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    result['frequency_mhz'] = cpu_freq.current
                    result['frequency_max'] = cpu_freq.max
                    result['frequency_min'] = cpu_freq.min
            except:
                pass

            return result
        except Exception as e:
            return {'error': f'Error getting CPU info: {str(e)}'}

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                'total_gb': round(memory.total / (1024 ** 3), 2),
                'available_gb': round(memory.available / (1024 ** 3), 2),
                'used_gb': round(memory.used / (1024 ** 3), 2),
                'percentage': memory.percent,
                'swap_total_gb': round(swap.total / (1024 ** 3), 2),
                'swap_used_gb': round(swap.used / (1024 ** 3), 2),
                'swap_percentage': round((swap.used / swap.total * 100) if swap.total > 0 else 0, 1)
            }
        except Exception as e:
            return {'error': f'Error getting memory info: {str(e)}'}

    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            disks = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total_gb': round(usage.total / (1024 ** 3), 2),
                        'used_gb': round(usage.used / (1024 ** 3), 2),
                        'free_gb': round(usage.free / (1024 ** 3), 2),
                        'percentage': round((usage.used / usage.total) * 100, 1)
                    }
                except (PermissionError, OSError):
                    continue
            return disks
        except Exception as e:
            return {'error': f'Error getting disk info: {str(e)}'}

    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_received': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_received': net_io.packets_recv,
                'mb_sent': round(net_io.bytes_sent / (1024 ** 2), 2),
                'mb_received': round(net_io.bytes_recv / (1024 ** 2), 2)
            }
        except Exception as e:
            return {'error': f'Error getting network info: {str(e)}'}

    def get_processes_info(self, limit: int = 10) -> Dict[str, Any]:
        """Get top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)

            return {
                'top_processes': processes[:limit]
            }
        except Exception as e:
            return {'error': f'Error getting process info: {str(e)}'}

    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        try:
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'hostname': platform.node(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            return {'error': f'Error getting system info: {str(e)}'}

    def get_uptime_info(self) -> Dict[str, Any]:
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.datetime.now().timestamp() - boot_time

            return {
                'boot_time': datetime.datetime.fromtimestamp(boot_time).isoformat(),
                'uptime_seconds': uptime_seconds,
                'uptime_hours': round(uptime_seconds / 3600, 1),
                'uptime_days': round(uptime_seconds / 86400, 1)
            }
        except Exception as e:
            return {'error': f'Error getting uptime info: {str(e)}'}

    def get_temperature_info(self) -> Dict[str, Any]:
        """Get temperature information"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                temp_data = {}
                for name, entries in temps.items():
                    temp_data[name] = [{'current': entry.current, 'high': entry.high, 'critical': entry.critical} for
                                       entry in entries]
                return temp_data
            else:
                return {'message': 'Temperature sensors not available'}
        except Exception as e:
            return {'error': f'Error getting temperature info: {str(e)}'}
