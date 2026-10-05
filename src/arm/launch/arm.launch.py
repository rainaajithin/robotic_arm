from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    arm_pkg = FindPackageShare('arm')

    # ---------------------------------------------------------
    # Robot description
    # ---------------------------------------------------------
    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'),
            ' ',
            PathJoinSubstitution([
                arm_pkg,
                'urdf',
                'arm.urdf.xacro'
            ])
        ]),
        value_type=str
    )

    # ---------------------------------------------------------
    # Robot State Publisher
    # ---------------------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description,
                'use_sim_time': True
            }
        ]
    )

    # ---------------------------------------------------------
    # Gazebo
    # ---------------------------------------------------------
    gazebo = ExecuteProcess(
        cmd=[
            'gz',
            'sim',
            '-r',
            'empty.sdf'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Spawn robot into Gazebo
    # ---------------------------------------------------------
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic',
            'robot_description',
            '-name',
            'arm'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Joint State Broadcaster
    # ---------------------------------------------------------
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Arm Controller
    # ---------------------------------------------------------
    arm_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'arm_controller',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # Gripper Controller
    # ---------------------------------------------------------
    gripper_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'gripper_controller',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    clock_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
    ],
    output='screen'
)

    # ---------------------------------------------------------
    # Launch sequence
    # ---------------------------------------------------------
    return LaunchDescription([

        # Start Gazebo
        gazebo,
        clock_bridge,
        # Start robot_state_publisher
        robot_state_publisher,


        # Wait for Gazebo + robot_description, then spawn robot
        TimerAction(
            period=5.0,
            actions=[
                spawn_robot
            ]
        ),

        # Wait for robot and ros2_control to initialize
        TimerAction(
            period=8.0,
            actions=[
                joint_state_broadcaster
            ]
        ),

        # Start arm controller after broadcaster
        TimerAction(
            period=10.0,
            actions=[
                arm_controller
            ]
        ),

        # Start gripper controller
        TimerAction(
            period=12.0,
            actions=[
                gripper_controller
            ]
        ),
    ])