# llm_server.py
import ray
from ray import serve
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

ray.init(address="auto")  # Headノードで実行
serve.start(detached=True)

app = FastAPI()

class Prompt(BaseModel):
    text: str
    reset: bool = False  # オプションで履歴リセット

@serve.deployment(route_prefix="/generate")
class LLMService:
    def __init__(self):
        model_name = "deepseek-ai/deepseek-coder-6.7b-instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.history = [
            {"role": "system", "content": "あなたはコード実装を支援する熟練エンジニアです。ユーザーの自作ライブラリや目的に応じて、Pythonコードを提案・修正・補足してください。"}
        ]  # 履歴保持
        self.max_history = 10  # 最大10ラウンド（user+assistant）

    async def __call__(self, request):
        data = await request.json()
        prompt = data.get("text", "")
        reset = data.get("reset", False)

        if reset:
            self.history = []
            return {"response": "Context reset."}

        # ユーザー入力追加
        self.history.append({"role": "user", "content": prompt})

        # 過去履歴をトークンに整形
        messages = self.history[-self.max_history:]  # 最大10ターンまで
        inputs = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_special_tokens=True
        ).to(self.model.device)

        outputs = self.model.generate(
            inputs,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.7
        )
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # アシスタント応答を履歴に追加
        self.history.append({"role": "assistant", "content": result})

        # 履歴を最大max_historyラウンドに制限
        if len(self.history) > 2 * self.max_history:
            self.history = self.history[-2 * self.max_history:]

        return {"response": result}

LLMService.deploy()

@serve.ingress(app)
class Entry:
    @app.post("/generate")
    async def generate(self, prompt: Prompt):
        handle = serve.get_deployment("LLMService").get_handle()
        response = await handle.__call__.remote({"text": prompt.text, "reset": prompt.reset})
        return response

