# turtle_action_practice

ROS2(Jazzy) 액션(action) 통신 패턴을 turtlesim으로 익히는 미니 프로젝트.
`turtlesim_projects`와 별개의 프로젝트 — 토픽/서비스는 거기서 익혔고, 여기선 액션만 다룬다.

두 개 패키지로 구성:
- `turtle_action_interfaces` (`ament_cmake`) — 커스텀 액션 타입 `MoveToGoal` 정의만 담당.
- `turtle_action_practice` (`ament_python`) — 실제 액션 서버/클라이언트 노드.

## 프로젝트 목록

| # | 파일 | 주제 | 문서 |
|---|------|------|------|
| 1 | `turtle_action_interfaces/action/MoveToGoal.action` | 커스텀 액션 인터페이스 | [docs/01_action_interface.md](docs/01_action_interface.md) |
| 2 | `turtle_action_practice/goal_server.py` | 액션 서버 (목표 이동 + feedback + cancel) | [docs/02_goal_server.md](docs/02_goal_server.md) |
| 3 | `turtle_action_practice/goal_client.py` | 액션 클라이언트 (goal 전송 + result 대기) | [docs/03_goal_client.md](docs/03_goal_client.md) |

1~3 모두 구현 완료. 서버는 `MultiThreadedExecutor` + `ReentrantCallbackGroup`으로 액션 실행 중에도
pose 구독과 취소 콜백이 돌도록 구성했고, 클라이언트는 goal 전송 3초 뒤 취소 요청을 보내 cancel 경로까지 확인한다.

## 빌드 & 실행

```bash
# 워크스페이스 루트에서
cd ~/ros2/ros2_portfolio/mini_project
colcon build --packages-select turtle_action_interfaces turtle_action_practice
source install/setup.bash

# turtlesim 실행 (터미널 1)
ros2 run turtlesim turtlesim_node

# 액션 서버 실행 (터미널 2)
ros2 run turtle_action_practice goal_server

# 액션 클라이언트 실행 (터미널 3)
ros2 run turtle_action_practice goal_client
```

## Q&A / 진행 노트

자세한 개념 정리는 [NOTES.md](NOTES.md) 참고.
