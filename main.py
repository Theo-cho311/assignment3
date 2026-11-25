import json
import time


def mac_operation(pattern, filt):
    n = len(pattern)
    total = 0.0
    for r in range(n):
        for c in range(n):
            total += pattern[r][c] * filt[r][c]
    return total


def compare_scores(score_a, score_b, label_a, label_b):
    if abs(score_a - score_b) < 1e-9:
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
    if label == "+" or label == "cross" or label == "Cross":
        return "Cross"
    elif label == "x" or label == "X":
        return "X"
    else:
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

    print("\n=== 모드 1 판정 결과 ===")
    print("필터 A 점수:", score_a)
    print("필터 B 점수:", score_b)
    print(f"연산 시간: {elapsed_ms:.6f} ms")
    print("판정 결과:", result)

    measure_performance([3])


def run_mode_2():
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    total_count = 0
    pass_count = 0
    fail_list = []

    print("\n=== data.json 일괄 판정 ===")
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

            if pred == expected:
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
