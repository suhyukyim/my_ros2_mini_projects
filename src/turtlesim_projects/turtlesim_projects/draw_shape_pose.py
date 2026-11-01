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

from math import pi

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class DrawShapePose(Node):

    def __init__(self):
        super().__init__('draw_shape_pose')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.declare_parameter('target_distance', 2.0)
        self.declare_parameter('target_angle', 1.57)
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('turn_gain', 1.5)
        self.declare_parameter('angle_tolerance', 0.005)
        self.declare_parameter('timer_period', 0.1)

        self.mode = 'move'  # 'move' or 'turn'
        self.target_distance = self.get_parameter('target_distance').value
        self.side_count = 0
        self.timer_period = self.get_parameter('timer_period').value
        self.pose_recived = False  # Flag to indicate if the pose has been received

        # latest pose, and where the current move/turn segment started
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_theta = 0.0
        self.linear_speed = self.get_parameter('linear_speed').value
        self.target_angle = self.get_parameter('target_angle').value  # 90 degrees in radians
        # proportional gain: settle time ~= ln(target_angle/tolerance) / turn_gain
        self.turn_gain = self.get_parameter('turn_gain').value
        self.angle_tolerance = self.get_parameter('angle_tolerance').value
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        live_params = (
            'target_distance', 'target_angle', 'linear_speed', 'turn_gain', 'angle_tolerance'
        )
        for param in params:
            if param.name in live_params:
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)

    def pose_callback(self, msg):
        # store the latest pose so timer_callback can read it
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta
        if not self.pose_recived:
            self.start_x = msg.x
            self.start_y = msg.y
            self.start_theta = msg.theta
            self.pose_recived = True

    def timer_callback(self):
        if not self.pose_recived:
            return  # Do nothing until the first pose message is received
        twist = Twist()
        if self.mode == 'move':
            twist.linear.x = self.linear_speed
            moved = ((self.current_x - self.start_x)**2 + (self.current_y - self.start_y)**2)**0.5
            if moved >= self.target_distance:
                self.mode = 'turn'
                self.start_theta = self.current_theta
        elif self.mode == 'turn':
            delta = self.current_theta - self.start_theta
            if delta < -pi:
                delta += 2 * pi
            elif delta > pi:
                delta -= 2 * pi
            remain = self.target_angle - abs(delta)
            if remain < self.angle_tolerance:
                remain = 0.0
            else:
                twist.angular.z = self.turn_gain * remain
            if remain == 0.0:
                self.mode = 'move'
                self.start_x = self.current_x
                self.start_y = self.current_y
                self.start_theta = self.current_theta
                # self.side_count += 1
                # if self.side_count >= 4:
                #     # Stop the turtle after completing the square
                #     twist.linear.x = 0.0
                #     twist.angular.z = 0.0
                #     self.timer.cancel()  # Stop the timer to stop moving
        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = DrawShapePose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
