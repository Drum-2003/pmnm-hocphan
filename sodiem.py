from flask import Flask, jsonify, request, url_for, abort, redirect
from markupsafe import escape

app = Flask(__name__)

app.json.ensure_ascii = False  

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A",
                   "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},

    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A",
                   "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},

    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B",
                   "scores": {"PMMNM": 9.5, "CSDL": 9.0}},

    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B",
                   "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},

    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A",
                   "scores": {}},

    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C",
                   "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}
def tinh_diem_tb(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)


def xep_loai(diem_tb):
    if diem_tb is None:
        return "—"
    if diem_tb >= 8.0:
        return "Giỏi"
    if diem_tb >= 6.5:
        return "Khá"
    if diem_tb >= 5.0:
        return "Trung bình"
    return "Yếu"


def build_student(mssv, sv):
    tb = tinh_diem_tb(sv["scores"])
    return {
        "mssv": mssv,
        "name": sv["name"],
        "lop": sv["lop"],
        "scores": sv["scores"],
        "diem_tb": tb,
        "xep_loai": xep_loai(tb),
    }
def danh_sach_lop():
    return sorted({sv["lop"] for sv in STUDENTS.values()})


def hien_thi_diem(tb):
    return tb if tb is not None else "—"

def page(title, body):
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>

<style>
    * {{
        box-sizing: border-box;
    }}

    body {{
        font-family: Arial, sans-serif;
        background: #f4f6f8;
        color: #333;
        max-width: 950px;
        margin: 0 auto;
        padding: 30px 20px;
    }}

    .container {{
        background: white;
        padding: 28px;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.08);
    }}

    h1 {{
        color: #2e8b57;
        margin-top: 0;
        margin-bottom: 20px;
    }}

    h2 {{
        color: #444;
        margin-top: 25px;
    }}

    p {{
        line-height: 1.6;
    }}

    a {{
        color: #2e8b57;
    }}

    ul {{
        padding-left: 20px;
    }}

    li {{
        margin: 10px 0;
    }}

    table {{
        border-collapse: collapse;
        width: 100%;
        margin-top: 18px;
        background: white;
        border-radius: 8px;
        overflow: hidden;
    }}

    th {{
        background: #2e8b57;
        color: white;
        padding: 12px 10px;
        text-align: left;
    }}

    td {{
        border-bottom: 1px solid #ddd;
        padding: 11px 10px;
    }}

    tr:hover {{
        background: #f1f8f4;
    }}

    .filter {{
        margin: 15px 0;
    }}

    .filter a {{
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
        padding: 7px 14px;
        border: 1px solid #2e8b57;
        border-radius: 20px;
        text-decoration: none;
        color: #2e8b57;
        background: white;
    }}

    .filter a:hover {{
        background: #eaf6ef;
    }}

    .filter a.active {{
        background: #2e8b57;
        color: white;
    }}

    .card {{
        background: #f8faf9;
        padding: 15px 18px;
        border-left: 4px solid #2e8b57;
        border-radius: 6px;
        margin: 15px 0;
    }}

    .back {{
        display: inline-block;
        margin-top: 20px;
        text-decoration: none;
        font-weight: bold;
    }}

    .menu {{
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 20px;
    }}

    .menu a {{
        display: inline-block;
        padding: 10px 16px;
        background: #2e8b57;
        color: white;
        border-radius: 6px;
        text-decoration: none;
    }}

    .menu a:hover {{
        background: #246b45;
    }}
</style>

</head>

<body>
<div class="container">
{body}
</div>
</body>
</html>"""

@app.route("/home")
@app.route("/")
def index():
    total = len(STUDENTS)
    so_lop = len(danh_sach_lop())
    body = f"""
<h1>Sổ điểm sinh viên</h1>
<p>Tổng số sinh viên: <strong>{total}</strong></p>
<p>Số lớp: <strong>{so_lop}</strong></p>
<ul>
  <li><a href="{url_for('student_list')}">/students</a></li>
  <li><a href="{url_for('api_students')}">/api/students</a></li>
</ul>"""
    return page("Trang chủ", body)

@app.route("/danh-sach")
@app.route("/students")
def student_list():
    lop = request.args.get("lop", "").strip() 
    students = [build_student(m, sv) for m, sv in STUDENTS.items()]
    if lop: 
        students = [s for s in students if s["lop"].lower() == lop.lower()]
    cls = "active" if not lop else ""
    links = [f'<a class="{cls}" href="{url_for("student_list")}">Tất cả</a>']
    for l in danh_sach_lop():
        cls = "active" if lop.lower() == l.lower() else ""
        links.append(f'<a class="{cls}" href="{url_for("student_list", lop=l)}">{l}</a>')
    thanh_loc = f'<div class="filter">{"".join(links)}</div>'

    if students:
        rows = ""
        for s in students:
            rows += (
                "<tr>"
                f'<td><a href="{url_for("student_detail", mssv=s["mssv"])}">{s["mssv"]}</a></td>'
                f'<td>{escape(s["name"])}</td>'
                f'<td>{s["lop"]}</td>'
                f'<td>{hien_thi_diem(s["diem_tb"])}</td>'
                f'<td>{s["xep_loai"]}</td>'
                "</tr>"
            )
        ket_qua = ("<table><tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th>"
                   f"<th>Điểm TB</th><th>Xếp loại</th></tr>{rows}</table>")
    else:
        ket_qua = '<p style="color:#b00">Không có sinh viên phù hợp.</p>'

    body = (f"<h1>Danh sách sinh viên</h1>{thanh_loc}{ket_qua}"
            f'<p><a href="{url_for("index")}">← Trang chủ</a></p>')
    return page("Danh sách sinh viên", body)
@app.route("/students/<mssv>")
def student_detail(mssv):
    sv = STUDENTS.get(mssv)
    if sv is None:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    s = build_student(mssv, sv)
    if s["scores"]:
        rows = "".join(
            f"<tr><td>{mon}</td><td>{diem}</td></tr>"
            for mon, diem in s["scores"].items()
        )
        bang_diem = f"<table><tr><th>Học phần</th><th>Điểm</th></tr>{rows}</table>"
    else:
        bang_diem = "<p>Chưa có điểm.</p>"

    body = f"""
<h1>{escape(s["name"])}</h1>
<p>MSSV: <strong>{s["mssv"]}</strong></p>
<p>Lớp: <a href="{url_for("student_list", lop=s["lop"])}">{s["lop"]}</a></p>
<p>Điểm TB: <strong>{hien_thi_diem(s["diem_tb"])}</strong>
   | Xếp loại: <strong>{s["xep_loai"]}</strong></p>
<h2>Bảng điểm</h2>
{bang_diem}
<p><a href="{url_for("student_list")}">← Danh sách</a></p>"""
    return page(s["name"], body)

@app.route("/s/<mssv>")
@app.route("/sv/<mssv>")
def short_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)
@app.route("/api/students")
def api_students():
    return jsonify([build_student(m, sv) for m, sv in STUDENTS.items()])
if __name__ == "__main__":
    app.run(debug=True, port=8000)
