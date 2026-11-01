# Copyright 2026 suhyuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Spawn


class TurtleChase(Node):

    def __init__(self):
        super().__init__('turtle_chase')
        # spawn turtle2, subscribe to /turtle1/pose and /turtle2/pose,
        # and publish to /turtle2/cmd_vel to chase turtle1
        self.publisher_2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        spawn_client = self.create_client(Spawn, '/spawn')
        while not spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')
        request = Spawn.Request()
        request.x = 0.0
        request.y = 0.0
        request.theta = 0.0
        request.name = 'turtle2'
        future = spawn_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        self.get_logger().info(f'Spawned: {response.name}')

        # s
        # subcribe
        self.subscription_1 = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback_1,
            10
        )
        self.subscription_2 = self.create_subscription(
            Pose,
            '/turtle2/pose',
            self.pose_callback_2,
            10
        )

        self.declare_parameter('linear_gain', 1.0)
        self.declare_parameter('angular_gain', 1.0)
        self.declare_parameter('timer_period', 0.1)
        self.linear_gain = self.get_parameter('linear_gain').value
        self.angular_gain = self.get_parameter('angular_gain').value

        # value init
        self.turtle1_x = 0.0
        self.turtle1_y = 0.0
        self.turtle1_theta = 0.0
        self.turtle2_x = 0.0
        self.turtle2_y = 0.0
        self.turtle2_theta = 0.0
        self.turtle1_received = False  # True once /turtle1/pose has a real message
        self.turtle2_received = False  # True once /turtle2/pose has a real message
        self.timer_period = self.get_parameter('timer_period').value  # seconds

        # timer
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            if param.name in ('linear_gain', 'angular_gain'):
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)

    # callback
    def pose_callback_1(self, msg):
        self.turtle1_x = msg.x
        self.turtle1_y = msg.y
        self.turtle1_theta = msg.theta
        self.turtle1_received = True

    def pose_callback_2(self, msg):
        self.turtle2_x = msg.x
        self.turtle2_y = msg.y
        self.turtle2_theta = msg.theta
        self.turtle2_received = True

    def timer_callback(self):
        if not (self.turtle1_received and self.turtle2_received):
            return  # Skip this tick until both turtles have reported a real pose
        # 거리오차
        dx = self.turtle1_x - self.turtle2_x
        dy = self.turtle1_y - self.turtle2_y
        distance = (dx**2 + dy**2)**0.5
        # 목표 각도
        target_angle = math.atan2(self.turtle1_y - self.turtle2_y, self.turtle1_x - self.turtle2_x)
        # 각도오차
        angle_error = target_angle - self.turtle2_theta
        if angle_error > math.pi:
            angle_error -= 2 * math.pi
        elif angle_error < -math.pi:
            angle_error += 2 * math.pi
        # 속도 제어
        twist = Twist()
        twist.linear.x = self.linear_gain * distance
        twist.angular.z = self.angular_gain * angle_error
        self.publisher_2.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleChase()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
