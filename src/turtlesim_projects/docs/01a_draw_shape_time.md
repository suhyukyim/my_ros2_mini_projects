# 1a. draw_shape_time — 도형 그리기 (시간 기반)

## 목적
`/turtle1/cmd_vel`에 `geometry_msgs/Twist`를 주기적으로 퍼블리시해서 원과 사각형을 그린다. 실제 위치 피드백 없이 "속도 × 시간"만으로 이동/회전량을 추정하는 dead-reckoning(추측 항법) 방식.

## 사용 토픽
- Publish: `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`)

## 익힐 개념

### 1. timer 기반 주기 실행
- `create_timer(주기_초, callback)` — 인자는 딱 두 개, 토픽/타입과 무관 (publisher/subscription과 다름)
- `rclpy.spin(node)`는 executor를 돌려서, 등록된 timer들의 "다음 실행 예정 시각"을 계속 확인하다가 시간이 되면 콜백을 호출 — `while` 루프를 직접 도는 게 아니라 이벤트 루프가 대신 깨워주는 방식
- 콜백 안의 지역 변수(`twist = Twist()`)는 호출이 끝나면 사라지므로, 호출 간에 유지되어야 하는 값(현재 모드, 누적 거리/각도 등)은 반드시 `self.xxx`(인스턴스 속성)로 저장해야 함

### 2. 원 그리기 — 상태 없이 가능
- `linear.x`, `angular.z`를 **동시에** 0이 아닌 상수로 주면 등속 원운동이 됨
- 반지름 `r = v / ω` (예: `linear.x=2.0`, `angular.z=1.0` → `r=2`)
- 매 tick마다 같은 값을 반복 publish하면 끝 — 사각형과 달리 "몇 번째 변인지" 같은 상태 추적이 불필요

### 3. 사각형 그리기 — mode 상태 머신
- `self.mode`를 `'move'` / `'turn'`으로 나눠 분기
- `move`: `linear.x`만 채워 직진, `turn`: `angular.z`만 채워 제자리 회전
- 목표 도달 판정은 **누적값**으로: `current_distance += linear.x * timer_period`, `current_angle += angular.z * timer_period` (실제 이동/회전량 = 속도 × 경과시간)
- `linear.x`/`angular.z` 값과 누적 증가량 계산에 쓰는 속도값을 반드시 같은 변수/표현식으로 일치시켜야 함 — 손으로 숫자를 따로 맞추면(예: 각속도 0.01, 증가량 0.01) 실제 물리량과 어긋나는 버그가 생김

### 4. Twist vs Pose
- `Twist`(geometry_msgs) = 우리가 **명령으로 보내는** 속도 (publish)
- `Pose`(turtlesim 자체 타입, `x`/`y`/`theta`/`linear_velocity`/`angular_velocity` flat field) = 거북이가 **보고하는 현재 상태** (subscribe) — 이번 구현에서는 사용 안 함, [draw_shape_pose](draw_shape_pose.md)에서 사용 예정

## 알려진 한계 (dead-reckoning의 근본 문제)
- `current_angle`, `current_distance`는 실제 센서 값이 아니라 "이 정도 속도로 이만큼 시간이 지났으니 이만큼 움직였을 것"이라는 **추정치**
- 부동소수점 누적 오차 + tick 단위(0.1초)로만 도달 여부를 확인하기 때문에, 목표치를 정확히 맞추지 못하고 최대 1 tick만큼 오버슈트할 수 있음 → 사각형의 네 변 길이는 비슷해도 회전각이 정확히 90도씩 쌓이지 않아 완전히 닫힌 정사각형이 안 나올 수 있음
- 근본 해결책은 실제 `/turtle1/pose`를 구독해서 진짜 theta/위치를 기준으로 판단하는 closed-loop 방식 → [draw_shape_pose](01b_draw_shape_pose.md)에서 구현

## 상태
구현 완료 — 원(상태 없음), 사각형(move/turn 상태 머신, 시간 기반 추정) 동작. 정사각형 각도 오차는 알려진 이슈로 남겨두고 pose 기반 버전에서 해결 예정.

## 실행 방법
```bash
ros2 run turtlesim turtlesim_node   # 별도 터미널
ros2 run turtlesim_projects draw_shape_time
```
