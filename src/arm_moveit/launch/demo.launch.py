from launch import LaunchDescription
from launch_ros.actions import Node

from moveit_configs_utils import MoveItConfigsBuilder


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
        {"use_sim_time": True},
    ],
)
    rviz_node = Node(
    package="rviz2",
    executable="rviz2",
    output="screen",
    arguments=[
        "-d",
        str(
            moveit_config.package_path
            / "config"
            / "moveit.rviz"
        ),
    ],
    parameters=[
        moveit_config.robot_description,
        moveit_config.robot_description_semantic,
        moveit_config.robot_description_kinematics,
        moveit_config.planning_pipelines,
        moveit_config.joint_limits,
        {"use_sim_time": True},
    ],
)

    return LaunchDescription([
        move_group_node,
        rviz_node,
    ])