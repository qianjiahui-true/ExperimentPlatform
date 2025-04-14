from flask import Flask, render_template, request, redirect, url_for, session
import random
import time
import csv  # 导入 CSV 模块
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于加密会话数据

# 联想任务
questions = [
    {"question": "亮、照、星", "answer": "明"},
    {"question": "代、童、级", "answer": "年"},
    {"question": "倒、超、票", "answer": "车"},
    {"question": "刻、光、临", "answer": "时"},
    {"question": "升、问、费", "answer": "学"},
    {"question": "印、园、费", "answer": "花"},
    {"question": "原、清、超", "answer": "高"},
    {"question": "酒、选、发", "answer": "美"},
    {"question": "员、计、体", "answer": "会"},
    {"question": "问、案、应", "answer": "答"},
    {"question": "夜、接、断", "answer": "间"},
    {"question": "奇、转、喜", "answer": "好"},
    {"question": "存、女、写", "answer": "生"},
    {"question": "导、费、表", "answer": "电"},
    {"question": "展、改、度", "answer": "进"},
    {"question": "等、架、流", "answer": "上"},
    {"question": "建、新、趣", "answer": "兴"},
    {"question": "得、逃、过", "answer": "难"},
    {"question": "播、导、得", "answer": "主"},
    {"question": "政、通、善", "answer": "变"},
    {"question": "数、女、减", "answer": "少"},
    {"question": "书、试、表", "answer": "面"},
    {"question": "期、落、善", "answer": "后"},
    {"question": "条、原、压", "answer": "油"},
    {"question": "歌、友、养", "answer": "老"},
    {"question": "求、物、词", "answer": "证"},
    {"question": "流、掉、平", "answer": "放"},
    {"question": "火、落、指", "answer": "点"},
    {"question": "无、报、节", "answer": "情"},
    {"question": "留、图、随", "answer": "意"},
    {"question": "异、格、感", "answer": "性"},
    {"question": "当、宜、轻", "answer": "便"},
    {"question": "缘、先、内", "answer": "人"},
    {"question": "考、产、测", "answer": "量"},
    {"question": "航、产、运", "answer": "海"},
    {"question": "间、观、守", "answer": "看"},
    {"question": "解、原、论", "answer": "理"},
    {"question": "解、服、听", "answer": "说"},
    {"question": "通、业、李", "answer": "行"},
    {"question": "速、语、见", "answer": "成"},
]

questions_test=[
    {"question": "牌、现、钱", "answer": "金"},
    {"question": "黑、具、德", "answer": "道"},
]

# 模拟将用户随机分配到控制组或实验组
def assign_group():
    return random.choice(['control', 'experiment'])

def record_data(user_id, group, likert_scale, difficulty_change, correct_rate, time_taken, user_answer, difficulty_perception, performance_comparision ):
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
                    ['user_id', 'group', 'likert_scale','difficulty_change','correct_rate', 'time_taken', 'user_answer', 'difficulty_change', 'performance_comparision'])
            # 写入数据（每次答题提交时）
            writer.writerow(
                [user_id, group, likert_scale, difficulty_change, correct_rate, time_taken, user_answer, difficulty_change, performance_comparision])
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

USER_ID_FILE = 'last_user_id.txt'

# 读取或初始化 user_id
def get_next_user_id():
    # 检查文件是否存在
    if os.path.exists(USER_ID_FILE):
        # 如果文件存在，读取上一个 user_id
        with open(USER_ID_FILE, 'r') as file:
            last_user_id = int(file.read().strip())
        # 生成下一个 user_id
        next_user_id = last_user_id + 1
    else:
        # 如果文件不存在，表示是第一次运行，设置为 001
        next_user_id = 1
    
    # 将下一个 user_id 存回文件中
    with open(USER_ID_FILE, 'w') as file:
        file.write(str(next_user_id))
    
    return f"user_{next_user_id:03d}"  # 返回格式化后的 user_id，如 user_001, user_002


@app.route('/')
def index():
    # 为每个用户分配组别（控制组或实验组）
    session['group'] = assign_group()
    session['user_id'] = get_next_user_id()  # 可以根据需要动态生成用户ID
    session['current_question_index'] = 0  # 从第一个问题开始
    return render_template('index.html', group=session['group'])

# 处理用户点击同意或不同意的操作
@app.route('/handle_consent', methods=['POST'])
def handle_consent():
    consent = request.form.get('consent')
    if consent == 'agree':
        # 如果用户同意，跳转到期望问卷页面
        return redirect(url_for('surveypre'))
    else:
        # 如果用户不同意，跳转到感谢页面
        return redirect(url_for('disagree'))

@app.route('/disagree')
def disagree():
    # 显示感谢页面，用户选择不同意后跳转到此页面
    return render_template('disagree.html')

@app.route('/tasktest', methods=['GET', 'POST'])
def tasktest():
    if 'current_question_index' not in session:
        session['current_question_index'] = 0  # 初始化题目索引
    
    current_index = session['current_question_index']
    if current_index >= len(questions_test):
        return render_template('finish_test.html')  # 练习题完成后跳转到结束页面

    current_question = questions_test[current_index]  # 获取当前题目
    error_message = None

    if request.method == 'POST':
        user_answer = request.form['answer'].strip()  # 获取用户输入的答案
        correct_answer = current_question['answer']

        if user_answer != correct_answer:
            error_message = f"回答错误！正确答案是：{correct_answer}"
        else:
            error_message = "回答正确！"
            session['current_question_index'] += 1  # 正确答案，跳到下一题
             # 等待1.5秒后跳转到下一个题目
        time.sleep(1.5)

    return render_template('tasktest.html', question=current_question['question'], error_message=error_message)

@app.route('/finish_test')
def finish_test():
    # 如果用户完成了所有练习题，显示“开始正式实验”按钮
    return render_template('finish_test.html')

@app.route('/surveypre', method=['GET','POST'])
def survey():
    if request.method == 'POST': #处理问卷结果
        likert_scale = request.form['likert_scale']
        session['likert_scale'] = likert_scale

        difficulty_change = request.form[difficulty_change]
        session['difficulty_change'] = difficulty_change
        
        return redirect(url_for('tasktest'))

    return render_template('surveypre.html', group=session['group'])

@app.route('/task', methods=['GET', 'POST'])
def task():
    try:
        group = session['group']
        current_question_index = session['current_question_index']

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

            # 保存任务数据到会话
            session['correct_rate'] = correct_rate
            session['time_taken'] = time_taken
            session['user_answer'] = user_answer

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

            # 更新当前题目索引，继续到下一题
            session['current_question_index'] += 1
            print(
                f"Next question index: {session['current_question_index']} (debug)")

        # 如果是 GET 请求，渲染页面并显示当前题目
        return render_template('task.html', question = current_question, group=group, error_message=error_message, next_question_index=session['current_question_index'])

    except Exception as e:
        print(f"Error in task route: {e}")
        return "Internal Server Error", 500  # 返回 500 错误，便于调试

@app.route('/surveypost', methods=['GET', 'POST'])
def surveypost():
    if request.method == 'POST':
        # 获取提交的问卷数据
        difficulty_perception = request.form['difficulty_perception']
        session['difficulty_perception'] = difficulty_perception
        performance_comparison = request.form['performance_comparison']
        session['performance_comparison']= performance_comparison

       # 将所有数据一起保存到 CSV 文件中
        record_data(
            session.get('user_id', 'user_001'),
            session['group'],
            session['likert_scale'],
            session['difficulty_change'],
            session['correct_rate'],
            session['time_taken'],
            session['user_answer'],
            session['difficulty_perception'],
            session['performance_comparison'],
        )
        
        # 提交后跳转到结束页面或其他任务页面
        return redirect(url_for('finish'))

    return render_template('surveypost.html', group=session['group'])

@app.route('/finish')
def finish():
    return render_template('finish.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
