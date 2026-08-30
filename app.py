from flask import Flask, request, redirect, render_template_string
import psycopg2
import os

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            applied_date DATE NOT NULL DEFAULT CURRENT_DATE,
            status TEXT NOT NULL DEFAULT 'applied',
            link TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Job Tracker</title>
  <style>
    body { font-family: sans-serif; max-width: 900px; margin: 40px auto; }
    .stats { display: flex; gap: 20px; margin-bottom: 20px; }
    .stat { background: #f4f4f4; padding: 15px; border-radius: 6px; flex: 1; }
    .stat b { display: block; font-size: 24px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    input, select, textarea { padding: 8px; margin: 4px; }
    .applied { color: #666; }
    .interview { color: #0066cc; font-weight: bold; }
    .offer { color: #00aa00; font-weight: bold; }
    .rejected { color: #cc0000; }
  </style>
</head>
<body>
  <h1>Job Application Tracker</h1>

  <div class="stats">
    <div class="stat"><b>{{ total }}</b>Total</div>
    <div class="stat"><b>{{ interviews }}</b>Interviews</div>
    <div class="stat"><b>{{ rate }}%</b>Response Rate</div>
  </div>

  <form method="post" action="/add">
    <input name="company" placeholder="Company" required>
    <input name="position" placeholder="Position" required>
    <input name="link" placeholder="Job link">
    <select name="status">
      <option value="applied">Applied</option>
      <option value="interview">Interview</option>
      <option value="offer">Offer</option>
      <option value="rejected">Rejected</option>
    </select>
    <input name="notes" placeholder="Notes">
    <button>Add</button>
  </form>

  <table>
    <tr><th>Company</th><th>Position</th><th>Date</th><th>Status</th><th></th></tr>
    {% for a in apps %}
    <tr>
      <td>{{ a[1] }}</td>
      <td>{{ a[2] }}</td>
      <td>{{ a[3] }}</td>
      <td class="{{ a[4] }}">{{ a[4] }}</td>
      <td>
        <form method="post" action="/update/{{ a[0] }}" style="display:inline">
          <select name="status" onchange="this.form.submit()">
            <option {% if a[4]=='applied' %}selected{% endif %}>applied</option>
            <option {% if a[4]=='interview' %}selected{% endif %}>interview</option>
            <option {% if a[4]=='offer' %}selected{% endif %}>offer</option>
            <option {% if a[4]=='rejected' %}selected{% endif %}>rejected</option>
          </select>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, company, position, applied_date, status FROM applications ORDER BY applied_date DESC")
    apps = cur.fetchall()
    cur.close()
    conn.close()

    total = len(apps)
    responded = sum(1 for a in apps if a[4] != "applied")
    interviews = sum(1 for a in apps if a[4] == "interview")
    rate = round(responded / total * 100) if total else 0

    return render_template_string(TEMPLATE, apps=apps, total=total,
                                   interviews=interviews, rate=rate)

@app.route("/add", methods=["POST"])
def add():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO applications (company, position, status, link, notes) VALUES (%s, %s, %s, %s, %s)",
        (request.form["company"], request.form["position"],
         request.form["status"], request.form.get("link"), request.form.get("notes"))
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/update/<int:app_id>", methods=["POST"])
def update(app_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE applications SET status = %s WHERE id = %s",
                (request.form["status"], app_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return {"status": "ok"}, 200
    except Exception:
        return {"status": "error"}, 503

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("APP_PORT", 5000)))
