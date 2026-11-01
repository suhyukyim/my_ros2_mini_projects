# 3. goal_client.py — 액션 클라이언트

## 목적
`MoveToGoal` 액션의 클라이언트 역할. 목표 좌표를 서버로 보내고, feedback을 구독하고,
결과를 기다리고, 필요하면 중간에 취소한다.

## 익힐 개념
- `ActionClient(node, action_type, action_name)`로 클라이언트를 만드는 방법.
- `send_goal_async(goal_msg, feedback_callback=...)` — 서비스의 `call_async`와 같은
  자리지만, feedback 콜백을 함께 등록한다는 점이 다르다.
- goal 전송 → 수락/거절 응답(`goal_response_callback`) → 결과 대기(`get_result_callback`)로
  이어지는 3단계 콜백 체이닝. game_referee.py의 `do_kill` → `on_kill_done` 패턴과
  구조적으로 동일 (블로킹 대신 `add_done_callback`으로 다음 단계 잇기).
- `goal_handle.cancel_goal_async()`로 진행 중인 goal을 취소하는 방법.

## 의미
서버 쪽에서 배운 걸 클라이언트 쪽에서 대칭적으로 확인하는 노드. 서버의 feedback
publish -> 클라이언트의 feedback_callback, 서버의 succeed()/canceled() -> 클라이언트의
result.success 로 이어지는 왕복을 직접 눈으로 확인하는 게 목표.

## 상태
구현 완료 — goal 전송 → 수락 확인 → result 수신을 future 콜백 체인으로 처리하고, feedback(남은 거리)을 출력.
goal 전송 3초 뒤 `cancel_goal`이 호출돼 취소 경로까지 확인한다.

## 실행 방법
```bash
colcon build --packages-select turtle_action_practice
source install/setup.bash
# turtlesim_node + goal_server가 이미 떠 있는 상태에서
ros2 run turtle_action_practice goal_client
```
확인: goal_server 터미널과 goal_client 터미널 양쪽에 feedback/result 로그가 찍히고,
거북이가 실제로 목표 좌표로 이동하는지 확인. cancel_goal도 별도로 테스트해볼 것.
