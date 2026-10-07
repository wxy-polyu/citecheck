# CiteCheck

中文 | [English](README.en.md)

上传一篇或多篇论文 PDF 并提问。CiteCheck 返回答案、支撑原文，以及每句对应的章节和页码。没有原文支撑的句子会被标成不确定，不进入最终答案。

论文按章节切块，并保留页码。简单问题检索一次；需要连起不同章节时，先拆成子问题再检索。BM25 和 embedding 两路结果合并排序。返回答案前，模型逐句对照检索到的原文，这个判断不使用检索分数。

## 安装

需要 Python 3.12。

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
```

在 `.env` 里填写 `LLM_BASE_URL`、`LLM_API_KEY` 和 `LLM_MODEL`。接口兼容 OpenAI，默认示例是 DeepSeek。API key 只放在本机 `.env`。

```bash
python -m citecheck
```

这条命令只检查配置是否读到，不打印 key，也不调用模型。第一次检索会下载 embedding 模型 `all-MiniLM-L6-v2`。

## 使用

生成示例论文并提问：

```bash
python -m citecheck.sample_docs
python -m citecheck.ask \
  --pdf examples/widgetnet.pdf \
  --question "What accuracy does WidgetNet reach on Widget-100?"
```

两篇一起问：

```bash
python -m citecheck.ask \
  --pdf examples/widgetnet.pdf \
  --pdf examples/widgetnet_lite.pdf \
  --question "Do WidgetNet and WidgetNet-Lite report the same accuracy on Widget-100?"
```

`--system` 可选 `b1`、`b2`、`b3`、`full`，以及 `no_planner`、`embedding_only`、`no_verifier`。

演示页：

```bash
streamlit run app.py
```

可以上传 PDF，也可以使用示例论文。页面显示答案、每一句的核对结果、章节页码和检索到的段落。

## 对照

- B1：只把问题交给模型，不读论文。
- B2：混合检索一次后作答，不规划，也不逐句检查。
- B3：按问题规划检索，不逐句检查。
- CiteCheck：在 B3 之后逐句检查。支持的句子保留引用，其余标成不确定。

## 评测

```bash
python -m citecheck.evaluate --dataset custom --systems b1,b2,b3,full
python -m citecheck.evaluate --dataset qasper --limit 20 --systems b1,b2,b3,full
python -m citecheck.evaluate --dataset scifact --limit 50
python -m unittest discover -s tests -v
```

结果写到 `data/results/latest.json`。QASPER 和 SciFact 会下载到 `data/`，该目录不提交。QASPER 看答案 token F1 和证据召回，不评页码。SciFact 只判断摘要是支持还是反驳。自建题在 `examples/custom_questions.json`，引用算对需要章节和页码都一致。示例论文是合成的，可以按同一格式换成其他论文。
