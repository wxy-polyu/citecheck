const STRINGS = {
  zh: {
    noLibrary: "尚未建立论文库",
    library: "研究资料",
    papers: "论文库",
    addPapers: "添加论文",
    history: "记录",
    session: "当前会话",
    workspaceActions: "工作台操作",
    sample: "示例论文",
    upload: "上传 PDF",
    lite: "同时加入 WidgetNet-Lite",
    chooseFiles: "选择 PDF",
    drop: "支持一次选择多篇论文",
    index: "建立索引",
    indexing: "正在索引…",
    indexed: "索引就绪",
    system: "回答方式",
    question: "向论文提问",
    shortcut: "⌘ / Ctrl + Enter 提交",
    questionPlaceholder: "例如：论文的主要贡献是什么？",
    answer: "提问",
    asking: "分析中…",
    sources: "证据来源",
    runDetails: "运行详情",
    historyHint: "仅保留在当前浏览器标签页。打开记录不会重新调用模型。",
    historyEmpty: "本次会话还没有问题。",
    libraryEmpty: "建立索引后，论文和章节会显示在这里。",
    paperSummary: (papers, pages) => `${papers} 篇论文 · ${pages} 页`,
    pageCount: (n) => `${n} 页`,
    chunkCount: (n) => `${n} 个片段`,
    page: (n) => `第 ${n} 页`,
    unknownPage: "页码未知",
    welcomeKicker: "基于原文的论文问答",
    welcomeTitle: "从证据开始，而不是从模型猜测开始。",
    welcomeCopy: "加入论文后，CiteCheck 会保留章节和页码，检索相关段落，并在返回答案前逐句核对。",
    readyTitle: "论文已经就绪。你想核对什么？",
    readyCopy: "答案中的每个事实都会尽量连接到原文位置；缺少支撑的句子会被明确标出。",
    stepParse: "读取论文",
    stepParseCopy: "保留章节与页码",
    stepRetrieve: "检索证据",
    stepRetrieveCopy: "合并关键词与语义结果",
    stepVerify: "逐句核对",
    stepVerifyCopy: "区分支持与不确定",
    examples: "可以这样问",
    resultQuestion: "问题",
    resultAnswer: "回答",
    openSources: (n) => `查看 ${n} 条证据`,
    openRun: "查看运行过程",
    claims: "逐句核对",
    claimsSummary: (supported, uncertain) => `${supported} 句有支撑 · ${uncertain} 句需注意`,
    supported: "原文支持",
    uncertain: "证据不足",
    refutes: "原文反驳",
    loadingTitle: "正在阅读相关段落",
    loadingCopy: "系统正在规划检索并核对每个句子。",
    noClaims: "没有产生可核对的句子。",
    noSources: "这次回答没有检索到证据段落。",
    noRun: "没有可显示的运行记录。",
    metricSteps: "检索步数",
    metricLatency: "耗时",
    metricTokens: "Token",
    metricCoverage: "有支撑句子",
    trace: "检索与核对",
    traceNoneTitle: "未读取论文",
    traceNone: "该系统只把问题交给模型。",
    traceSingleTitle: "单次检索",
    traceSingle: "没有使用规划器。",
    traceSearchTitle: "规划检索",
    traceSearch: "系统决定继续寻找证据。",
    traceStopTitle: "停止检索",
    traceStop: "现有证据已经足够。",
    traceVerifyTitle: "逐句核对",
    traceVerify: (supported, uncertain) => `${supported} 句有原文支撑，${uncertain} 句证据不足。`,
    traceNoVerify: "当前回答方式没有逐句核对。",
    need_pdf: "请先选择至少一篇 PDF。",
    unknown_source: "无法识别论文来源。",
    unknown_library: "请先建立论文索引。",
    unknown_system: "无法识别回答方式。",
    empty_question: "请先输入问题。",
    need_index: "先在左侧建立论文索引。",
    llm: "无法调用语言模型。",
    index_failed: "论文索引建立失败。",
    ask_failed: "本次提问未能完成。",
    network: "无法连接本机服务。",
    close: "关闭",
  },
  en: {
    noLibrary: "No paper library",
    library: "Research material",
    papers: "Paper library",
    addPapers: "Add papers",
    history: "History",
    session: "Current session",
    workspaceActions: "Workspace actions",
    sample: "Samples",
    upload: "Upload PDFs",
    lite: "Also include WidgetNet-Lite",
    chooseFiles: "Choose PDFs",
    drop: "Select one or more papers",
    index: "Build index",
    indexing: "Indexing…",
    indexed: "Index ready",
    system: "Answer mode",
    question: "Ask the papers",
    shortcut: "⌘ / Ctrl + Enter to submit",
    questionPlaceholder: "For example: What is the paper's main contribution?",
    answer: "Ask",
    asking: "Working…",
    sources: "Evidence",
    runDetails: "Run details",
    historyHint: "Kept only in this browser tab. Opening an item does not call the model again.",
    historyEmpty: "No questions in this session yet.",
    libraryEmpty: "Papers and sections appear here after indexing.",
    paperSummary: (papers, pages) => `${papers} ${papers === 1 ? "paper" : "papers"} · ${pages} ${pages === 1 ? "page" : "pages"}`,
    pageCount: (n) => (n === 1 ? "1 page" : `${n} pages`),
    chunkCount: (n) => (n === 1 ? "1 passage" : `${n} passages`),
    page: (n) => `p. ${n}`,
    unknownPage: "unknown page",
    welcomeKicker: "Paper questions grounded in evidence",
    welcomeTitle: "Start with the source, not a model's guess.",
    welcomeCopy: "Add papers and CiteCheck will preserve their sections and pages, retrieve relevant passages, and check each sentence before returning an answer.",
    readyTitle: "Your papers are ready. What do you want to verify?",
    readyCopy: "Each factual sentence is linked back to the paper where possible. Anything without enough support is called out.",
    stepParse: "Read papers",
    stepParseCopy: "Keep sections and pages",
    stepRetrieve: "Find evidence",
    stepRetrieveCopy: "Merge lexical and semantic matches",
    stepVerify: "Check sentences",
    stepVerifyCopy: "Separate support from uncertainty",
    examples: "Try asking",
    resultQuestion: "Question",
    resultAnswer: "Answer",
    openSources: (n) => `View ${n} ${n === 1 ? "source" : "sources"}`,
    openRun: "View run details",
    claims: "Sentence check",
    claimsSummary: (supported, uncertain) => `${supported} supported · ${uncertain} need attention`,
    supported: "Supported",
    uncertain: "Not enough evidence",
    refutes: "Refuted",
    loadingTitle: "Reading the relevant passages",
    loadingCopy: "CiteCheck is planning retrieval and checking each sentence.",
    noClaims: "No checkable sentences were produced.",
    noSources: "No evidence passages were retrieved for this answer.",
    noRun: "No run information is available.",
    metricSteps: "Retrieval steps",
    metricLatency: "Latency",
    metricTokens: "Tokens",
    metricCoverage: "Supported claims",
    trace: "Retrieval and checking",
    traceNoneTitle: "Paper not read",
    traceNone: "This mode sends only the question to the model.",
    traceSingleTitle: "Single retrieval",
    traceSingle: "The planner was not used.",
    traceSearchTitle: "Plan retrieval",
    traceSearch: "The system decided to find more evidence.",
    traceStopTitle: "Stop retrieval",
    traceStop: "The available evidence is sufficient.",
    traceVerifyTitle: "Check sentences",
    traceVerify: (supported, uncertain) => `${supported} supported ${supported === 1 ? "sentence" : "sentences"} and ${uncertain} without enough evidence.`,
    traceNoVerify: "This answer mode does not check each sentence.",
    need_pdf: "Choose at least one PDF first.",
    unknown_source: "The paper source is not recognized.",
    unknown_library: "Build the paper index first.",
    unknown_system: "The answer mode is not recognized.",
    empty_question: "Enter a question first.",
    need_index: "Build a paper index from the left sidebar first.",
    llm: "The language model could not be called.",
    index_failed: "The paper index could not be built.",
    ask_failed: "This question could not be completed.",
    network: "The page could not reach the local service.",
    close: "Close",
  },
};

const SYSTEMS = [
  {
    id: "full",
    group: "main",
    zh: "CiteCheck",
    en: "CiteCheck",
    hintZh: "规划检索，并在返回前逐句核对。",
    hintEn: "Plan retrieval and check every sentence before returning.",
  },
  {
    id: "b3",
    group: "main",
    zh: "B3 · 规划检索",
    en: "B3 · Planned retrieval",
    hintZh: "规划检索，但不逐句核对。",
    hintEn: "Plan retrieval without checking each sentence.",
  },
  {
    id: "b2",
    group: "main",
    zh: "B2 · 单次 RAG",
    en: "B2 · Single-pass RAG",
    hintZh: "混合检索一次后直接作答。",
    hintEn: "Answer after one hybrid retrieval.",
  },
  {
    id: "b1",
    group: "main",
    zh: "B1 · 仅模型",
    en: "B1 · Prompt only",
    hintZh: "模型不读取论文。",
    hintEn: "The model does not read the paper.",
  },
  {
    id: "no_planner",
    group: "ablation",
    zh: "消融 · 去掉规划",
    en: "Ablation · No planner",
    hintZh: "检索一次，仍逐句核对。",
    hintEn: "Retrieve once and still check each sentence.",
  },
  {
    id: "embedding_only",
    group: "ablation",
    zh: "消融 · 只用向量",
    en: "Ablation · Embedding only",
    hintZh: "不用 BM25，保留规划和核对。",
    hintEn: "Keep planning and checks without BM25.",
  },
  {
    id: "no_verifier",
    group: "ablation",
    zh: "消融 · 去掉核对",
    en: "Ablation · No verifier",
    hintZh: "规划检索，但不逐句核对。",
    hintEn: "Plan retrieval without sentence checks.",
  },
];

const EXAMPLES = [
  {
    zh: "WidgetNet 在 Widget-100 上达到了多少准确率？",
    en: "What accuracy does WidgetNet reach on Widget-100?",
  },
  {
    zh: "这篇论文的主要贡献是什么？",
    en: "What is the main contribution of this paper?",
  },
  {
    zh: "训练使用了哪个数据集，训练了多少个 epoch？",
    en: "Which dataset is used for training, and for how many epochs?",
  },
  {
    zh: "WidgetNet 和 WidgetNet-Lite 的准确率是否相同？",
    en: "Do WidgetNet and WidgetNet-Lite report the same accuracy?",
  },
];

const HISTORY_KEY = "citecheck.history";
const LIBRARY_KEY = "citecheck.library";
const savedLibrary = loadLibrary();
const state = {
  lang: initialLang(),
  source: "sample",
  library: savedLibrary,
  system: "full",
  result: null,
  asked: "",
  history: loadHistory(),
  activeId: null,
  busy: "",
  error: null,
  indexNote: "",
  activePanel: null,
  evidenceTab: "sources",
  activeEvidence: null,
  expandedPapers: new Set(savedLibrary?.papers?.map((paper) => paper.id) || []),
};

const appShell = document.getElementById("app-shell");
const questionBox = document.getElementById("question");

document.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => setLang(button.dataset.lang));
});
document.querySelectorAll("[data-source]").forEach((button) => {
  button.addEventListener("click", () => setSource(button.dataset.source));
});
document.querySelectorAll("[data-detail-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    state.evidenceTab = button.dataset.detailTab;
    state.activePanel = "detail";
    render();
  });
});
document.getElementById("files").addEventListener("change", renderFileNames);
document.getElementById("index-button").addEventListener("click", indexPapers);
document.getElementById("system-select").addEventListener("change", (event) => {
  state.system = event.target.value;
  renderSystemDescription();
});
document.getElementById("ask-form").addEventListener("submit", (event) => {
  event.preventDefault();
  askQuestion();
});
questionBox.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
    event.preventDefault();
    askQuestion();
  }
});
document.getElementById("history-open").addEventListener("click", () => openPanel("history"));
document.getElementById("history-close").addEventListener("click", closePanels);
document.getElementById("detail-close").addEventListener("click", closePanels);
document.getElementById("mobile-library-button").addEventListener("click", () => openPanel("library"));
document.getElementById("library-close").addEventListener("click", closePanels);
document.getElementById("scrim").addEventListener("click", closePanels);
document.getElementById("add-papers").addEventListener("click", focusImport);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closePanels();
});

render();

function initialLang() {
  const saved = localStorage.getItem("citecheck.lang");
  if (saved === "zh" || saved === "en") return saved;
  return (navigator.language || "").toLowerCase().startsWith("en") ? "en" : "zh";
}

function loadHistory() {
  try {
    const saved = JSON.parse(sessionStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function loadLibrary() {
  try {
    const saved = JSON.parse(sessionStorage.getItem(LIBRARY_KEY) || "null");
    if (!saved || typeof saved.id !== "string" || !Array.isArray(saved.papers)) return null;
    return saved;
  } catch {
    return null;
  }
}

function t(key, ...args) {
  const value = STRINGS[state.lang][key];
  return typeof value === "function" ? value(...args) : value;
}

function setLang(lang) {
  state.lang = lang;
  localStorage.setItem("citecheck.lang", lang);
  render();
}

function setSource(source) {
  state.source = source;
  state.error = null;
  render();
}

function openPanel(panel) {
  state.activePanel = panel;
  renderPanelState();
}

function closePanels() {
  state.activePanel = null;
  renderPanelState();
}

function focusImport() {
  if (window.matchMedia("(max-width: 860px)").matches) {
    state.activePanel = "library";
  }
  renderPanelState();
  const panel = document.getElementById("import-panel");
  panel.classList.add("is-emphasized");
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
  window.setTimeout(() => panel.classList.remove("is-emphasized"), 1100);
}

function render() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  document.querySelectorAll(".drawer-header .icon-button").forEach((button) => {
    button.setAttribute("aria-label", t("close"));
  });
  document.getElementById("library-close").setAttribute("aria-label", t("close"));
  document.getElementById("mobile-library-button").setAttribute("aria-label", t("papers"));
  document.querySelector(".topbar-actions").setAttribute("aria-label", t("workspaceActions"));
  document.getElementById("library-sidebar").setAttribute("aria-label", t("papers"));
  document.getElementById("detail-panel").setAttribute(
    "aria-label",
    `${t("sources")} / ${t("runDetails")}`,
  );
  document.getElementById("history-drawer").setAttribute("aria-label", t("history"));

  document.getElementById("lang-zh").classList.toggle("is-active", state.lang === "zh");
  document.getElementById("lang-en").classList.toggle("is-active", state.lang === "en");
  document.getElementById("lang-zh").setAttribute("aria-pressed", String(state.lang === "zh"));
  document.getElementById("lang-en").setAttribute("aria-pressed", String(state.lang === "en"));
  document.getElementById("source-sample").classList.toggle("is-active", state.source === "sample");
  document.getElementById("source-upload").classList.toggle("is-active", state.source === "upload");
  document.getElementById("lite-row").hidden = state.source !== "sample";
  document.getElementById("upload-row").hidden = state.source !== "upload";

  renderPanelState();
  renderLibrarySummary();
  renderIndexState();
  renderSystemSelect();
  renderOutline();
  renderError();
  renderStage();
  renderDetail();
  renderHistory();
}

function renderPanelState() {
  appShell.classList.toggle("library-open", state.activePanel === "library");
  appShell.classList.toggle("detail-open", state.activePanel === "detail");
  appShell.classList.toggle("history-open", state.activePanel === "history");
}

function renderLibrarySummary() {
  const node = document.getElementById("library-summary");
  if (!state.library) {
    node.textContent = t("noLibrary");
    return;
  }
  const pages = state.library.papers.reduce((total, paper) => total + paper.pages, 0);
  node.textContent = t("paperSummary", state.library.papers.length, pages);
}

function renderIndexState() {
  const indexing = state.busy === "index";
  const asking = state.busy === "ask";
  const indexButton = document.getElementById("index-button");
  const askButton = document.getElementById("ask-button");
  indexButton.disabled = indexing;
  askButton.disabled = asking;
  indexButton.textContent = t(indexing ? "indexing" : "index");
  askButton.querySelector("span").textContent = t(asking ? "asking" : "answer");
  const status = document.getElementById("index-status");
  status.textContent = state.indexNote ? t(state.indexNote) : "";
  status.classList.toggle("is-ready", state.indexNote === "indexed");
}

function renderSystemSelect() {
  const select = document.getElementById("system-select");
  select.innerHTML = "";
  const groups = [
    { key: "main", label: state.lang === "zh" ? "主要系统" : "Main systems" },
    { key: "ablation", label: state.lang === "zh" ? "消融实验" : "Ablations" },
  ];
  groups.forEach((group) => {
    const optgroup = document.createElement("optgroup");
    optgroup.label = group.label;
    SYSTEMS.filter((system) => system.group === group.key).forEach((system) => {
      const option = document.createElement("option");
      option.value = system.id;
      option.textContent = system[state.lang];
      option.selected = system.id === state.system;
      optgroup.append(option);
    });
    select.append(optgroup);
  });
  renderSystemDescription();
}

function renderSystemDescription() {
  const system = SYSTEMS.find((item) => item.id === state.system);
  document.getElementById("system-description").textContent = system
    ? system[state.lang === "zh" ? "hintZh" : "hintEn"]
    : "";
}

function renderFileNames() {
  const files = [...document.getElementById("files").files];
  document.getElementById("file-names").textContent = files.map((file) => file.name).join(" · ");
}

function renderOutline() {
  const root = document.getElementById("outline");
  root.innerHTML = "";
  if (!state.library) {
    const empty = document.createElement("p");
    empty.className = "paper-tree-empty";
    empty.textContent = t("libraryEmpty");
    root.append(empty);
    return;
  }

  state.library.papers.forEach((paper) => {
    const details = document.createElement("details");
    details.className = "paper-node";
    details.open = state.expandedPapers.has(paper.id);
    details.addEventListener("toggle", () => {
      if (details.open) state.expandedPapers.add(paper.id);
      else state.expandedPapers.delete(paper.id);
    });

    const summary = document.createElement("summary");
    summary.append(icon("chevron", "paper-chevron"));
    const copy = document.createElement("span");
    const title = document.createElement("span");
    title.className = "paper-title";
    title.textContent = paper.title;
    const meta = document.createElement("span");
    meta.className = "paper-meta";
    meta.textContent = `${t("pageCount", paper.pages)} · ${t(
      "chunkCount",
      paper.sections.reduce((total, section) => total + section.chunks, 0),
    )}`;
    copy.append(title, meta);
    summary.append(copy);

    const sections = document.createElement("ul");
    sections.className = "section-list";
    paper.sections.forEach((section) => {
      const item = document.createElement("li");
      const name = document.createElement("span");
      name.className = "section-name";
      name.textContent = section.name;
      const page = document.createElement("span");
      page.className = "section-page";
      page.textContent = section.page == null ? "—" : t("page", section.page);
      item.append(name, page);
      sections.append(item);
    });
    details.append(summary, sections);
    root.append(details);
  });
}

function renderError() {
  const node = document.getElementById("error");
  if (!state.error) {
    node.hidden = true;
    node.textContent = "";
    return;
  }
  node.hidden = false;
  const translated = state.error.code && STRINGS[state.lang][state.error.code];
  const prefix = translated ? t(state.error.code) : "";
  node.textContent = [prefix, state.error.message].filter(Boolean).join(" ") || t("network");
}

function renderStage() {
  const root = document.getElementById("stage");
  root.innerHTML = "";
  if (state.busy === "ask") {
    root.append(renderLoading());
    return;
  }
  if (!state.result) {
    root.append(renderEmptyState());
    return;
  }
  root.append(renderResult());
}

function renderLoading() {
  const section = document.createElement("section");
  section.className = "loading-state";
  const kicker = document.createElement("p");
  kicker.className = "empty-kicker";
  kicker.textContent = t("loadingTitle");
  section.append(kicker);
  for (let index = 0; index < 3; index += 1) {
    const line = document.createElement("div");
    line.className = "loading-line";
    section.append(line);
  }
  const copy = document.createElement("p");
  copy.className = "loading-copy";
  copy.textContent = t("loadingCopy");
  section.append(copy);
  return section;
}

function renderEmptyState() {
  const section = document.createElement("section");
  section.className = "empty-state";
  const kicker = document.createElement("p");
  kicker.className = "empty-kicker";
  kicker.textContent = t("welcomeKicker");
  const title = document.createElement("h2");
  title.textContent = t(state.library ? "readyTitle" : "welcomeTitle");
  const copy = document.createElement("p");
  copy.className = "empty-copy";
  copy.textContent = t(state.library ? "readyCopy" : "welcomeCopy");
  section.append(kicker, title, copy, renderWorkflow(), renderExamples());
  return section;
}

function renderWorkflow() {
  const list = document.createElement("div");
  list.className = "workflow-steps";
  [
    ["01", "stepParse", "stepParseCopy"],
    ["02", "stepRetrieve", "stepRetrieveCopy"],
    ["03", "stepVerify", "stepVerifyCopy"],
  ].forEach(([number, titleKey, copyKey]) => {
    const item = document.createElement("div");
    item.className = "workflow-step";
    const numberNode = document.createElement("span");
    numberNode.className = "workflow-number";
    numberNode.textContent = number;
    const title = document.createElement("strong");
    title.textContent = t(titleKey);
    const copy = document.createElement("p");
    copy.textContent = t(copyKey);
    item.append(numberNode, title, copy);
    list.append(item);
  });
  return list;
}

function renderExamples() {
  const section = document.createElement("section");
  section.className = "example-section";
  const label = document.createElement("p");
  label.className = "section-label";
  label.textContent = t("examples");
  const list = document.createElement("div");
  list.className = "example-list";
  EXAMPLES.forEach((example) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "example-item";
    const text = document.createElement("span");
    text.textContent = example[state.lang];
    button.append(text, icon("arrow"));
    button.addEventListener("click", () => {
      questionBox.value = example[state.lang];
      questionBox.focus();
      questionBox.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    list.append(button);
  });
  section.append(label, list);
  return section;
}

function renderResult() {
  const article = document.createElement("article");
  article.className = "result";
  const header = document.createElement("header");
  header.className = "result-header";

  const questionLabel = document.createElement("p");
  questionLabel.className = "result-question-label";
  questionLabel.textContent = t("resultQuestion");
  const question = document.createElement("p");
  question.className = "result-question";
  question.textContent = state.asked;
  const answerLabel = document.createElement("p");
  answerLabel.className = "answer-label";
  answerLabel.textContent = t("resultAnswer");
  const answer = document.createElement("p");
  answer.className = "answer-text";
  answer.textContent = state.result.answer;
  const toolbar = document.createElement("div");
  toolbar.className = "result-toolbar";
  toolbar.append(
    toolbarButton(t("openSources", state.result.evidence.length), "source", () => {
      state.evidenceTab = "sources";
      state.activeEvidence = state.result.evidence[0]?.id || null;
      openPanel("detail");
      renderDetail();
    }),
    toolbarButton(t("openRun"), "activity", () => {
      state.evidenceTab = "run";
      openPanel("detail");
      renderDetail();
    }),
  );
  header.append(questionLabel, question, answerLabel, answer, toolbar);
  article.append(header, renderClaims());
  return article;
}

function toolbarButton(label, iconName, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "toolbar-button";
  button.append(icon(iconName));
  const text = document.createElement("span");
  text.textContent = label;
  button.append(text);
  button.addEventListener("click", onClick);
  return button;
}

function renderClaims() {
  const details = document.createElement("details");
  details.className = "claims-disclosure";
  details.open = true;
  const supported = state.result.claims.filter((claim) => claim.label === "supported").length;
  const uncertain = state.result.claims.length - supported;

  const summary = document.createElement("summary");
  const title = document.createElement("span");
  title.className = "claims-summary-title";
  title.append(icon("chevron"));
  const titleText = document.createElement("span");
  titleText.textContent = t("claims");
  title.append(titleText);
  const counts = document.createElement("span");
  counts.className = "claims-counts";
  counts.textContent = t("claimsSummary", supported, uncertain);
  summary.append(title, counts);
  details.append(summary);

  if (!state.result.claims.length) {
    const empty = document.createElement("p");
    empty.className = "empty-note";
    empty.textContent = t("noClaims");
    details.append(empty);
    return details;
  }

  const list = document.createElement("ol");
  list.className = "claims-list";
  state.result.claims.forEach((claim) => {
    const status = claim.label === "supported"
      ? "supported"
      : claim.verdict === "refutes"
        ? "refutes"
        : "uncertain";
    const item = document.createElement("li");
    item.className = "claim-row";
    item.dataset.status = status;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "claim-button";
    const stateLabel = document.createElement("span");
    stateLabel.className = "claim-status";
    stateLabel.textContent = t(status);
    const text = document.createElement("span");
    text.className = "claim-text";
    text.textContent = claim.text;
    button.append(stateLabel, text);
    const citation = claimCitation(claim);
    if (citation) {
      const citationLine = document.createElement("span");
      citationLine.className = "citation-line";
      citationLine.append(icon("source"));
      const citationText = document.createElement("span");
      citationText.textContent = citation;
      citationLine.append(citationText);
      button.append(citationLine);
    }
    button.addEventListener("click", () => {
      state.evidenceTab = claim.evidence_index ? "sources" : "run";
      state.activeEvidence = claim.evidence_index;
      openPanel("detail");
      renderDetail();
    });
    item.append(button);
    list.append(item);
  });
  details.append(list);
  return details;
}

function claimCitation(claim) {
  if (!claim.paper_title && !claim.section && claim.page == null) return "";
  const page = claim.page == null ? t("unknownPage") : t("page", claim.page);
  return [claim.paper_title, claim.section, page].filter(Boolean).join(" · ");
}

function renderDetail() {
  document.querySelectorAll("[data-detail-tab]").forEach((button) => {
    const active = button.dataset.detailTab === state.evidenceTab;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  const root = document.getElementById("detail-content");
  root.innerHTML = "";
  if (!state.result) {
    root.append(emptyNote(t("noRun"), "drawer-empty"));
    return;
  }
  if (state.evidenceTab === "sources") renderSources(root);
  else renderRunDetails(root);
}

function renderSources(root) {
  if (!state.result.evidence.length) {
    root.append(emptyNote(t("noSources"), "drawer-empty"));
    return;
  }
  state.result.evidence.forEach((source) => {
    const card = document.createElement("article");
    card.className = "source-card";
    card.id = `source-${source.id}`;
    card.classList.toggle("is-active", source.id === state.activeEvidence);
    const index = document.createElement("span");
    index.className = "source-index";
    index.textContent = `E${source.id}`;
    const location = document.createElement("div");
    location.className = "source-location";
    const page = source.page == null ? t("unknownPage") : t("page", source.page);
    location.textContent = [source.paper_title, source.section, page].filter(Boolean).join(" · ");
    const text = document.createElement("p");
    text.className = "source-text";
    text.textContent = source.text;
    card.append(index, location, text);
    card.addEventListener("click", () => {
      state.activeEvidence = source.id;
      renderDetail();
    });
    root.append(card);
  });
  if (state.activeEvidence) {
    window.requestAnimationFrame(() => {
      document.getElementById(`source-${state.activeEvidence}`)?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    });
  }
}

function renderRunDetails(root) {
  const supported = state.result.claims.filter((claim) => claim.label === "supported").length;
  const grid = document.createElement("div");
  grid.className = "metric-grid";
  [
    [String(state.result.steps), t("metricSteps")],
    [`${state.result.latency_s.toFixed(1)}s`, t("metricLatency")],
    [String(state.result.prompt_tokens + state.result.completion_tokens), t("metricTokens")],
    [`${supported}/${state.result.claims.length}`, t("metricCoverage")],
  ].forEach(([value, label]) => {
    const metric = document.createElement("div");
    metric.className = "metric";
    const metricValue = document.createElement("span");
    metricValue.className = "metric-value";
    metricValue.textContent = value;
    const metricLabel = document.createElement("span");
    metricLabel.className = "metric-label";
    metricLabel.textContent = label;
    metric.append(metricValue, metricLabel);
    grid.append(metric);
  });
  root.append(grid);

  const title = document.createElement("h3");
  title.className = "run-section-title";
  title.textContent = t("trace");
  root.append(title);

  const list = document.createElement("ol");
  list.className = "trace-list";
  (state.result.trace || []).forEach((step, index) => {
    list.append(renderTraceStep(step, index + 1));
  });
  const verify = {
    action: "verify",
    queries: [],
  };
  list.append(renderTraceStep(verify, (state.result.trace || []).length + 1));
  root.append(list);
}

function renderTraceStep(step, number) {
  const item = document.createElement("li");
  item.className = "trace-step";
  const dot = document.createElement("span");
  dot.className = "trace-dot";
  dot.textContent = String(number);
  const content = document.createElement("div");
  const title = document.createElement("div");
  title.className = "trace-title";
  const copy = document.createElement("p");
  copy.className = "trace-copy";

  if (step.action === "none") {
    title.textContent = t("traceNoneTitle");
    copy.textContent = t("traceNone");
  } else if (step.action === "single") {
    title.textContent = t("traceSingleTitle");
    copy.textContent = t("traceSingle");
  } else if (step.action === "stop") {
    title.textContent = t("traceStopTitle");
    copy.textContent = t("traceStop");
  } else if (step.action === "verify") {
    title.textContent = t("traceVerifyTitle");
    const supported = state.result.claims.filter((claim) => claim.label === "supported").length;
    copy.textContent = state.result.verify
      ? t("traceVerify", supported, state.result.claims.length - supported)
      : t("traceNoVerify");
  } else {
    title.textContent = t("traceSearchTitle");
    copy.textContent = t("traceSearch");
  }
  content.append(title, copy);
  if (step.queries?.length) {
    const queries = document.createElement("ul");
    queries.className = "trace-queries";
    step.queries.forEach((query) => {
      const queryItem = document.createElement("li");
      queryItem.textContent = query;
      queries.append(queryItem);
    });
    content.append(queries);
  }
  item.append(dot, content);
  return item;
}

function renderHistory() {
  document.getElementById("history-count").textContent = String(state.history.length);
  const root = document.getElementById("history");
  root.innerHTML = "";
  if (!state.history.length) {
    root.append(emptyNote(t("historyEmpty")));
    return;
  }
  state.history.forEach((entry) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "history-item";
    button.classList.toggle("is-active", entry.id === state.activeId);
    const question = document.createElement("span");
    question.className = "history-question";
    question.textContent = entry.question;
    const system = SYSTEMS.find((item) => item.id === entry.system);
    const meta = document.createElement("span");
    meta.className = "history-meta";
    meta.textContent = `${system ? system[state.lang] : entry.system} · ${formatTime(entry.at)}`;
    button.append(question, meta);
    button.addEventListener("click", () => {
      state.result = entry.result;
      state.asked = entry.question;
      state.system = entry.system;
      state.activeId = entry.id;
      state.error = null;
      state.activePanel = null;
      state.activeEvidence = null;
      questionBox.value = entry.question;
      render();
    });
    root.append(button);
  });
}

function formatTime(value) {
  return new Intl.DateTimeFormat(state.lang === "zh" ? "zh-CN" : "en", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function emptyNote(text, className = "empty-note") {
  const note = document.createElement("p");
  note.className = className;
  note.textContent = text;
  return note;
}

function icon(name, className = "") {
  const paths = {
    arrow: ["M4 10h11", "M11 6l4 4-4 4"],
    activity: ["M3 10h3l2-5 4 10 2-5h3"],
    source: ["M6 4.5h7.5A1.5 1.5 0 0 1 15 6v9.5H7A2 2 0 0 1 5 13.5v-8a1 1 0 0 1 1-1Z", "M7 13.5h8"],
    chevron: ["m7 5 5 5-5 5"],
  };
  const node = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  node.setAttribute("viewBox", "0 0 20 20");
  node.setAttribute("aria-hidden", "true");
  if (className) node.setAttribute("class", className);
  (paths[name] || paths.arrow).forEach((data) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", data);
    node.append(path);
  });
  return node;
}

async function indexPapers() {
  const body = new FormData();
  body.set("source", state.source);
  body.set("include_lite", document.getElementById("include-lite").checked ? "true" : "false");
  if (state.source === "upload") {
    const files = [...document.getElementById("files").files];
    if (!files.length) {
      state.error = { code: "need_pdf" };
      render();
      return;
    }
    files.forEach((file) => body.append("files", file));
  }

  state.busy = "index";
  state.error = null;
  state.indexNote = "indexing";
  render();
  try {
    const payload = await postForm("/api/library", body);
    state.library = { id: payload.library_id, papers: payload.papers };
    sessionStorage.setItem(LIBRARY_KEY, JSON.stringify(state.library));
    state.expandedPapers = new Set(payload.papers.map((paper) => paper.id));
    state.result = null;
    state.asked = "";
    state.activeId = null;
    state.activeEvidence = null;
    state.indexNote = "indexed";
    if (window.matchMedia("(max-width: 860px)").matches) state.activePanel = null;
  } catch (error) {
    state.indexNote = "";
    state.error = error;
  } finally {
    state.busy = "";
    render();
  }
}

async function askQuestion() {
  const question = questionBox.value.trim();
  if (!state.library) {
    state.error = { code: "need_index" };
    if (window.matchMedia("(max-width: 860px)").matches) state.activePanel = "library";
    render();
    return;
  }
  if (!question) {
    state.error = { code: "empty_question" };
    render();
    questionBox.focus();
    return;
  }

  state.busy = "ask";
  state.error = null;
  state.activePanel = null;
  render();
  try {
    const result = await postJson("/api/ask", {
      library_id: state.library.id,
      question,
      system: state.system,
    });
    const entry = {
      id: window.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`,
      question,
      system: state.system,
      result,
      at: Date.now(),
    };
    state.history = [entry, ...state.history].slice(0, 30);
    sessionStorage.setItem(HISTORY_KEY, JSON.stringify(state.history));
    state.result = result;
    state.asked = question;
    state.activeId = entry.id;
    state.activeEvidence = result.evidence[0]?.id || null;
  } catch (error) {
    state.error = error;
  } finally {
    state.busy = "";
    render();
  }
}

async function postForm(url, body) {
  let response;
  try {
    response = await fetch(url, { method: "POST", body });
  } catch {
    throw { code: "network" };
  }
  return readResponse(response);
}

async function postJson(url, body) {
  let response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw { code: "network" };
  }
  return readResponse(response);
}

async function readResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (response.ok) return payload;
  const detail = payload.detail;
  if (detail && typeof detail === "object") {
    throw { code: detail.code || "ask_failed", message: detail.message || "" };
  }
  throw { message: typeof detail === "string" ? detail : t("network") };
}
