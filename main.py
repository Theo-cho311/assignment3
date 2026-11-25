import json
import time

# 허용오차(epsilon) 기준: 부동소수점 미세 오차 보정용
EPSILON = 1e-9

# 표준 라벨 정규화 맵 (새 라벨 추가 시 이 매핑 테이블에 키-표준라벨 쌍을 추가)
LABEL_MAP = {
    "+": "Cross",
    "cross": "Cross",
    "Cross": "Cross",
    "x": "X",
    "X": "X",
}


def mac_operation(pattern, filt):
    """
    MAC(Multiply-Accumulate) 연산 함수
    - 해석 기준: 반환되는 MAC 점수가 높을수록(더 큰 값일수록) 입력 패턴과 필터의 형태가 더 유사함(일치성이 높음)을 의미합니다.
    - 근거: 같은 위치의 원소끼리 곱할 때 두 배열이 모두 활성(1)인 일치 위치에서만 1*1=1이 누적되고,
      불일치 위치(1*0, 0*1, 0*0)는 0이 되어 점수에 기여하지 않으므로 겹치는 칸이 많을수록 점수가 커집니다.
    """
    n = len(pattern)
    total = 0.0
    for r in range(n):
        for c in range(n):
            total += pattern[r][c] * filt[r][c]
    return total


def compare_scores(score_a, score_b, label_a, label_b):
    """
    허용오차(epsilon) 기반 두 필터의 MAC 점수 비교 함수
    - MAC 점수는 높을수록 유사도가 높으므로, 더 큰 점수를 가진 필터의 라벨을 반환합니다.
    - 두 점수의 차이가 EPSILON(1e-9) 미만이면 동점('UNDECIDED')으로 판정합니다.
    """
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    elif score_a > score_b:
        return label_a
    else:
        return label_b


def input_matrix_3x3(title):
    print(title)
    matrix = []
    for r in range(3):
        while True:
            line = input("숫자 3개 입력: ")
            parts = line.split()
            if len(parts) != 3:
                print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
            else:
                try:
                    row = [float(parts[0]), float(parts[1]), float(parts[2])]
                    matrix.append(row)
                    break
                except ValueError:
                    print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
    return matrix


def normalize_label(label):
    """라벨 정규화 함수: LABEL_MAP을 통해 원시 라벨('+', 'cross', 'x' 등)을 표준 라벨('Cross', 'X')로 변환"""
    if label in LABEL_MAP:
        return LABEL_MAP[label]
    return label


def measure_performance(sizes):
    print("\n=== 성능 분석 (10회 반복 평균) ===")
    print("크기(NxN) | 평균 시간(ms) | 연산 횟수(N^2)")
    print("------------------------------------------")
    for n in sizes:
        grid = [[1.0] * n for r in range(n)]
        start = time.perf_counter()
        for i in range(10):
            mac_operation(grid, grid)
        end = time.perf_counter()
        avg_ms = (end - start) * 1000 / 10
        print(f"{n}x{n} | {avg_ms:.6f} ms | {n * n}")


def run_mode_1():
    filter_a = input_matrix_3x3("필터 A (3x3)")
    filter_b = input_matrix_3x3("필터 B (3x3)")
    print("필터 A, B 저장 완료!")
    pattern = input_matrix_3x3("패턴 (3x3)")

    start = time.perf_counter()
    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000

    result = compare_scores(score_a, score_b, "A", "B")

    print("\n=== 모드 1 판정 결과 (MAC 점수가 높을수록 유사함) ===")
    print("필터 A 점수:", score_a)
    print("필터 B 점수:", score_b)
    print(f"연산 시간: {elapsed_ms:.6f} ms")
    print("판정 결과:", result)
    if result == "UNDECIDED":
        print("[모드 1 동점 안내] 두 필터의 MAC 점수가 동일(차이 < 1e-9)하여 판정 불가(UNDECIDED)입니다. 변별력 있는 필터나 패턴으로 다시 실행해 재입력해 주세요.")
    else:
        print(f"[점수 해석] 필터 {result}의 MAC 점수가 더 높으므로 입력 패턴은 필터 {result}와 더 유사합니다.")

    measure_performance([3])


def run_mode_2():
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    total_count = 0
    pass_count = 0
    fail_list = []

    print("\n=== data.json 일괄 판정 (MAC 점수가 높을수록 해당 필터와 유사) ===")
    for key in data["patterns"]:
        total_count += 1
        parts = key.split("_")
        if len(parts) < 2:
            print(key, "-> FAIL (사유: 키 형식 오류)")
            fail_list.append(key + ": 키 형식 오류")
            continue

        filter_key = "size_" + parts[1]
        if filter_key not in data.get("filters", {}):
            print(key, "-> FAIL (사유: 해당 크기 필터 없음)")
            fail_list.append(key + ": 해당 크기 필터 없음")
            continue

        raw_filters = data["filters"][filter_key]
        norm_filters = {}
        for f_key in raw_filters:
            norm_filters[normalize_label(f_key)] = raw_filters[f_key]

        if "Cross" not in norm_filters or "X" not in norm_filters:
            print(key, "-> FAIL (사유: Cross 또는 X 필터 누락)")
            fail_list.append(key + ": Cross 또는 X 필터 누락")
            continue

        filt_cross = norm_filters["Cross"]
        filt_x = norm_filters["X"]

        pattern = data["patterns"][key].get("input", [])
        expected = normalize_label(data["patterns"][key].get("expected", ""))

        n = len(filt_cross)
        if (
            len(pattern) != n
            or any(len(row) != n for row in pattern)
            or len(filt_x) != n
            or any(len(row) != n for row in filt_x)
        ):
            print(key, "-> FAIL (사유: 필터와 패턴 크기 불일치)")
            fail_list.append(key + ": 필터와 패턴 크기 불일치")
        else:
            score_cross = mac_operation(pattern, filt_cross)
            score_x = mac_operation(pattern, filt_x)
            pred = compare_scores(score_cross, score_x, "Cross", "X")

            if pred == "UNDECIDED":
                status = "FAIL"
                fail_list.append(key + f": 동점 자동 UNDECIDED 처리로 인한 자동 FAIL (expected={expected})")
            elif pred == expected:
                status = "PASS"
                pass_count += 1
            else:
                status = "FAIL"
                fail_list.append(key + f": 판정 불일치 (pred={pred}, expected={expected})")

            print(
                f"{key} | Cross점수: {score_cross} | X점수: {score_x} | 판정: {pred} | expected: {expected} -> {status}"
            )

    measure_performance([3, 5, 13, 25])

    print("\n=== 결과 요약 ===")
    print(f"전체 테스트 수: {total_count} | 통과 수: {pass_count} | 실패 수: {len(fail_list)}")
    if len(fail_list) > 0:
        print("실패 케이스 목록:")
        for fail_msg in fail_list:
            print(" -", fail_msg)


def main():
    print("=== Mini NPU 시뮬레이터 ===")
    print("1. 사용자 입력 모드 (3x3)")
    print("2. data.json 분석 모드")
    while True:
        choice = input("모드를 선택하세요 (1 또는 2): ").strip()
        if choice == "1":
            run_mode_1()
            break
        elif choice == "2":
            run_mode_2()
            break
        else:
            print("잘못된 입력입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
