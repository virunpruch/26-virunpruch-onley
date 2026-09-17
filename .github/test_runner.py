import os
import re
import subprocess
import sys


def normalize_text(text):
    """ตัดสัญลักษณ์ ตัวพิมพ์เล็ก-ใหญ่ และเว้นวรรคส่วนเกิน"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[!.,:="\'\(\)]', " ", text)
    return " ".join(text.split())


def extract_numbers(text):
    """ดึงตัวเลขทั้งหมดจากผลลัพธ์ของนักเรียน"""
    if not text:
        return []
    return [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]


def run_student_code(filename, input_data):
    """สั่งรันโค้ดนักเรียน รองรับทั้งมีและไม่มี .py"""
    target_file = filename
    if not os.path.exists(target_file) and not target_file.endswith(".py"):
        target_file = filename + ".py"

    if not os.path.exists(target_file):
        return None, "File Not Found"

    try:
        process = subprocess.run(
            [sys.executable, target_file],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=5,
        )
        return process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return None, "Timeout (โปรแกรมวนลูปไม่จบ)"
    except Exception as e:
        return None, str(e)


# =========================================================
# เกณฑ์การตรวจยืดหยุ่นแยกรายข้อสำหรับ Set 6 (ข้อละ 4 คะแนน)
# =========================================================


def grade_exam_1(output, stderr, test_case):
    """ข้อ 1: คำนวณคะแนนเฉลี่ย 3 วิชา [(s1 + s2 + s3) / 3]"""
    expected = test_case["expected"]
    total_sum = test_case["sum"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณหาค่าเฉลี่ยถูกต้องได้เต็ม
    elif any(abs(n - total_sum) < 0.1 for n in nums):
        return 0.5  # คำนวณเฉพาะผลรวม 3 วิชา (ลืมหาร 3)
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_2(output, stderr, test_case):
    """ข้อ 2: ตรวจสอบความสูงสำหรับเล่นเครื่องเล่น (Can Ride / Cannot Ride)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected == "cannot ride":
        if "cannot" in norm_out or ("can" in norm_out and "not" in norm_out):
            return 1.0  # พิมพ์ Cannot Ride ถูกต้อง
    elif expected == "can ride":
        if "can" in norm_out and "not" not in norm_out:
            return 1.0  # พิมพ์ Can Ride ถูกต้อง

    if "ride" in norm_out or "can" in norm_out:
        return 0.5  # มีการแสดงผลคำตอบกลุ่มเล่นเครื่องเล่นได้
    return 0.0


def grade_exam_3(output, stderr, test_case):
    """ข้อ 3: ตรวจสอบการหาร 5 ลงตัว (Yes / No)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์ Yes หรือ No ถูกต้อง
    elif "yes" in norm_out or "no" in norm_out:
        return 0.5  # พิมพ์คำตอบออกมาแต่เงื่อนไขสลับกัน
    return 0.0


def grade_exam_4(output, stderr, test_case):
    """ข้อ 4: คำนวณค่าจัดส่งตามน้ำหนัก (30, 50, 100)"""
    expected = test_case["expected"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.1 for n in nums):
        return 1.0  # คำนวณค่าจัดส่งตรงเงื่อนไข
    elif any(n in [30, 50, 100] for n in nums):
        return 0.5  # พิมพ์ตัวเลขกลุ่มราคาค่าจัดส่งออกมาแต่เงื่อนไขผิด
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_5(output, stderr, test_case):
    """ข้อ 5: บอกช่วงเวลา 24 ชม. (Morning / Afternoon / Night)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์ Morning / Afternoon / Night ถูกต้อง
    elif any(k in norm_out for k in ["morning", "afternoon", "night"]):
        return 0.5  # พิมพ์ช่วงเวลาออกมาได้แต่เงื่อนไขสลับกัน
    return 0.0


# =========================================================
# ชุดข้อมูลทดสอบ (Test Cases สำหรับ Set 6)
# =========================================================
EXAMS = {
    "Examination_1.py": {
        "grader": grade_exam_1,
        "cases": [
            {"input": "80\n90\n70\n", "expected": 80.0, "sum": 240},
            {"input": "10\n20\n30\n", "expected": 20.0, "sum": 60},
            {"input": "50\n50\n50\n", "expected": 50.0, "sum": 150},
            {"input": "15\n25\n40\n", "expected": 26.67, "sum": 80},
        ],
    },
    "Examination_2.py": {
        "grader": grade_exam_2,
        "cases": [
            {"input": "150\n", "expected": "Can Ride"},
            {"input": "140\n", "expected": "Can Ride"},
            {"input": "139\n", "expected": "Cannot Ride"},
            {"input": "100\n", "expected": "Cannot Ride"},
        ],
    },
    "Examination_3.py": {
        "grader": grade_exam_3,
        "cases": [
            {"input": "15\n", "expected": "Yes"},
            {"input": "0\n", "expected": "Yes"},
            {"input": "7\n", "expected": "No"},
            {"input": "14\n", "expected": "No"},
        ],
    },
    "Examination_4.py": {
        "grader": grade_exam_4,
        "cases": [
            {"input": "0.5\n", "expected": 30},
            {"input": "1.0\n", "expected": 30},
            {"input": "4.0\n", "expected": 50},
            {"input": "10.0\n", "expected": 100},
        ],
    },
    "Examination_5.py": {
        "grader": grade_exam_5,
        "cases": [
            {"input": "8\n", "expected": "Morning"},
            {"input": "12\n", "expected": "Afternoon"},
            {"input": "15\n", "expected": "Afternoon"},
            {"input": "20\n", "expected": "Night"},
        ],
    },
}

# =========================================================
# ประมวลผลและสร้าง Markdown สรุปคะแนน
# =========================================================
total_score = 0.0
summary_rows = []

for exam_name, exam_data in EXAMS.items():
    grader = exam_data["grader"]
    cases = exam_data["cases"]

    exam_score = 0.0
    passed_cases = 0.0

    for case in cases:
        stdout, stderr = run_student_code(exam_name, case["input"])
        if stdout is not None:
            score = grader(stdout, stderr, case)
            exam_score += score
            if score >= 1.0:
                passed_cases += 1.0
            elif score > 0:
                passed_cases += 0.5

    final_exam_score = min(4.0, round(exam_score, 1))
    total_score += final_exam_score

    if final_exam_score >= 4.0:
        status = "🟢 ผ่าน"
    elif final_exam_score > 0:
        status = "🟡 ผ่านบางส่วน"
    else:
        status = "❌ ไม่ผ่าน"

    score_display = (
        f"{int(final_exam_score)}"
        if final_exam_score.is_integer()
        else f"{final_exam_score}"
    )
    passed_display = (
        f"{int(passed_cases)}"
        if passed_cases.is_integer()
        else f"{passed_cases}"
    )

    summary_rows.append(
        f"| `{exam_name}` | {status} | {passed_display}/4 เคส | {score_display} / 4 |"
    )

final_total_display = (
    f"{int(total_score)}" if total_score.is_integer() else f"{total_score}"
)

markdown_summary = f"""
## 📊 สรุปผลการสอบวิชาเขียนโปรแกรม (Set 6)

| ข้อสอบ | สถานะการตรวจ | ผ่าน Test Cases | คะแนนที่ได้ |
| :--- | :--- | :--- | :--- |
""" + "\n".join(summary_rows) + f"""

### 🎯 คะแนนรวมทั้งหมด: {final_total_display} / 20 คะแนน
"""

print(markdown_summary)

github_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if github_summary_path:
    with open(github_summary_path, "a", encoding="utf-8") as f:
        f.write(markdown_summary)
