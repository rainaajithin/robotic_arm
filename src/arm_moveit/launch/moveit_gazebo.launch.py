from launch import LaunchDescription
from launch_ros.actions import Node

from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    moveit_config = (
        MoveItConfigsBuilder(
            "arm",
            package_name="arm_moveit"
        )
        .joint_limits(
            file_path="config/joint_limits.yaml"
        )
        .trajectory_execution(
            file_path="config/moveit_controllers.yaml",
            moveit_manage_controllers=False,
        )
        .to_moveit_configs()
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
        ],
        arguments=[
            "--ros-args",
            "-p",
            "use_sim_time:=true",
        ],
    )

    rviz_config = os.path.join(
        get_package_share_directory("arm_moveit"),
        "config",
        "moveit.rviz"
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=[
            "-d",
            rviz_config,
        ],
        parameters=[
            {
                "use_sim_time": True,
            },
        ],
    )

    return LaunchDescription([
        move_group_node,
        rviz_node,
    ])