from flask import Flask, request, redirect, session
from datetime import date, datetime
import json

app = Flask(__name__)
app.secret_key = "970512"

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

menu = """
<div style="background:#4CAF50;padding:15px;">
<a href="/" style="color:white;margin:10px;">대시보드</a>
<a href="/items" style="color:white;margin:10px;">준비물</a>
<a href="/tasks" style="color:white;margin:10px;">수행평가</a>
<a href="/exam" style="color:white;margin:10px;">기말 D-Day</a>
<a href="/notice" style="color:white;margin:10px;">공지사항</a>
<a href="/suggest" style="color:white;margin:10px;">익명 건의함</a>
<button onclick="toggleDark()">🌙</button>
</div>
"""

style = """
<style>

body{
font-family:Arial;
background:#f4f6f8;
margin:0;
padding:0;
text-align:center;
}

.menu{
background:#4CAF50;
padding:15px;
}

.menu a{
color:white;
margin:10px;
text-decoration:none;
font-weight:bold;
}

.card{
background:white;
padding:25px;
margin:20px auto;
border-radius:15px;
box-shadow:0 3px 10px rgba(0,0,0,0.1);
max-width:700px;
}

.weekbox{
display:flex;
gap:15px;
margin-top:20px;
flex-wrap:wrap;
justify-content:center;
}

.daycard{
background:white;
border-radius:15px;
padding:20px;
width:130px;
text-align:center;
box-shadow:0 3px 8px rgba(0,0,0,0.1);
transition:0.2s;
}

.daycard:hover{
transform:translateY(-5px);
}

.day{
font-size:20px;
font-weight:bold;
margin-bottom:8px;
}

.item{
font-size:14px;
color:#555;
}

.taskbox{
display:flex;
flex-direction:column;
gap:15px;
margin-top:20px;
}

.taskcard{
background:white;
border-radius:12px;
padding:15px;
box-shadow:0 2px 8px rgba(0,0,0,0.1);
text-align:left;
}

.subject{
font-size:20px;
font-weight:bold;
margin-bottom:5px;
}

.desc{
font-size:14px;
color:#555;
}

.taskcard a{
font-size:12px;
color:#ff4444;
text-decoration:none;
}

.dark{
background:#1e1e1e;
color:white;
}

.dark .card{
background:#2a2a2a;
}

.dark .daycard{
background:#2a2a2a;
}

</style>
"""

script = """
<script>

function toggleDark(){
    document.body.classList.toggle("dark")

    if(document.body.classList.contains("dark")){
        localStorage.setItem("darkmode","on")
    }else{
        localStorage.setItem("darkmode","off")
    }
}

window.onload = function(){
    if(localStorage.getItem("darkmode") === "on"){
        document.body.classList.add("dark")
    }
}

</script>
"""

def save_data(data):
    with open("data.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

@app.route("/")
def dashboard():
    return f"""
    {style}
    {script}
    {menu}

    <div class="card">
    <h1>3학년 3반 대시보드에 오신 걸 환영합니다</h1>

    </div>
    """

@app.route("/items")
def items_page():

    cards = ""

    today = date.today().weekday()
    days = ["월","화","수","목","금"]

    for i, (day, item) in enumerate(data["items"].items()):

        highlight = ""

        if days[i] == days[today]:
            highlight = 'style="border:3px solid #4CAF50;"'

        cards += f"""
        <div class="daycard" {highlight}>
            <div class="day">{day}</div>
            <div class="item">{item}</div>
        </div>
        """

    return f"""
    {style}{script}{menu}

    <div class="card">
    <h2>준비물</h2>

    <div class="weekbox">
    {cards}
    </div>

    </div>
    """

@app.route("/tasks")
def tasks():

    cards = ""

    for i, t in enumerate(data["tasks"]):

        dday_text = ""

        if t["date"] and "-" in t["date"]:

            due = datetime.strptime(t["date"], "%Y-%m-%d").date()
            d = (due - date.today()).days

            if d > 0:
                dday_text = f"D-{d}"
            elif d == 0:
                dday_text = "D-DAY"
            else:
                dday_text = f"D+{abs(d)}"

        cards += f"""
        <div class="taskcard">

            <div class="subject">{t["subject"]}</div>
            <div class="desc">{t["desc"]}</div>
            <div class="desc">{t["date"]} ({dday_text})</div>

        </div>
        """

    return f"""
    {style}{script}{menu}

    <div class="card">
    <h2>수행평가</h2>

    <div class="taskbox">
    {cards}
    </div>

    </div>
    """

@app.route("/exam")
def exam():

    today = date.today()

    exam1 = date(today.year,6,30)
    exam2 = date(today.year,7,1)
    exam3 = date(today.year,7,2)

    d1 = (exam1 - today).days
    d2 = (exam2 - today).days
    d3 = (exam3 - today).days

    return f"""
    {style}{script}{menu}

    <div class="card">
    <h2>기말고사 D-Day</h2>
    <p>6월 30일 → D-{d1}</p>
    <p>7월 1일 → D-{d2}</p>
    <p>7월 2일 → D-{d3}</p>
    </div>
    """

@app.route("/notice")
def notice():

    cards = ""

    for n in data["notice"]:

        cards += f"""
        <div class="taskcard">

            <div class="subject">{n["title"]}</div>
            <div class="desc">{n["desc"]}</div>

        </div>
        """

    return f"""
    {style}{script}{menu}

    <div class="card">
    <h2>공지사항</h2>

    <div class="taskbox">
    {cards}
    </div>

    </div>
    """

@app.route("/suggest", methods=["GET","POST"])
def suggest():

    if request.method == "POST":

        text = request.form.get("text")

        if text:
            data["suggest"].append({
             "text": text,
             "time": datetime.now().strftime("%m-%d %H:%M")
            })
            save_data(data)

        return redirect("/suggest")

    return f"""
    {style}{script}{menu}

    <div class="card">
    <h2>익명 건의함</h2>

    <form method="post">
    <textarea name="text" rows="5" style="width:90%;"></textarea><br><br>
    <button type="submit">건의 보내기</button>
    </form>

    </div>
    """

from flask import request

@app.route("/admin", methods=["GET","POST"])
def admin():

    password = "970512"

    # 로그인 처리
    if request.method == "POST" and "password" in request.form:
        if request.form["password"] == password:
            session["admin"] = True
        else:
            return """
            <h2>관리자 로그인</h2>
            <p>비밀번호 틀림</p>
            <form method="post">
            비밀번호 <input type="password" name="password">
            <button type="submit">로그인</button>
            </form>
            """

    # 로그인 안했으면 로그인 화면
    if not session.get("admin"):
        return """
        <h2>관리자 로그인</h2>
        <form method="post">
        비밀번호 <input type="password" name="password">
        <button type="submit">로그인</button>
        </form>
        """

    # ===== 여기부터 관리자 페이지 =====

    if request.method == "POST":

        for day in ["월","화","수","목","금"]:
            data["items"][day] = request.form.get(day,"")

        tasks = []
        i = 0

        while True:
            subject = request.form.get(f"subject{i}")
            desc = request.form.get(f"desc{i}")
            date = request.form.get(f"date{i}")

            if subject is None:
                break

            tasks.append({
                "subject": subject,
                "desc": desc,
                "date": date
            })

            i += 1

        data["tasks"] = tasks

        notices = []
        i = 0

        while True:
            title = request.form.get(f"title{i}")
            desc = request.form.get(f"ndesc{i}")

            if title is None:
                break

            notices.append({
                "title": title,
                "desc": desc
            })

            i += 1

        data["notice"] = notices

        save_data(data)

    task_html = ""

    for i, task in enumerate(data["tasks"]):
        task_html += f"""
        <div class="taskcard">
        과목 <input name="subject{i}" value="{task['subject']}">
        설명 <input name="desc{i}" value="{task['desc']}">
        마감 <input name="date{i}" value="{task['date']}">
        <a href="/delete_task/{i}">삭제</a>
        </div><br>
        """

    notice_html = ""

    for i, n in enumerate(data["notice"]):

        notice_html += f"""
        <div class="taskcard">
        제목 <input name="title{i}" value="{n['title']}">
        설명 <input name="ndesc{i}" value="{n['desc']}">
        <a href="/delete_notice/{i}">삭제</a>
        </div><br>
        """

    suggest_html = ""

    for i, s in enumerate(data["suggest"]):

        suggest_html += f"""
        <div class="taskcard">
        {s["text"]}
        <br>
        <small>{s["time"]}</small>
        <br>
        <a href="/delete_suggest/{i}">삭제</a>
        </div><br>
        """

    return f"""
    {style}

    <div class="card">

    <h2>관리자 페이지</h2>

    <form method="post">

    <h3>준비물</h3>

    월 <input name="월" value="{data["items"]["월"]}"><br>
    화 <input name="화" value="{data["items"]["화"]}"><br>
    수 <input name="수" value="{data["items"]["수"]}"><br>
    목 <input name="목" value="{data["items"]["목"]}"><br>
    금 <input name="금" value="{data["items"]["금"]}"><br><br>

    <h3>수행평가</h3>

    <br>

    {task_html}

    <br>
    <a href="/add_task">수행평가 추가</a>

    <br><br>

    <h3>공지사항</h3>

    <br>

    {notice_html}

    <br>
    <a href="/add_notice">공지 추가</a>

    <br><br>
    <button type="submit">저장</button>

    </form>

    <h3>익명 건의함</h3>

    <br>

    {suggest_html}

    <br>
    <a href="/">대시보드로 돌아가기</a>

    </div>
    """

@app.route("/add_task")
def add_task():

    if not session.get("admin"):
        return redirect("/admin")

    data["tasks"].append({
        "subject":"새 과목",
        "desc":"설명",
        "date":"마감"
    })

    save_data(data)

    return redirect("/admin")

@app.route("/delete_task/<int:i>")
def delete_task(i):

    if not session.get("admin"):
        return redirect("/admin")

    data["tasks"].pop(i)

    save_data(data)

    return redirect("/admin")

@app.route("/add_notice")
def add_notice():

    if not session.get("admin"):
        return redirect("/admin")

    data["notice"].append({
        "title":"새 공지",
        "desc":"내용"
    })

    save_data(data)

    return redirect("/admin")

@app.route("/delete_notice/<int:i>")
def delete_notice(i):

    if not session.get("admin"):
        return redirect("/admin")

    data["notice"].pop(i)

    save_data(data)

    return redirect("/admin")

@app.route("/delete_suggest/<int:i>")
def delete_suggest(i):

    if not session.get("admin"):
        return redirect("/admin")

    data["suggest"].pop(i)

    save_data(data)

    return redirect("/admin")

app.run(debug=True)
