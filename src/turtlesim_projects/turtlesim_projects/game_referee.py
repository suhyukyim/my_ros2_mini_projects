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

import random

from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from turtlesim.msg import Pose
from turtlesim.srv import Kill, Spawn


class GameReferee(Node):

    def __init__(self):
        super().__init__('game_referee')
        # turtle1(도망자/플레이어), turtle2(추격자) pose 구독 + /kill, /spawn 서비스 클라이언트
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

        self.kill_client = self.create_client(Kill, '/kill')
        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /kill service...')

        # spawn
        self.spawn_client = self.create_client(Spawn, '/spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        # 점수를 알리는 퍼블리셔
        self.score_publisher = self.create_publisher(Int32, '/game/score', 10)

        self.declare_parameter('catch_radius', 0.5)
        self.declare_parameter('timer_period', 0.1)

        self.turtle1_x = 0.0
        self.turtle1_y = 0.0
        self.turtle2_x = 0.0
        self.turtle2_y = 0.0
        self.catch_radius = self.get_parameter('catch_radius').value  # 이 거리 이하면 "잡힘"
        self.score = 0
        self.turtle2_ready = False

        self.timer_period = self.get_parameter('timer_period').value
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'catch_radius':
                self.catch_radius = param.value
        return SetParametersResult(successful=True)

    def pose_callback_1(self, msg):
        self.turtle1_x = msg.x
        self.turtle1_y = msg.y

    def pose_callback_2(self, msg):
        self.turtle2_ready = True
        self.turtle2_x = msg.x
        self.turtle2_y = msg.y

    def timer_callback(self):
        # 거리 계산
        dx = self.turtle1_x - self.turtle2_x
        dy = self.turtle1_y - self.turtle2_y
        distance = (dx**2 + dy**2)**0.5

        # catch_radius 이하로 가까워지면 "잡힘" 처리 -> kill -> spawn
        if distance <= self.catch_radius:
            if not self.turtle2_ready:
                return
            score = Int32()
            self.score += 1
            score.data = self.score
            self.score_publisher.publish(score)
            self.do_kill('turtle1')

    def do_spawn(self, x, y, theta, name):
        spawn_request = Spawn.Request()
        spawn_request.x = x
        spawn_request.y = y
        spawn_request.theta = theta
        spawn_request.name = name
        self.spawn_client.call_async(spawn_request)

    def do_kill(self, name):
        kill_request = Kill.Request()
        kill_request.name = name
        future = self.kill_client.call_async(kill_request)
        future.add_done_callback(self.on_kill_done)

    def on_kill_done(self, future):
        self.get_logger().info(f'kill done: {future.result()}')
        # 여기서 kill이 끝났으니, 다음 할 일(spawn)을 이어서 호출
        self.do_spawn(float(random.randint(1, 10)), float(random.randint(1, 10)), 0.0, 'turtle1')


def main(args=None):
    rclpy.init(args=args)
    node = GameReferee()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
