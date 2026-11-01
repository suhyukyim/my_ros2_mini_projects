# 3. turtle_chase — 거북이 추격

## 목적
거북이 2마리(`turtle1`, `turtle2`)를 스폰하고, `turtle2`가 `turtle1`의 위치를 구독해 쫓아가도록 제어한다.

## 사용 토픽/서비스
- Service client: `/spawn` (`turtlesim/srv/Spawn`) — turtle2 생성
- Subscribe: `/turtle1/pose`, `/turtle2/pose` (`turtlesim/msg/Pose`)
- Publish: `/turtle2/cmd_vel` (`geometry_msgs/msg/Twist`)

## 익힐 개념
- 서브스크라이버 콜백에서 상태(pose) 저장
- 서비스 클라이언트로 거북이 스폰
- 두 좌표 사이 거리/각도 계산 → 간단한 P 제어(비례 제어)로 추격

## 상태
구현 완료 — `/spawn`으로 turtle2 생성, 두 거북이 pose 구독, 거리/각도 오차 기반 P 제어로 추격

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects turtle_chase
```
