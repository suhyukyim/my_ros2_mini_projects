# 1. MoveToGoal — 커스텀 액션 인터페이스

## 목적
turtle_action_interfaces 패키지에 정의된 `MoveToGoal.action`을 이해한다.
이 액션이 이후 goal_server(#2)/goal_client(#3)가 주고받는 메시지 타입이 된다.

## 왜 토픽/서비스가 아니라 액션인가
- **토픽**: 한쪽이 계속 보내기만 함. "완료됐다"는 개념이 없음.
- **서비스**: 요청 → 응답 한 번으로 끝남. 오래 걸리는 작업의 중간 진행상황을 알 수 없고,
  진행 중 취소도 못 함.
- **액션**: 목표(goal)를 보내고, 진행 중 계속 feedback을 받고, 끝나면 result를 받고,
  중간에 cancel도 할 수 있음. "시간이 걸리는 작업"에 맞는 유일한 표준 통신 패턴.

## MoveToGoal.action 필드
```
# Goal
float32 x
float32 y
---
# Result
bool success
float32 total_time
---
# Feedback
float32 distance_remaining
```

- **Goal** (`x`, `y`): 거북이가 도착해야 할 목표 좌표. 클라이언트가 채워서 보냄.
- **Feedback** (`distance_remaining`): 서버가 이동 도중 주기적으로 보고하는 남은 거리.
- **Result** (`success`, `total_time`): 도착 성공 여부와 걸린 시간. 서버가 종료 시 한 번 보냄.

`---`로 구분된 세 블록이 `.action` 파일 문법. `ros2 interface show
turtle_action_interfaces/action/MoveToGoal`로 언제든 확인 가능.

## 익힐 개념
- `.action` 파일은 `ament_python` 패키지에서 직접 정의할 수 없고, 별도의 `ament_cmake`
  인터페이스 패키지(`turtle_action_interfaces`)가 필요한 이유 (`rosidl_generate_interfaces`가
  코드 생성을 하는데, 이게 CMake 빌드 단계에서 일어남).
- Goal / Result / Feedback 세 블록의 역할 구분.

## 상태
완료 — `turtle_action_interfaces` 패키지는 인터페이스 정의만 담당한다.
