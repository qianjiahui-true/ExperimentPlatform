from flask import Flask, render_template, request, redirect, url_for, session
import random
import time
import csv  # 导入 CSV 模块
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于加密会话数据

# 任务题目列表（假设数据）
questions = [
    {"question": "erucse", "answer": "rescue"},
    {"question": "ichar", "answer": "chair"},
    {"question": "tep", "answer": "pet"},
    {"question": "cuerse", "answer": "rescue"},
    # 更多题目可以在此添加
]

# 模拟将用户随机分配到控制组或实验组


def assign_group():
    return random.choice(['control', 'experiment'])


def record_data(user_id, group, correct_rate, time_taken, user_answer):
    # 获取文件路径
    file_path = os.path.join(os.getcwd(), 'user_data.csv')

    # 检查文件是否已经存在，如果文件不存在，则写入表头
    file_exists = os.path.exists(file_path)

    try:
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # 如果文件是第一次创建，写入表头
                writer.writerow(
                    ['user_id', 'group', 'correct_rate', 'time_taken', 'user_answer'])
            # 写入数据（每次答题提交时）
            writer.writerow(
                [user_id, group, correct_rate, time_taken, user_answer])
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")


@app.route('/')
def index():
    # 为每个用户分配组别（控制组或实验组）
    session['group'] = assign_group()
    session['user_id'] = 'user_001'  # 可以根据需要动态生成用户ID
    session['current_question_index'] = 0  # 从第一个问题开始
    return render_template('index.html', group=session['group'])


@app.route('/task', methods=['GET', 'POST'])
def task():
    try:
        group = session['group']
        current_question_index = session['current_question_index']

        print("Current question index:", current_question_index)  # 打印查看索引值

        if current_question_index >= len(questions):
            return redirect(url_for('finish'))

        # 获取当前题目
        current_question = questions[current_question_index]

        # 初始化 error_message，防止未定义错误
        error_message = None

        # 表单提交
        if request.method == 'POST':
            # 获取用户输入的答案
            user_answer = request.form['answer'].strip()

            # 尝试获取 correct_rate 和 time_taken，如果无法转换为 float，设置默认值
            try:
                correct_rate = float(request.form['correct_rate'])
                time_taken = float(request.form['time_taken'])
            except ValueError:
                correct_rate = 0.0
                time_taken = 0.0

            # 获取当前题目正确答案
            correct_answer = current_question['answer']
            is_correct = (user_answer == correct_answer)

            # 根据组别提供不同的错误提示
            if group == 'control':
                if not is_correct:
                    error_message = "错误！请继续下一题。"
                else:
                    error_message = "回答正确"
            elif group == 'experiment':
                if not is_correct:
                    error_message = "错误！系统将根据您的错误调整后续难度。"
                else:
                    error_message = "回答正确"

            # 调用 record_data 保存数据到 CSV
            record_data(session.get('user_id', 'user_001'), group,
                        correct_rate, time_taken, user_answer)
            # 更新当前题目索引，继续到下一题
            session['current_question_index'] += 1
            print(
                f"Next question index: {session['current_question_index']} (debug)")

        # 如果是 GET 请求，渲染页面并显示当前题目
        return render_template('task.html', question=current_question, group=group, error_message=error_message, next_question_index=session['current_question_index'])

    except Exception as e:
        print(f"Error in task route: {e}")
        return "Internal Server Error", 500  # 返回 500 错误，便于调试


@app.route('/next_question')
def next_question():
    """ 这个路由用于前端在 1.5 秒后自动跳转到下一题 """
    if 'current_question_index' in session:
        session['current_question_index'] += 1
    return redirect(url_for('task'))


@app.route('/finish')
def finish():
    return render_template('finish.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
