# turtlesim_projects

ROS2(Jazzy) turtlesim으로 하나씩 익혀가는 미니 프로젝트 모음. `ament_python` 빌드 타입 패키지.

## 프로젝트 목록

난이도 순으로 진행 추천.

| # | 파일 | 주제 | 문서 |
|---|------|------|------|
| 1a | `draw_shape_time.py` | 도형 그리기 (타이머 입문, 시간 기반 추정) | [docs/01a_draw_shape_time.md](docs/01a_draw_shape_time.md) |
| 1b | `draw_shape_pose.py` | 도형 그리기 (pose 실측 기반) | [docs/01b_draw_shape_pose.md](docs/01b_draw_shape_pose.md) |
| 2 | `custom_teleop.py` | 키보드 원격 조종 | [docs/02_custom_teleop.md](docs/02_custom_teleop.md) |
| 3 | `turtle_chase.py` | 거북이 추격 (서브스크라이버 + 제어) | [docs/03_turtle_chase.md](docs/03_turtle_chase.md) |
| 4 | `turtle_service_control.py` | 서비스 활용 (spawn/kill/set_pen/reset) | [docs/04_turtle_service_control.md](docs/04_turtle_service_control.md) |
| 5 | `waypoint_nav.py` | 경로 추종 (waypoint navigation) | [docs/05_waypoint_nav.md](docs/05_waypoint_nav.md) |
| 6 | `obstacle_avoid.py` | 장애물 회피 추격 (potential field) | [docs/06_obstacle_avoid.md](docs/06_obstacle_avoid.md) |
| 7 | `game_referee.py` | 잡기 판정 / 점수 / 리스폰 | [docs/07_game_referee.md](docs/07_game_referee.md) |
| 8 | `launch/game.launch.py` | 게임 한 번에 실행 (launch 파일) | [docs/08_game_launch.md](docs/08_game_launch.md) |

1~8 모두 구현 완료 (Phase B, 멀티 거북이 게임 캡스톤 완결). `custom_teleop`은 launch로 띄운 4번 `custom_teleop.py`와 별개로, `game.launch.py` 실행 시엔 표준입력 문제로 launch에 포함되지 않으므로 별도 터미널에서 `ros2 run turtlesim_projects custom_teleop`로 직접 실행 필요.

## 빌드 & 실행

```bash
# 워크스페이스 루트에서
cd ~/ros2/ros2_portfolio/mini_project
colcon build --packages-select turtlesim_projects
source install/setup.bash

# turtlesim 실행 (별도 터미널)
ros2 run turtlesim turtlesim_node

# 만든 노드 실행
ros2 run turtlesim_projects draw_shape_time
```

## Q&A / 진행 노트

### package.xml, setup.py는 어떻게 만드나?

이 패키지의 `package.xml`/`setup.py`/`setup.cfg`/`resource/`는 처음엔 직접 손으로 작성했지만, 원래 표준 방법은 `ros2 pkg create` 명령어를 쓰는 것.

```bash
cd ~/ros2/ros2_portfolio/mini_project/src
ros2 pkg create --build-type ament_python turtlesim_projects \
  --dependencies rclpy turtlesim geometry_msgs
```

이 명령이 자동으로 만들어주는 것:
- `package.xml`, `setup.py`, `setup.cfg` (dependencies도 package.xml에 자동 반영)
- `resource/turtlesim_projects`
- `turtlesim_projects/__init__.py` 포함한 패키지 폴더
- 예제 노드 실행 진입점

단, `setup.py`의 `entry_points`에 노드 5개를 등록하는 건 자동으로 안 해주므로 어차피 수동으로 추가해야 하는 부분.

(참고: `mkdir -p`는 별개로, 중첩 디렉토리를 한 번에 만드는 옵션이고 `ros2 pkg create`와는 무관함.)
