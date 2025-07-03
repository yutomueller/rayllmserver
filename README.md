# DeepSeek-Coder 6.7B LLM Server (Ray Serve)

本構成は、DeepSeek-Coder 6.7B Instruct モデルを使用し、Ray Serve によって高速な分散LLM推論APIを構築するものです。Pythonの自作ライブラリへの質問応答やコード生成を目的とし、CLIからの指示入力→コード生成→実行までを一貫して行う設計です。

---

## ✅ 構成概要

* LLM: DeepSeek-Coder 6.7B Instruct（HuggingFaceモデル）
* API: FastAPI + Ray Serve による高性能エンドポイント
* 文脈保持: 最大10ターンまでの履歴をサーバー側で保持
* クライアント: CLIからAPIにプロンプトを送信・コード生成結果を自動実行
* 分散性: Rayクラスタ構成済。ワークPCは資源提供可能。

---

## 📦 インストール

```bash
pip install ray[serve]==2.44.1 fastapi uvicorn transformers torch accelerate pydantic requests
```

※ PyTorch は GPU 環境に応じてインストールしてください：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## 🚀 起動手順

### ヘッドノード（中央LLMサーバー）

```bash
python llm_server.py
```

### クライアントPC（任意）

```bash
python llm_client.py "sklearnを使って異常を検出するコードを書いて"
```

### 文脈をリセットする

```bash
python llm_client.py --reset
```

### 実行確認なしで自動実行（危険）

```bash
python llm_client.py --force "関数をグラフ描画するコードを生成して"
```

---

## ⚙️ 分散処理


* 現状、LLM推論は中央ノードでのみ行います（推論分散は未実装）
* 並列前処理、Embedding生成、RAG、探索系処理などには分散計算が可能です

---

## 📜 ライセンス一覧

| ライブラリ名              | ライセンス      | 商用利用 |
| ------------------- | ---------- | ---- |
| ray / ray\[serve]   | Apache 2.0 | ✅ OK |
| fastapi             | MIT        | ✅ OK |
| transformers        | Apache 2.0 | ✅ OK |
| torch (PyTorch)     | BSD + NCSA | ✅ OK |
| accelerate          | Apache 2.0 | ✅ OK |
| pydantic            | MIT        | ✅ OK |
| requests            | Apache 2.0 | ✅ OK |
| DeepSeek-Coder 6.7B | Apache 2.0 | ✅ OK |

---

## 🔍 GPU使用確認

サーバー側で以下の確認が可能：

### nvidia-smi

```bash
watch -n 1 nvidia-smi
```

### Pythonコード

```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

---

## 📌 注意事項

* 実行されるコードは `exec()` によって直接実行されます。信頼できる環境でご使用ください。
* 最大10ラウンド分の会話履歴が保持され、それ以上は自動で古い履歴が削除されます。
* CLIから送信されたプロンプトがPythonコードを含む場合、自動抽出され `exec()` によって即時実行されます（--force で強制実行）。

---

## ✨ 今後の拡張候補

* 軽量LLM（GGUF）をワークPCに配置し、推論の分散化
* 文書検索や要約タスクをRay Taskで並列処理
* LangChainとの連携によるRAG構成
* DeepSpeed / FSDPによるマルチGPU推論

---

## 👤 作者

* 使用モデル: DeepSeek-Coder 6.7B Instruct
* 開発: Yuto Mueller

---
