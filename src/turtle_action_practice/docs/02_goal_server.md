# 2. goal_server.py — 액션 서버

## 목적
`MoveToGoal` 액션의 서버 역할. 클라이언트가 보낸 목표 좌표로 turtle1을 이동시키고,
이동 중 남은 거리를 feedback으로 보고하며, 취소 요청도 처리한다.

## 익힐 개념
- `ActionServer(node, action_type, action_name, execute_callback, cancel_callback)` 로
  액션 서버를 등록하는 방법.
- `execute_callback`이라고 저절로 블로킹이 안전해지는 게 아니라는 점. 기본값
  (`rclpy.spin(node)` = 싱글스레드 executor + 기본 MutuallyExclusive 콜백그룹)에서
  콜백 안에 `while`을 넣으면 노드 전체가 멈춘다 — pose 구독도, 취소 처리도 안 돈다.
  waypoint_nav.py의 "타이머 콜백에 while 넣으면 안 된다"와 같은 얘기.
- 그래서 이 파일의 `main()`은 `MultiThreadedExecutor`로 스핀하고, 구독과 `ActionServer`에
  같은 `ReentrantCallbackGroup`을 물려놨다. 이 조합 **덕분에** `execute_callback` 안에서
  블로킹 루프를 돌려도 pose 구독과 취소 확인이 동시에 계속 돌아간다. Nav2 같은 실제
  액션 서버들이 쓰는 executor 패턴이 바로 이것.
- `goal_handle.publish_feedback(...)`으로 진행 중 상태를 클라이언트에 계속 보고.
- `goal_handle.is_cancel_requested` 확인 → `goal_handle.canceled()` → `Result(success=False, ...)`
  반환하는 취소 처리 흐름.
- `goal_handle.succeed()` → `Result(success=True, ...)` 반환하는 정상 종료 흐름.

## 의미
서비스(`turtle_service_control.py`)까지는 "요청 한 번, 응답 한 번"이었는데, 액션은
그 사이에 진행상황(feedback)과 취소 가능성이 추가된 구조. Nav2 같은 실제 자율주행
스택이 전부 이 패턴 위에 세워져 있다.

## 상태
구현 완료 — P 제어로 목표까지 이동하며 남은 거리 feedback 발행, 취소 요청 처리, 도착 시 성공 여부와
소요 시간 반환. `MultiThreadedExecutor` + `ReentrantCallbackGroup`으로 실행 중에도 pose 구독과 취소가 동작한다.

## 실행 방법
```bash
colcon build --packages-select turtle_action_practice
source install/setup.bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtle_action_practice goal_server
```
확인: 다른 터미널에서 `ros2 action list`에 `/move_to_goal`이 뜨는지,
`ros2 action info /move_to_goal -t`로 타입이 `turtle_action_interfaces/action/MoveToGoal`인지 확인.
