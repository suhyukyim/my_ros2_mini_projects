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


class WaypointNav(Node):

    def __init__(self):
        super().__init__('waypoint_nav')
        # hold a list of waypoints, subscribe to /turtle1/pose,
        # publish to /turtle1/cmd_vel, and advance to the next waypoint on arrival
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.declare_parameter('max_speed', 2.0)
        self.declare_parameter('arrival_threshold', 0.05)
        self.declare_parameter('linear_gain', 0.5)
        self.declare_parameter('angular_gain', 0.5)
        self.declare_parameter('distance_gain', 1.0)
        self.declare_parameter('timer_period', 0.1)

        self.waypoint = [(2.0, 2.0), (3.0, 2.0), (2.0, 3.0), (3.0, 3.0), (5.0, 5.0)]  # (x,y)
        self.index = 0
        self.finished = False
        self.length = len(self.waypoint)
        self.cur_x = 5.0
        self.cur_y = 5.0
        self.cur_theata = 0.0
        self.time_period = self.get_parameter('timer_period').value
        self.max_speed = self.get_parameter('max_speed').value
        self.arrival_threshold = self.get_parameter('arrival_threshold').value
        self.linear_gain = self.get_parameter('linear_gain').value
        self.angular_gain = self.get_parameter('angular_gain').value
        self.distance_gain = self.get_parameter('distance_gain').value

        self.timer = self.create_timer(self.time_period, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        live_params = (
            'max_speed', 'arrival_threshold', 'linear_gain', 'angular_gain', 'distance_gain'
        )
        for param in params:
            if param.name in live_params:
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)

    def pose_callback(self, msg):
        self.cur_x = msg.x
        self.cur_y = msg.y
        self.cur_theata = msg.theta

    def timer_callback(self):
        if not self.finished:
            # 거리 차이
            target_x, target_y = self.waypoint[self.index]
            distance = ((target_x - self.cur_x)**2 + (target_y - self.cur_y)**2)**0.5
            # 각도 차이
            target_angle = math.atan2(target_y - self.cur_y, target_x - self.cur_x)
            angle_error = target_angle - self.cur_theata
            # 각도 보정
            if angle_error > math.pi:
                angle_error -= 2 * math.pi
            elif angle_error < -math.pi:
                angle_error += 2 * math.pi
            # 이동 및 회전
            if distance >= self.arrival_threshold:
                capped_distance = min(self.distance_gain * distance, self.max_speed)
                twist = Twist()
                twist.linear.x = self.linear_gain * capped_distance
                twist.angular.z = self.angular_gain * angle_error
                self.publisher.publish(twist)
            else:
                self.index += 1
                if not self.index - self.length:  # 범위 넘었을 때
                    self.finished = True
                    twist = Twist()
                else:
                    return


def main(args=None):
    rclpy.init(args=args)
    node = WaypointNav()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
