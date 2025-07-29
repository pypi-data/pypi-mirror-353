=================
moveit2_commander
=================


.. image:: https://img.shields.io/pypi/v/moveit2_commander.svg
        :target: https://pypi.python.org/pypi/moveit2_commander

.. image:: https://readthedocs.org/projects/moveit2-commander/badge/?version=latest
        :target: https://github.com/7cmdehdrb/moveit2_commander/blob/master/DOCUMENT.md
        :alt: Documentation Status



package for controlling moveit2 services


* Free software: MIT license
* Documentation: https://github.com/7cmdehdrb/moveit2_commander/blob/master/DOCUMENT.md


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


## Requirements

This package depends on ROS2 packages and message types:

- ROS2:
        -humble

- ROS2 Core Libraries:
        - rclpy

- ROS2 Message Types:
        - builtin_interfaces.msg.Duration
        - control_msgs.action.GripperCommand
        - geometry_msgs.msg.*
        - moveit_msgs.action.ExecuteTrajectory
        - moveit_msgs.msg.*
        - moveit_msgs.srv.*
        - nav_msgs.msg.*
        - sensor_msgs.msg.*
        - shape_msgs.msg.*
        - std_msgs.msg.*
        - trajectory_msgs.msg.*
        - visualization_msgs.msg.*