# llm_client.py
import requests
import argparse
import re

LLM_SERVER = "http://<HEAD_NODE_IP>:8000/generate"  # ← 必要に応じて変更

def extract_code_blocks(text):
    # ```python ... ``` を抽出
    return re.findall(r"```(?:python)?\\n(.*?)```", text, re.DOTALL)

def confirm_execute(code, block_num):
    print(f"\n▶ Pythonコード（Block {block_num}）:\n{code}")
    response = input("⚠️ このコードを実行しますか？ [y/N]: ")
    return response.lower().strip() == "y"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", help="プロンプト内容")
    parser.add_argument("--reset", action="store_true", help="履歴をリセット")
    parser.add_argument("--force", action="store_true", help="確認なしで自動実行")
    args = parser.parse_args()

    if args.reset:
        requests.post(LLM_SERVER, json={"text": "", "reset": True})
        print("🧹 文脈履歴をリセットしました。")
        return

    if not args.text:
        print("⛔ プロンプトを入力してください。")
        return

    res = requests.post(LLM_SERVER, json={"text": args.text})
    output = res.json()["response"]
    print("🧠 LLM応答:\n", output)

    code_blocks = extract_code_blocks(output)
    if code_blocks:
        for i, code in enumerate(code_blocks, start=1):
            if args.force or confirm_execute(code, i):
                try:
                    exec(code, globals())
                except Exception as e:
                    print(f"⚠️ 実行中にエラーが発生しました: {e}")
            else:
                print(f"🚫 Block {i} はスキップされました。")
    else:
        print("💬 コードブロックは見つかりませんでした。")

if __name__ == "__main__":
    main()


