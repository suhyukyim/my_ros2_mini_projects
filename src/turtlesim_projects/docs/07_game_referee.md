# 7. game_referee — 잡기 판정 / 점수 / 리스폰

## 목적
`turtle1`(도망자/플레이어)과 `turtle2`(추격자, obstacle_avoid)의 pose를 동시에 구독해
거리가 임계값 이하로 가까워지면 "잡힘"으로 판정한다. 점수를 집계해 토픽으로 알리고,
잡히면 kill/spawn 서비스를 호출해 도망자를 새 위치로 재배치한다.

## 사용 토픽/서비스
- Subscribe: `/turtle1/pose`, `/turtle2/pose` (`turtlesim/msg/Pose`)
- Publish: `/game/score` (`std_msgs/msg/Int32`)
- Service client: `/kill`, `/spawn` (`turtlesim/srv/Kill`, `turtlesim/srv/Spawn`)

## 익힐 개념
- 다중 토픽 구독 관리 (turtle_chase.py 패턴 재사용)
- 게임 상태(점수)를 별도 토픽으로 publish
- 서비스 클라이언트를 "판정 결과에 따른 액션"으로 실제 호출 (turtle_service_control.py 패턴 재사용)
- 랜덤 재배치 (respawn)

## 상태
구현 완료 — 두 거북이 pose 구독, `catch_radius` 이하 잡힘 판정, `/game/score` 점수 publish, kill → spawn 재배치

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects turtle_chase   # 또는 obstacle_avoid, turtle2 스폰용
ros2 run turtlesim_projects game_referee
```
