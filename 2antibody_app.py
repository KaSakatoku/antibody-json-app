import streamlit as st
import json
from github import Github
import pandas as pd

# GitHubリポジトリ名（あなたのリポジトリに書き換える）
REPO_NAME = "KaSakatoku/antibody-json-app"  # ← ここだけ変更点
FILE_PATH = "rack.json"

# GitHubトークンで認証
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo(REPO_NAME)
file = repo.get_contents(FILE_PATH)
rack = json.loads(file.decoded_content)

# ラックの定義
ROWS, COLS = 8, 12
POSITIONS = [f"{chr(65+i)}{j+1}" for i in range(ROWS) for j in range(COLS)]

# 未定義の位置を初期化
for pos in POSITIONS:
    if pos not in rack:
        rack[pos] = {"name": "", "clone": "", "fluor": ""}

# UI
st.title("🧪 抗体ラック管理アプリ（GitHub JSON保存）")

search = st.text_input("🔍 抗体名・クローン・蛍光色素で検索", "")

for i in range(ROWS):
    cols = st.columns(COLS)
    for j in range(COLS):
        pos = f"{chr(65+i)}{j+1}"
        ab = rack[pos]
        label = ab["name"] if ab["name"] else pos
        highlight = search.lower() in f"{ab['name']} {ab['clone']} {ab['fluor']}".lower()
        if cols[j].button(label, key=pos, use_container_width=True):
            st.session_state.selected = pos
        if highlight:
            cols[j].markdown("<div style='height:5px;background-color:lime;'></div>", unsafe_allow_html=True)

# 編集フォーム
if "selected" in st.session_state:
    pos = st.session_state.selected
    ab = rack[pos]
    st.subheader(f"位置: {pos}")
    ab["name"] = st.text_input("抗体名", ab["name"])
    ab["clone"] = st.text_input("クローン", ab["clone"])
    ab["fluor"] = st.text_input("蛍光色素", ab["fluor"])
    if st.button("保存"):
        rack[pos] = ab

        # 🔁 最新のshaを取得し直す
        file = repo.get_contents(FILE_PATH)

        repo.update_file(
            path=FILE_PATH,
            message=f"update {pos}",
            content=json.dumps(rack, indent=2),
            sha=file.sha
        )
        st.success("保存しました。ページを更新して反映を確認してください。")
