# CiteCheck 实现计划

范围以 [PROPOSAL.md](PROPOSAL.md) 为准。不要额外增加表格解析、公式检索、多轮对话、用户账号或多用户网站。主要功能和实验做完之后，如果还有时间，再考虑表格、公式和记住前面的对话。

## 做完后用户能做什么

网页上传一篇或多篇论文 PDF，输入一个问题。系统返回短答案、支撑原文、每句的章节和页码。没有依据的句子删掉或标成不确定。

```text
PDF + question
  -> parse and section chunk
  -> planner
  -> BM25 + embedding
  -> draft answer
  -> LLM claim check
  -> cited answer
```

## 代码怎么拆

逻辑和网页分开。评测直接调用同一套 workflow。建议文件：

- `ingest.py`：用 PyMuPDF 抽正文，保留 section 和 page，按章节切块。
- `retrieve.py`：BM25 与 embedding 两路检索，合并排序。Embedding 模型可以更换，索引存在本地。
- `agent.py`：planner 决定检索一次还是拆成子问题。同一个可配置语言模型写草稿，再把每个 claim 和检索到的段落交给它，判断支持或不支持。这个判断不用检索分数。
- `evaluate.py`：跑 B1、B2、B3 和完整系统，写出指标。
- `app.py`：薄网页，只负责上传、提问和展示。可以用 Streamlit，或一个很小的 FastAPI 页面。
- `.env`：放 API key。提交 `.env.example`，不要提交真实 key。
- `README.md`：在实现过程中补上安装、依赖、配置、示例输入和复现命令。

PDF 库、embedding 模型和语言模型是现成工具。自己要做的是带页码的切块、按问题复杂度分步检索，以及返回答案前的逐句检查。

## 评测

- QASPER 子集：答案准确率或 token F1，证据段落有没有检索到。不评页码。
- SciFact 子集：把 claim 和已标注摘要交给 verifier，只看支持或反驳判断。不评页码。
- 自建约 30 题：事实题、跨章节题、少量两篇比较。引用正确要求章节和页码都与标准证据一致。
- 对比：B1 只提示；B2 在同一批 chunk 上做单次 RAG；B3 有 planner 和混合检索，没有 verifier；完整系统再加上 verifier。消融再去掉 planner，或只用 embedding。
- 同时记录步数、延迟和 token 费用。

指标定义：

- 引用算对：章节和页码都与标准证据一致。
- 证据召回：标准段落有没有被检索到。
- 无依据比例：被标成不确定，或没有对上段落的句子占全部句子的比例。
- 任务成功：系统给出了答案，并且留下来的每一句都有引用。

## 周计划

- 10 月 10–16 日：解析、切块、BM25、B1 和 B2。
- 10 月 17–23 日：embedding、混合排序、planner、LLM verifier。
- 10 月 24–30 日：写约 30 道自建题，跑主要对比。
- 11 月 1–8 日：消融和错误分析。
- 11 月 9–15 日：幻灯片、演示页、本机复现脚本。Slides 截止 11 月 15 日 23:59。
- 11 月 16–27 日：课堂演示是 11 月 20 日和 27 日。这段时间改演示里暴露的问题，并开始写报告。
- 11 月 23–29 日：定稿报告、代码和 README。最终截止 11 月 29 日 23:59。

## 给实现 agent 的顺序

1. 建立 Python 项目、`requirements.txt`、`.env.example` 和 `.gitignore`。
2. 实现 PDF 解析、按章节切块和 BM25，并让 B1、B2 能对一篇示例 PDF 跑通。
3. 加入 embedding、planner 和 LLM verifier。
4. 接上 QASPER 子集、SciFact 子集和自建题，输出对比结果。
5. 做演示页，并补全 README 里的复现步骤。
