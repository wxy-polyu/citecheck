# CiteCheck: A Verifiable Planning-and-Retrieval Agent for Research Paper Question Answering

**Course:** COMP5511 Artificial Intelligence Concepts  
**Project type:** Application project  
**Student Name:** Wang Xinyang  
**Student ID:** 26120641g

## 1. Problem and Motivation

Postgraduate students and researchers often use a large language model to understand a paper: what it contributes, how the method differs from a baseline, and which experiment supports a claim. A direct prompt can produce a fluent answer that the paper does not support. A standard retrieval-augmented generation pipeline [4] can return a locally similar passage and still miss a multi-hop question, or attach a citation that does not match the generated sentence.

This project builds CiteCheck, an agent that answers questions about a research paper and shows where each claim comes from. In the demo, the input is one or more paper PDFs and a natural-language question. The output is a short answer, the supporting evidence, a section and page citation for each claim, and a verification label that marks any claim the retrieved evidence does not support.

The intended users are postgraduate students and researchers who need to check a paper quickly and see the source of each statement. The task matters for AI agents because a useful agent has to plan what evidence is missing, retrieve it, and change the answer when the evidence is insufficient [1]. CiteCheck combines query planning, retrieval, and claim verification in one measurable workflow. It is a document agent for research papers, rather than a web-browsing agent.

## 2. Proposed Approach

CiteCheck uses the following stages.

1. **Document Parser.** Extract the paper text and keep section headings and page numbers.
2. **Section-aware Chunking.** Split the paper into passage chunks labelled with paper, section, page, and paragraph, so a later citation can point back to a specific location.
3. **Query Planner.** Decide whether the question can be answered from one passage or should be split into sub-questions. Factual questions take one retrieval step. Questions that connect a method with an experimental result are decomposed before retrieval. The planner chooses the next retrieval step from the question and the evidence already found, following the idea of interleaving reasoning and actions [5].
4. **Hybrid Retriever.** Retrieve candidate evidence with BM25 and with embedding similarity, then merge the two rankings. BM25 favours exact technical terms. Embeddings favour passages that use different wording for a similar idea.
5. **Evidence Verifier.** Split the draft answer into atomic claims. For each claim, the same language model is prompted with the claim and the retrieved passage and asked to label the passage as supporting or not supporting the claim [3]. The decision does not use the retrieval score. Unsupported claims are removed or explicitly marked as uncertain.
6. **Answer Synthesizer.** Produce the final answer with section and page citations and a short evidence trace.
7. **Demo Interface.** Provide a thin web page where a user uploads one or more PDFs, asks a question, and reads the answer, evidence, citations, and verification labels. This interface is for demonstration. The retrieval and verification logic stays in the Python workflow above.

The workflow is:

```text
Paper PDF + user question
    -> Document Parser
    -> Section-aware Chunking
    -> Query Planner
    -> Hybrid Retriever (BM25 + embeddings)
    -> Draft answer
    -> Evidence Verifier
    -> Cited answer + verification labels
```

The implementation will be in Python. PDF parsing will use an existing parser such as PyMuPDF. Lexical retrieval will use BM25. Dense retrieval will use a pretrained embedding model through a configurable interface, with chunks stored in a local index. Generation and verification will use a configurable language-model interface, so either an API model or a local model can be used. These models and libraries are external resources. They are not the contribution of this project.

The contribution is the workflow that connects three design choices: section-aware chunking that preserves citation locations, planning that retrieves once or in steps according to question complexity, and a verifier that checks each claim against retrieved evidence before the answer is returned. A single prompt does not retrieve evidence. A single-pass RAG pipeline [4] retrieves once and does not test whether every sentence in the answer is supported. CiteCheck uses the verifier result to reject or qualify unsupported claims, which is the behaviour needed when an answer must stay faithful to a paper.

## 3. Implementation and Evaluation Plan

Development is organised into document ingestion, retrieval, the agent workflow, and evaluation scripts. The submitted repository will contain the source code, a README with setup, dependencies, configuration, example inputs, and the commands that reproduce the main results.

**Data.** Evaluation will use three sources.

- A subset of QASPER [2], which provides questions, answers, and evidence paragraphs for research papers. It is used for answer accuracy and evidence recall. Its evidence labels are paragraphs rather than page numbers, so section and page citation is not scored on this subset.
- A subset of SciFact [3], which labels whether an abstract supports or refutes a scientific claim. Each claim is given to the verifier together with its labeled abstract. This subset tests the support label only. It is not used to score section and page citation.
- A custom set of about 30 questions written on public papers, with gold answers and gold section or page evidence. This set covers factual questions, cross-section questions, and a small number of two-paper comparisons. A two-paper question loads both papers, and the demo page can accept more than one PDF. This set is used for the citation metric.

**Baselines.**

- B1: a prompt-only language model, with no retrieval.
- B2: standard single-pass RAG [4] over the same chunks, with no planner and no verifier.
- B3: the planner and hybrid retriever, with no verifier. This baseline keeps the reasoning-and-retrieval loop [5] and removes only the verification stage.
- CiteCheck: planner, hybrid retriever, and verifier.

**Metrics.** Answer accuracy or token F1 against the gold answer; evidence recall; citation precision and recall on the custom set; unsupported-claim rate; task success rate; number of retrieval steps; latency; and token or API cost. A citation counts as correct only when both the section and the page match the gold evidence. Evidence recall asks only whether the gold passage was retrieved. The unsupported-claim rate is the fraction of answer sentences that are marked uncertain or have no matching passage. A task succeeds when the system returns an answer and every remaining sentence has a citation. Ablations remove the planner, replace hybrid retrieval with embedding-only retrieval, and remove the verifier. These comparisons show whether each added stage changes accuracy, citation quality, or the rate of unsupported claims, and whether the extra cost is justified.

**Schedule.**

- **Oct 10–16:** implement PDF ingestion, section-aware chunking, BM25, and the prompt-only and single-pass RAG baselines.
- **Oct 17–23:** add embedding retrieval, hybrid ranking, the query planner, and the evidence verifier.
- **Oct 24–30:** build the custom question set and run the main comparison.
- **Nov 1–8:** run ablations and write the error analysis.
- **Nov 9–15:** prepare the presentation slides, the demo page, and the local reproduction scripts.
- **Nov 16–27:** use the presentation period to fix failure cases found during the demo, and start the report.
- **Nov 23–29:** finalize the report, source code, README, and reproduction scripts.

## References

1. Liangbo Ning, Ziran Liang, Zhuohang Jiang, Haohao Qu, Yujuan Ding, Wenqi Fan, Xiao-yong Wei, Shanru Lin, Hui Liu, Philip S. Yu, and Qing Li. 2025. A Survey of WebAgents: Towards Next-Generation AI Agents for Web Automation with Large Foundation Models. In Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25). Association for Computing Machinery, New York, NY, USA, 6140–6150. https://doi.org/10.1145/3711896.3736555
2. Pradeep Dasigi, Kyle Lo, Iz Beltagy, Arman Cohan, Noah A. Smith, and Matt Gardner. 2021. A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers. In Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies. Association for Computational Linguistics, Online, 4599–4610. https://doi.org/10.18653/v1/2021.naacl-main.365
3. David Wadden, Shanchuan Lin, Kyle Lo, Lucy Lu Wang, Madeleine van Zuylen, Arman Cohan, and Hannaneh Hajishirzi. 2020. Fact or Fiction: Verifying Scientific Claims. In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP). Association for Computational Linguistics, Online, 7534–7550. https://doi.org/10.18653/v1/2020.emnlp-main.609
4. Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela. 2020. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In Advances in Neural Information Processing Systems, Vol. 33. Curran Associates, Inc., 9459–9474. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html
5. Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2023. ReAct: Synergizing Reasoning and Acting in Language Models. In The Eleventh International Conference on Learning Representations. https://openreview.net/forum?id=WE_vluYUL-X
