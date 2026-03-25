import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from datetime import datetime
from groq import Groq

client = Groq(api_key="GROQ_API_KEY")

# ── Colors ────────────────────────────────────────────────────────────────────
DARK_BG   = "#0d1117"
PANEL_BG  = "#161b22"
CARD_BG   = "#1c2128"
BORDER    = "#30363d"
TEXT_MAIN = "#e6edf3"
TEXT_DIM  = "#8b949e"
ACCENT    = "#58a6ff"
GREEN     = "#3fb950"
PURPLE    = "#bc8cff"
ORANGE    = "#ffa657"
RED       = "#ff7b72"
YELLOW    = "#e3b341"
COLORS    = [ACCENT, GREEN, PURPLE, ORANGE, RED, YELLOW, "#79c0ff"]
ICONS     = ["📘", "⚙️", "🌐", "💡", "🔬", "🚀", "🎯"]

A4_W = 794
A4_H = 1123


# ── LLM ───────────────────────────────────────────────────────────────────────
def generate_doc(topic, author, designation, experience, email, date):
    system = """You are a professional document writer. Return ONLY valid JSON, no markdown, no extra text.
The JSON must have:
{
  "title": "...",
  "subtitle": "...",
  "abstract": "4-5 sentence abstract",
  "keywords": ["kw1","kw2","kw3","kw4","kw5"],
  "sections": [
    {"heading": "...", "content": "at least 200 words of detailed content"}
  ],
  "conclusion": "at least 120 words",
  "references": [
    {"label": "Author, Title, Journal, Year", "url": "https://..."}
  ]
}
Include exactly 6 sections. Each section must have at least 200 words. No conclusion inside sections."""

    prompt = f"""Topic: {topic}
Author: {author}
Designation: {designation}
Experience: {experience}
Email: {email}
Date: {date}
Generate a comprehensive, detailed, professional academic document."""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": prompt}],
        max_tokens=4000
    )
    raw = r.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Helpers ───────────────────────────────────────────────────────────────────
def selectable(parent, text, font, fg, bg, pady=(0, 4), padx=0, center=False, height=None):
    if not text or not text.strip():
        return
    if height is None:
        height = max(1, len(text) // 88 + text.count("\n") + 1)
    t = tk.Text(parent, font=font, fg=fg, bg=bg,
                relief="flat", bd=0, wrap="word", height=height,
                cursor="xterm", selectbackground="#264f78",
                selectforeground="white", exportselection=True,
                highlightthickness=0)
    t.insert("1.0", text)
    if center:
        t.tag_configure("c", justify="center")
        t.tag_add("c", "1.0", "end")
    t.configure(state="disabled")
    t.pack(fill="x", pady=pady, padx=padx)
    return t


def divider(parent, bg, color, thickness=1):
    tk.Frame(parent, bg=color, height=thickness).pack(fill="x", pady=6)


# ── App ───────────────────────────────────────────────────────────────────────
class DocApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✦ AI Document Studio")
        self.configure(bg=DARK_BG)
        self.geometry("1280x900")
        self.resizable(True, True)
        self.doc_data = None
        self._build_ui()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # topbar
        top = tk.Frame(self, bg=PANEL_BG, height=50)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="  ✦  AI Document Studio",
                 bg=PANEL_BG, fg=TEXT_MAIN,
                 font=("Helvetica", 15, "bold")).pack(side="left", padx=16, pady=12)
        tk.Label(top, text="Groq  •  llama-3.3-70b-versatile",
                 bg=PANEL_BG, fg=TEXT_DIM,
                 font=("Helvetica", 9)).pack(side="right", padx=16)

        body = tk.Frame(self, bg=DARK_BG)
        body.pack(fill="both", expand=True)

        # sidebar
        side = tk.Frame(body, bg=PANEL_BG, width=290)
        side.pack(side="left", fill="y", padx=(12, 6), pady=12)
        side.pack_propagate(False)

        self._lbl(side, "📄  Topic")
        self.topic_var = self._ent(side, "Large Language Models")
        self._lbl(side, "👤  Author Name")
        self.author_var = self._ent(side, "John Doe")
        self._lbl(side, "🏷️  Designation")
        self.desig_var = self._ent(side, "Senior Researcher")
        self._lbl(side, "🏢  Organization")
        self.org_var = self._ent(side, "MIT")
        self._lbl(side, "📅  Experience")
        self.exp_var = self._ent(side, "10+ years in NLP & AI")
        self._lbl(side, "✉️  Email")
        self.email_var = self._ent(side, "john.doe@mit.edu")

        tk.Frame(side, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)

        self.gen_btn = tk.Button(
            side, text="⚡  Generate Document",
            bg=ACCENT, fg=DARK_BG, font=("Helvetica", 11, "bold"),
            relief="flat", cursor="hand2", pady=11, bd=0,
            activebackground="#79c0ff",
            command=self._start)
        self.gen_btn.pack(fill="x", padx=14, pady=(0, 6))

        for txt, cmd, color in [
            ("📋  Copy All",    self._copy_all, CARD_BG),
            ("💾  Export TXT",  self._export,   CARD_BG),
            ("🗑️  Clear",       self._clear,    CARD_BG),
        ]:
            tk.Button(side, text=txt, bg=color, fg=TEXT_MAIN,
                      font=("Helvetica", 10), relief="flat",
                      cursor="hand2", pady=8, bd=0,
                      command=cmd).pack(fill="x", padx=14, pady=3)

        tk.Frame(side, bg=BORDER, height=1).pack(fill="x", padx=14, pady=10)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(side, textvariable=self.status_var,
                 bg=PANEL_BG, fg=TEXT_DIM,
                 font=("Helvetica", 8), wraplength=240,
                 justify="left").pack(padx=14, anchor="w")
        self.progress = ttk.Progressbar(side, mode="indeterminate")
        self.progress.pack(fill="x", padx=14, pady=6)

        # ── A4 canvas area ────────────────────────────────────────────────────
        right = tk.Frame(body, bg="#2a2a3e")
        right.pack(side="right", fill="both", expand=True, padx=(6, 12), pady=12)

        tk.Label(right,
                 text="Document Preview  •  Select text with mouse  •  Cmd+C to copy",
                 bg="#2a2a3e", fg="#505070",
                 font=("Helvetica", 8)).pack(anchor="w", padx=8, pady=(4, 2))

        self.canvas = tk.Canvas(right, bg="#2a2a3e", highlightthickness=0)
        sb = ttk.Scrollbar(right, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.doc_frame = tk.Frame(self.canvas, bg="#2a2a3e")
        self.cw = self.canvas.create_window((0, 0), window=self.doc_frame, anchor="nw")
        self.doc_frame.bind("<Configure>",
                            lambda _: self.canvas.configure(
                                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self.cw, width=e.width))
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(
                             -1 if e.delta > 0 else 1, "units"))

        self._show_welcome()

    def _lbl(self, p, t):
        tk.Label(p, text=t, bg=PANEL_BG, fg=TEXT_DIM,
                 font=("Helvetica", 9, "bold")).pack(anchor="w", padx=14, pady=(10, 2))

    def _ent(self, p, default):
        var = tk.StringVar(value=default)
        f = tk.Frame(p, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", padx=14)
        tk.Entry(f, textvariable=var, bg=CARD_BG, fg=TEXT_MAIN,
                 insertbackground=TEXT_MAIN, relief="flat",
                 font=("Helvetica", 10), bd=0).pack(fill="x", padx=8, ipady=6)
        return var

    # ── Welcome ───────────────────────────────────────────────────────────────
    def _show_welcome(self):
        for w in self.doc_frame.winfo_children():
            w.destroy()
        f = tk.Frame(self.doc_frame, bg="#2a2a3e")
        f.pack(expand=True, fill="both", pady=120)
        tk.Label(f, text="✦", bg="#2a2a3e", fg=ACCENT,
                 font=("Helvetica", 52)).pack()
        tk.Label(f, text="AI Document Studio",
                 bg="#2a2a3e", fg=TEXT_MAIN,
                 font=("Helvetica", 22, "bold")).pack(pady=(8, 6))
        tk.Label(f, text="Fill in the details and click ⚡ Generate",
                 bg="#2a2a3e", fg=TEXT_DIM,
                 font=("Helvetica", 11)).pack()

    # ── Generate ──────────────────────────────────────────────────────────────
    def _start(self):
        topic = self.topic_var.get().strip()
        if not topic:
            messagebox.showwarning("Missing", "Please enter a topic.")
            return
        self.gen_btn.configure(state="disabled")
        self.progress.start(8)
        self.status_var.set("⚡ Generating via LLM…")
        author = self.author_var.get().strip()
        desig  = self.desig_var.get().strip()
        org    = self.org_var.get().strip()
        exp    = self.exp_var.get().strip()
        email  = self.email_var.get().strip()
        date   = datetime.now().strftime("%B %d, %Y")
        threading.Thread(
            target=self._thread,
            args=(topic, author, desig, org, exp, email, date),
            daemon=True).start()

    def _thread(self, topic, author, desig, org, exp, email, date):
        try:
            data = generate_doc(topic, author, f"{desig}, {org}", exp, email, date)
            self.doc_data = {"data": data, "author": author, "desig": desig,
                             "org": org, "exp": exp, "email": email, "date": date}
            self.after(0, lambda: self._render(data, author, desig, org, exp, email, date))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, self._done)

    def _done(self):
        self.progress.stop()
        self.gen_btn.configure(state="normal")
        self.status_var.set("Done ✓  —  select text & Cmd+C to copy")

    # ── Render ────────────────────────────────────────────────────────────────
    def _render(self, data, author, desig, org, exp, email, date):
        for w in self.doc_frame.winfo_children():
            w.destroy()

        self._render_cover(data, author, desig, org, exp, email, date)

        sections = data.get("sections", [])
        # 2 sections per page
        for i in range(0, len(sections), 2):
            chunk = sections[i:i+2]
            self._render_content_page(chunk, i // 2 + 2, i)

        self._render_conclusion_page(data, len(sections) // 2 + 2)
        self.canvas.yview_moveto(0)

    # ── Cover Page ────────────────────────────────────────────────────────────
    def _render_cover(self, data, author, desig, org, exp, email, date):
        page = self._new_page()

        # top accent band
        tk.Frame(page, bg=ACCENT, height=10).pack(fill="x")

        body = tk.Frame(page, bg="white")
        body.pack(fill="both", expand=True, padx=70, pady=50)

        # title
        selectable(body, data.get("title", "").upper(),
                   font=("Helvetica", 24, "bold"), fg="#0d1117", bg="white",
                   pady=(30, 6), center=True)

        tk.Frame(body, bg=ACCENT, height=3, width=100).pack(pady=4)

        selectable(body, data.get("subtitle", ""),
                   font=("Helvetica", 12, "italic"), fg="#444444", bg="white",
                   pady=(4, 30), center=True)

        # abstract box
        ab = tk.Frame(body, bg="#f0f4ff",
                      highlightbackground="#c0d0ff", highlightthickness=1)
        ab.pack(fill="x", pady=(0, 20))
        tk.Label(ab, text="  ABSTRACT", bg="#f0f4ff", fg=ACCENT,
                 font=("Helvetica", 9, "bold")).pack(anchor="w", padx=14, pady=(10, 4))
        selectable(ab, data.get("abstract", ""),
                   font=("Georgia", 10), fg="#222222", bg="#f0f4ff",
                   pady=(0, 12), padx=14)

        # keywords
        kws = data.get("keywords", [])
        if kws:
            kf = tk.Frame(body, bg="white")
            kf.pack(anchor="w", pady=(0, 20))
            tk.Label(kf, text="Keywords: ", bg="white", fg="#555555",
                     font=("Helvetica", 9, "bold")).pack(side="left")
            for i, kw in enumerate(kws):
                c = COLORS[i % len(COLORS)]
                tk.Label(kf, text=f" {kw} ", bg=c, fg="white",
                         font=("Helvetica", 8, "bold"),
                         padx=5, pady=2).pack(side="left", padx=3)

        # divider
        tk.Frame(body, bg="#dddddd", height=1).pack(fill="x", pady=(10, 20))

        # author card
        ac = tk.Frame(body, bg="#f9f9f9",
                      highlightbackground="#dddddd", highlightthickness=1)
        ac.pack(fill="x")
        al = tk.Frame(ac, bg=ACCENT, width=5)
        al.pack(side="left", fill="y")
        ai = tk.Frame(ac, bg="#f9f9f9")
        ai.pack(side="left", fill="both", expand=True, padx=16, pady=14)

        tk.Label(ai, text="👤  " + author,
                 bg="#f9f9f9", fg="#0d1117",
                 font=("Helvetica", 13, "bold")).pack(anchor="w")
        tk.Label(ai, text=f"🏷️  {desig}  •  🏢  {org}",
                 bg="#f9f9f9", fg="#444444",
                 font=("Helvetica", 10)).pack(anchor="w", pady=(4, 2))
        tk.Label(ai, text=f"⏱️  Experience: {exp}",
                 bg="#f9f9f9", fg="#555555",
                 font=("Helvetica", 10)).pack(anchor="w", pady=2)
        tk.Label(ai, text=f"✉️  {email}",
                 bg="#f9f9f9", fg=ACCENT,
                 font=("Helvetica", 10)).pack(anchor="w", pady=2)
        tk.Label(ai, text=f"📅  {date}",
                 bg="#f9f9f9", fg="#555555",
                 font=("Helvetica", 10)).pack(anchor="w", pady=(2, 0))

        # bottom accent
        tk.Frame(page, bg=ACCENT, height=5).pack(fill="x", side="bottom")

    # ── Content Page ──────────────────────────────────────────────────────────
    def _render_content_page(self, sections, page_num, offset):
        page = self._new_page()
        tk.Frame(page, bg=ACCENT, height=5).pack(fill="x")

        body = tk.Frame(page, bg="white")
        body.pack(fill="both", expand=True, padx=60, pady=40)

        for j, sec in enumerate(sections):
            color = COLORS[(offset + j) % len(COLORS)]
            icon  = ICONS[(offset + j) % len(ICONS)]

            # heading button-style
            hf = tk.Frame(body, bg=color)
            hf.pack(fill="x", pady=(16 if j > 0 else 0, 8))
            tk.Label(hf, text=f"  {icon}  {sec.get('heading','').upper()}  ",
                     bg=color, fg="white",
                     font=("Helvetica", 11, "bold"),
                     pady=9).pack(anchor="w")

            selectable(body, sec.get("content", ""),
                       font=("Georgia", 11), fg="#1a1a1a", bg="white",
                       pady=(0, 10))

            if j < len(sections) - 1:
                tk.Frame(body, bg="#eeeeee", height=1).pack(fill="x", pady=8)

        # page number
        pf = tk.Frame(page, bg="white")
        pf.pack(fill="x", side="bottom")
        tk.Frame(pf, bg=ACCENT, height=3).pack(fill="x")
        tk.Label(pf, text=f"— {page_num} —",
                 bg="white", fg="#aaaaaa",
                 font=("Georgia", 9)).pack(pady=5)

    # ── Conclusion Page ───────────────────────────────────────────────────────
    def _render_conclusion_page(self, data, page_num):
        page = self._new_page()
        tk.Frame(page, bg=GREEN, height=5).pack(fill="x")

        body = tk.Frame(page, bg="white")
        body.pack(fill="both", expand=True, padx=60, pady=40)

        hf = tk.Frame(body, bg=GREEN)
        hf.pack(fill="x", pady=(0, 12))
        tk.Label(hf, text="  ✅  CONCLUSION  ",
                 bg=GREEN, fg="white",
                 font=("Helvetica", 11, "bold"), pady=9).pack(anchor="w")

        selectable(body, data.get("conclusion", ""),
                   font=("Georgia", 11), fg="#1a1a1a", bg="white",
                   pady=(0, 20))

        # references
        refs = data.get("references", [])
        if refs:
            tk.Frame(body, bg="#dddddd", height=1).pack(fill="x", pady=(10, 14))
            tk.Label(body, text="🔗  References",
                     bg="white", fg=PURPLE,
                     font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 8))
            for ref in refs:
                rf = tk.Frame(body, bg="white")
                rf.pack(fill="x", pady=3)
                tk.Label(rf, text="→ ", bg="white", fg=PURPLE,
                         font=("Helvetica", 10)).pack(side="left")
                t = tk.Text(rf, bg="white", fg=ACCENT,
                            font=("Helvetica", 10),
                            relief="flat", bd=0, height=1,
                            cursor="xterm", exportselection=True,
                            highlightthickness=0, wrap="none")
                t.insert("1.0", ref.get("label", "") + "  —  " + ref.get("url", ""))
                t.configure(state="disabled")
                t.pack(side="left", fill="x", expand=True)

        # footer
        pf = tk.Frame(page, bg="white")
        pf.pack(fill="x", side="bottom")
        tk.Frame(pf, bg=GREEN, height=3).pack(fill="x")
        tk.Label(pf,
                 text=f"— {page_num} —   •   Generated by AI Document Studio  •  Groq llama-3.3-70b",
                 bg="white", fg="#aaaaaa",
                 font=("Georgia", 8)).pack(pady=5)

    # ── A4 page frame ─────────────────────────────────────────────────────────
    def _new_page(self):
        shadow = tk.Frame(self.doc_frame, bg="#111111")
        shadow.pack(pady=(16, 0), padx=20)
        page = tk.Frame(shadow, bg="white", width=A4_W,
                        highlightbackground="#cccccc", highlightthickness=0)
        page.pack(padx=3, pady=3)
        page.pack_propagate(False)
        # set min height
        page.configure(height=A4_H)
        return page

    # ── Actions ───────────────────────────────────────────────────────────────
    def _clear(self):
        self.doc_data = None
        self._show_welcome()
        self.status_var.set("Cleared")

    def _copy_all(self):
        if not self.doc_data:
            messagebox.showinfo("Nothing", "Generate a document first.")
            return
        d = self.doc_data["data"]
        lines = [d["title"], d.get("subtitle", ""), "",
                 "ABSTRACT", d.get("abstract", ""), "",
                 "Author: " + self.doc_data["author"],
                 "Designation: " + self.doc_data["desig"],
                 "Organization: " + self.doc_data["org"],
                 "Experience: " + self.doc_data["exp"],
                 "Email: " + self.doc_data["email"],
                 "Date: " + self.doc_data["date"], "", "-" * 60, ""]
        for sec in d.get("sections", []):
            lines += [sec["heading"], sec["content"], ""]
        lines += ["CONCLUSION", d.get("conclusion", "")]
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.status_var.set("Copied to clipboard ✓")

    def _export(self):
        if not self.doc_data:
            messagebox.showinfo("Nothing", "Generate a document first.")
            return
        d = self.doc_data["data"]
        lines = [d["title"], "=" * 60, d.get("subtitle", ""), "",
                 "ABSTRACT", d.get("abstract", ""), "",
                 "Author: " + self.doc_data["author"],
                 "Designation: " + self.doc_data["desig"],
                 "Organization: " + self.doc_data["org"],
                 "Experience: " + self.doc_data["exp"],
                 "Email: " + self.doc_data["email"],
                 "Date: " + self.doc_data["date"], "", "-" * 60, ""]
        for sec in d.get("sections", []):
            lines += [sec["heading"], "-" * len(sec["heading"]), sec["content"], ""]
        lines += ["CONCLUSION", "-" * 10, d.get("conclusion", "")]
        path = f"/Users/baishalinisahu/{d['title'][:40].replace(' ', '_')}.txt"
        with open(path, "w") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Exported", f"Saved:\n{path}")


if __name__ == "__main__":
    app = DocApp()
    app.mainloop()
