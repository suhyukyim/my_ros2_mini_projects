import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_action_interfaces.action import MoveToGoal
import math
import time

class GoalServer(Node):
	def __init__(self):
		super().__init__('goal_server')

		self.cb_group = ReentrantCallbackGroup()

		self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
		
		self.subscription = self.create_subscription(
			Pose,
			'/turtle1/pose',
			self.pose_callback,
			10,
			callback_group=self.cb_group
		)

		self.cur_x = 5.0
		self.cur_y = 5.0
		self.cur_theta = 0.0

		self._action_server = ActionServer(
			self,
			MoveToGoal,
			'move_to_goal',
			execute_callback=self.execute_callback,
			cancel_callback=self.cancel_callback,
			callback_group=self.cb_group,
		)

	def pose_callback(self, msg):
		self.cur_x = msg.x
		self.cur_y = msg.y
		self.cur_theta = msg.theta

	def cancel_callback(self, goal_handle):
		# 취소 요청은 항상 허용 (거절하려면 CancelResponse.REJECT)
		return CancelResponse.ACCEPT

	def execute_callback(self, goal_handle):
		# goal_handle.request.x, goal_handle.request.y가 목표 좌표.
		#
		# 목표에 도착할 때까지 P제어로 이동하면서 매 스텝 남은 거리를 feedback으로
		# 보내고, 취소 요청이 오면 canceled(), 도착하면 succeed()로 끝낸다.
		#
		# 여기서 while로 블로킹해도 되는 이유: 기본 설정(싱글스레드 executor +
		# MutuallyExclusive 콜백그룹)이었다면 이 루프가 노드 전체를 막아서
		# pose 구독도 cancel_callback도 돌지 않는다. 그래서 main()을
		# MultiThreadedExecutor로 돌리고 구독과 ActionServer에 같은
		# ReentrantCallbackGroup을 물려, 루프 중에도 두 콜백이 계속 돌게 했다.
		# 대신 루프 주기는 직접 제어한다 (time.sleep). Nav2 액션 서버도 같은 패턴.
		x,y = goal_handle.request.x , goal_handle.request.y
		self.get_logger().info(f'goal = ({x} , {y})')
		self.get_logger().info(f'cur = ({self.cur_x} , {self.cur_y})')
		
		start_time = self.get_clock().now()  
		
		while True:
			if goal_handle.is_cancel_requested:
				self.get_logger().warn('goal canceled')  
				self.publisher.publish(Twist()) 
				goal_handle.canceled()
				elapsed =(self.get_clock().now() - start_time).nanoseconds/ 1e9
				return MoveToGoal.Result(success = False , total_time = elapsed)
			
			distance = ((x - self.cur_x)**2 + (y - self.cur_y)**2)**0.5
			target_angle = math.atan2(y - self.cur_y, x - self.cur_x)
			angle_error = target_angle - self.cur_theta
			if angle_error > math.pi:
				angle_error -= 2 * math.pi
			elif angle_error < -math.pi:
				angle_error += 2 * math.pi
			
			if distance < 0.1 :
				break

			twist = Twist()
			twist.linear.x = 1.5 * distance
			twist.angular.z = 4.0 * angle_error
			self.publisher.publish(twist)

			feedback = MoveToGoal.Feedback()
			feedback.distance_remaining = distance
			goal_handle.publish_feedback(feedback)
			
			time.sleep(0.1)

		self.publisher.publish(Twist())
		goal_handle.succeed()
		self.get_logger().info('goal reached')      # ← 추가
		elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
		return MoveToGoal.Result(success = True , total_time = elapsed)
	
def main(args=None):
	rclpy.init(args=args)
	node = GoalServer()
	executor = MultiThreadedExecutor()
	rclpy.spin(node, executor=executor)
	node.destroy_node()
	rclpy.shutdown()


if __name__ == '__main__':
	main()
