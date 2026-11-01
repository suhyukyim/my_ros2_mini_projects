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


class ObstacleAvoid(Node):

    def __init__(self):
        super().__init__('obstacle_avoid')
        # turtle2(추격자)를 스폰해서 turtle1을 쫓게 하고,
        # turtle3를 고정 위치의 "장애물"로 하나 더 스폰한다.
        self.publisher_2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        spawn_client = self.create_client(Spawn, '/spawn')
        while not spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        self.declare_parameter('chaser_start_x', 0.0)
        self.declare_parameter('chaser_start_y', 0.0)
        self.declare_parameter('obstacle_x', 2.0)
        self.declare_parameter('obstacle_y', 2.0)
        self.declare_parameter('obstacle_radius', 2.0)
        self.declare_parameter('linear_gain', 1.0)
        self.declare_parameter('angular_gain', 1.0)
        self.declare_parameter('timer_period', 0.1)

        chaser_start_x = self.get_parameter('chaser_start_x').value
        chaser_start_y = self.get_parameter('chaser_start_y').value
        obstacle_x = self.get_parameter('obstacle_x').value
        obstacle_y = self.get_parameter('obstacle_y').value

        self.request2 = self.spawn_turtle('turtle2', chaser_start_x, chaser_start_y)
        self.request3 = self.spawn_turtle('turtle3', obstacle_x, obstacle_y)
        move_to_target = spawn_client.call_async(self.request2)
        avoid_to_obstacle = spawn_client.call_async(self.request3)
        rclpy.spin_until_future_complete(self, move_to_target)
        rclpy.spin_until_future_complete(self, avoid_to_obstacle)
        self.get_logger().info(f'Spawned: {move_to_target.result().name}')
        self.get_logger().info(f'Spawned: {avoid_to_obstacle.result().name}')

        # subscription_1: turtle1/pose (추격 대상), subscription_2: turtle2/pose (내 위치).
        # 장애물(turtle3)은 위치가 고정이라 구독하지 않고 스폰 좌표를 그대로 쓴다.
        self.subscription_1 = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback_1,
            10
        )

        self.subscription_2 = self.create_subscription(
            Pose,
            'turtle2/pose',
            self.pose_callback_2,
            10
        )

        # value init (turtle_chase.py 참고, 필요한 대로 수정)
        self.turtle1_x = 0.0
        self.turtle1_y = 0.0
        self.turtle2_x = 0.0
        self.turtle2_y = 0.0
        self.turtle2_theta = 0.0
        self.obstacle_x = self.request3.x
        self.obstacle_y = self.request3.y
        self.obstacle_radius = self.get_parameter('obstacle_radius').value  # 반경 안이면 반발력 작동
        self.linear_gain = self.get_parameter('linear_gain').value
        self.angular_gain = self.get_parameter('angular_gain').value

        self.timer_period = self.get_parameter('timer_period').value
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            if param.name in ('obstacle_radius', 'linear_gain', 'angular_gain'):
                setattr(self, param.name, param.value)
        return SetParametersResult(successful=True)

    def spawn_turtle(self, name, x, y, theta=0.0):
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.name = name
        request.theta = float(theta)
        return request

    def pose_callback_1(self, msg):
        self.turtle1_x = msg.x
        self.turtle1_y = msg.y
        self.turtle1_theta = msg.theta

    def pose_callback_2(self, msg):
        self.turtle2_x = msg.x
        self.turtle2_y = msg.y
        self.turtle2_theta = msg.theta

    def timer_callback(self):
        # 목표까지의 벡터
        dx_t = self.turtle1_x - self.turtle2_x
        dy_t = self.turtle1_y - self.turtle2_y
        # 목표까지의 거리
        distance = (dx_t**2 + dy_t**2)**0.5
        # 장애물까지 거리
        dx_obs = self.turtle2_x - self.obstacle_x
        dy_obs = self.turtle2_y - self.obstacle_y
        distance_obstacle = (dx_obs**2 + dy_obs**2)**0.5

        # radius 영역 밖일 때만 유닛 역벡터 만들어서 다가올 수록 더 밀어내기 위함, 아니면 그냥 (0,0) 설정
        if distance_obstacle < self.obstacle_radius:
            dx_o = self.turtle2_x - self.obstacle_x
            dy_o = self.turtle2_y - self.obstacle_y
            weight = distance_obstacle * (self.obstacle_radius - distance_obstacle)
            dx_o *= weight
            dy_o *= weight
        else:
            (dx_o, dy_o) = (0.0, 0.0)

        # 합성 벡터
        (dx_final, dy_final) = (dx_t + dx_o, dy_t + dy_o)

        # 목표 각도
        target_angle = math.atan2(dy_final, dx_final)

        # 목표 각도 오차
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
    node = ObstacleAvoid()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
