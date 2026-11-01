import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtle_action_interfaces.action import MoveToGoal


class GoalClient(Node):
    def __init__(self):
        super().__init__('goal_client')
        self._action_client = ActionClient(self, MoveToGoal, 'move_to_goal')
        self._goal_handle = None

    def send_goal(self, x, y):
        # 서버 대기 -> goal 전송 -> 응답은 add_done_callback으로 goal_response_callback에 잇는다.
        # 3초 뒤 cancel_goal이 한 번 불려서 중간 취소 경로를 확인한다.
        
        self.timer = self.create_timer(3.0,self.cancel_goal)
        self._action_client.wait_for_server()
        
        goal_msg = MoveToGoal.Goal()
        goal_msg.x = x 
        goal_msg.y = y
        
        self.send_goal_future = self._action_client.send_goal_async(goal_msg,feedback_callback = self.feedback_callback)
        self.send_goal_future.add_done_callback(self.goal_response_callback)
        

    def feedback_callback(self, feedback_msg):
        # 남은 거리 출력
        self.get_logger().info(f'{feedback_msg.feedback.distance_remaining}')

    def goal_response_callback(self, future):
        # 수락되면 취소용으로 goal_handle을 저장하고 result를 기다린다.
        goal_handle = future.result()
        if goal_handle.accepted :
            self._goal_handle = goal_handle
            goal_handle.get_result_async().add_done_callback(self.get_result_callback)
        else:    
            self.get_logger().info("False")
            return
        
    def get_result_callback(self, future):
        # 성공 여부와 소요 시간 출력
        result = future.result().result
        self.get_logger().info(f'{result.success} , {result.total_time}')

    def cancel_goal(self):
        # 중간 취소 경로 테스트용: send_goal에서 만든 타이머로 한 번만 호출된다.
        if self._goal_handle:
            self._goal_handle.cancel_goal_async()
        self.timer.cancel()



def main(args=None):
    rclpy.init(args=args)
    node = GoalClient()
    node.send_goal(1.0,1.0)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
