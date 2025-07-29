"""Main module."""
"""
Main module for UAVLink simulation management.

This module provides functionality to manage NS-3 UAV simulations, including process
control and inter-process communication.
"""

import os
import subprocess
import psutil
import time
import signal
from typing import Dict, Optional, Tuple, Any, Union

# Constants
EARLY_TERMINATION_CHECK_DELAY = 0.5  # Time to wait for confirming subprocess startup

def format_simulation_params(setting_map: Dict[str, Any]) -> str:
    """
    Convert simulation settings to command line arguments string.

    Args:
        setting_map: Dictionary containing simulation parameters.

    Returns:
        Formatted command line arguments string.
    """
    command_args = ''
    for key, value in setting_map.items():
        command_args += f' --{key}={value}'
    return command_args

def launch_uav_simulation(
    path: str,
    simulation_target_name: str,
    setting: Optional[Dict[str, Any]] = None,
    env: Optional[Dict[str, str]] = None,
    show_output: bool = False
) -> Tuple[str, subprocess.Popen]:
    """
    Launch a single NS-3 simulation process.

    Args:
        path: Path to NS-3 installation directory
        simulation_target_name: Name of the simulation target
        setting: Dictionary of simulation settings
        env: Environment variables for the subprocess
        show_output: Whether to show subprocess output

    Returns:
        Tuple containing the command string and subprocess object
    """
    if env is None:
        env = {}
    env.update(os.environ)
    env['LD_LIBRARY_PATH'] = os.path.abspath(os.path.join(path, 'build', 'lib'))
    exec_path = os.path.join(path, 'ns3')

    cmd = f'{exec_path} run {simulation_target_name}'
    if setting:
        cmd += format_simulation_params(setting)
    
    kwargs = {
        'shell': True,
        'text': True,
        'env': env,
        'stdin': subprocess.PIPE,
        'preexec_fn': os.setpgrp
    }
    
    if not show_output:
        kwargs.update({
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE
        })

    proc = subprocess.Popen(cmd, **kwargs)
    return cmd, proc

def terminate_process_tree(
    process: Union[int, psutil.Process, subprocess.Popen],
    timeout: Optional[float] = None,
    on_terminate: Optional[callable] = None
) -> Tuple[list, list]:
    """
    Terminate a process and all its children.

    Args:
        process: Process to terminate (can be PID, psutil.Process, or subprocess.Popen)
        timeout: Time to wait for process termination
        on_terminate: Callback function when process terminates

    Returns:
        Tuple of (terminated_processes, still_alive_processes)
    """
    print('UAVLink: Terminating subprocesses...')
    if isinstance(process, int):
        process = psutil.Process(process)
    elif not isinstance(process, psutil.Process):
        process = psutil.Process(process.pid)
    
    children = [process] + process.children(recursive=True)
    for child in children:
        try:
            child.kill()
        except Exception:
            continue
    return psutil.wait_procs(children, timeout=timeout, callback=on_terminate)

def handle_termination_signal(sig: int, frame: Any) -> None:
    """Handle SIGINT signal."""
    print("\nUAVLink: SIGINT detected. Exiting...")
    exit(1)

class UAVLinkSimulation:
    """Manages NS-3 UAV simulation processes and communication."""
    
    _created = False

    def __init__(
        self,
        simulation_target_name: str,
        ns3_path: str,
        uavlink_module: Any,
        handle_finish: bool = False,
        use_vector: bool = False,
        vector_size: Optional[int] = None,
        shared_memory_size: int = 4096,
        shared_memory_name: str = "SharedMemorySegment",
        cpp_to_py_msg_name: str = "CppToPythonMessage",
        py_to_cpp_msg_name: str = "PythonToCppMessage",
        shared_lock_name: str = "SharedLock"
    ):
        """Initialize UAVLinkSimulation instance."""
        if UAVLinkSimulation._created:
            raise Exception('UAVLinkSimulation: Error: Only one instance allowed.')
        UAVLinkSimulation._created = True

        self.simulation_target_name = simulation_target_name
        os.chdir(ns3_path)
        self.uavlink_module = uavlink_module
        self.handle_finish = handle_finish
        self.use_vector = use_vector
        self.vector_size = vector_size
        self.shared_memory_size = shared_memory_size
        self.shared_memory_name = shared_memory_name
        self.cpp_to_py_msg_name = cpp_to_py_msg_name
        self.py_to_cpp_msg_name = py_to_cpp_msg_name
        self.shared_lock_name = shared_lock_name

        self.communication_interface = uavlink_module.UavLinkMsgInterfaceImpl(
            True, self.use_vector, self.handle_finish,
            self.shared_memory_size, self.shared_memory_name,
            self.cpp_to_py_msg_name, self.py_to_cpp_msg_name,
            self.shared_lock_name
        )
         
        if self.use_vector:
            if self.vector_size is None:
                raise Exception('UAVLinkSimulation: Error: Vector mode enabled but size is unknown.')
            self.communication_interface.GetCpp2PyVector().resize(self.vector_size)
            self.communication_interface.GetPy2CppVector().resize(self.vector_size)

        self.simulation_process = None
        self.simulation_command = None
        print('UAVLinkSimulation: Initialized.')

    def __del__(self):
        """Cleanup resources when object is destroyed."""
        self.stop_simulation()
        del self.communication_interface
        print('UAVLinkSimulation: Resources cleaned up.')

    def start_simulation(
        self,
        settings: Optional[Dict[str, Any]] = None,
        show_output: bool = False
    ) -> Any:
        """Start the simulation process."""
        self.stop_simulation()
        self.simulation_command, self.simulation_process = launch_uav_simulation(
            './', self.simulation_target_name, setting=settings, show_output=show_output
        )
        print("UAVLinkSimulation: Running with command: ", self.simulation_command)
        time.sleep(EARLY_TERMINATION_CHECK_DELAY)
        
        if not self.is_simulation_running():
            print('UAVLinkSimulation: Subprocess terminated early.')
            exit(1)
            
        signal.signal(signal.SIGINT, handle_termination_signal)
        return self.communication_interface

    def stop_simulation(self) -> None:
        """Stop the current simulation process if running."""
        if self.simulation_process and self.is_simulation_running():
            terminate_process_tree(self.simulation_process)
            self.simulation_process = None
            self.simulation_command = None

    def is_simulation_running(self) -> bool:
        """Check if simulation is currently running."""
        return self.simulation_process.poll() is None