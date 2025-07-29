#!/usr/bin/env python

"""Tests for `pyuavlink` package."""

import os
import unittest
from unittest.mock import MagicMock, patch

from pyuavlink import pyuavlink


class TestPyuavlink(unittest.TestCase):
    """Tests for `pyuavlink` package."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_module = MagicMock()
        self.mock_interface = MagicMock()
        self.mock_module.Ns3AiMsgInterfaceImpl.return_value = self.mock_interface

    def test_format_simulation_params(self):
        """Test simulation parameter formatting."""
        params = {
            'param1': 'value1',
            'param2': 'value2'
        }
        result = pyuavlink.format_simulation_params(params)
        self.assertEqual(result, ' --param1=value1 --param2=value2')

    @patch('subprocess.Popen')
    def test_launch_uav_simulation(self, mock_popen):
        """Test simulation launch."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        cmd, proc = pyuavlink.launch_uav_simulation(
            '/path/to/ns3',
            'test-sim',
            {'param': 'value'},
            show_output=True
        )

        self.assertIn('test-sim', cmd)
        self.assertIn('--param=value', cmd)
        self.assertEqual(proc, mock_process)

    def test_simulation_class(self):
        """Test UAVLinkSimulation class."""
        sim = pyuavlink.UAVLinkSimulation(
            simulation_target_name='test-sim',
            ns3_path='/path/to/ns3',
            uavlink_module=self.mock_module
        )

        self.assertEqual(sim.simulation_target_name, 'test-sim')
        self.assertIsNone(sim.simulation_process)
        self.mock_module.Ns3AiMsgInterfaceImpl.assert_called_once()

if __name__ == '__main__':
    unittest.main()
