"""Deep-learning extensions for the AI Engineering Interview Atlas.

The objects in this module are consumed by both the browser and the handbook
builders.  Formula strings are valid LaTeX and intentionally remain separate
from prose so that renderers never escape mathematical commands.
"""

from __future__ import annotations


ROADMAP = [
    {
        "id": "phase-00", "order": 0, "title": "Diagnostic and study system", "hours": 3,
        "prerequisites": [],
        "categories": [],
        "outcomes": ["Benchmark current recall across all domains", "Set a weekly active-recall cadence", "Create an error log organized by mechanism, tradeoff, metric, and failure"],
        "milestone": "Complete 50 mixed questions and label every miss by cause.",
        "practice": "50 mixed questions; do not study before the diagnostic.",
    },
    {
        "id": "phase-01", "order": 1, "title": "Python, APIs, and distributed foundations", "hours": 22,
        "prerequisites": ["phase-00"],
        "categories": ["Python Engineering", "Backend, APIs, and Microservices", "Distributed Systems and Reliability"],
        "outcomes": ["Explain Python execution and concurrency", "Design typed streaming APIs", "Reason about queues, retries, caching, consensus, and capacity"],
        "milestone": "Design a backpressured streaming API and defend its failure semantics.",
        "practice": "180 questions plus system designs 8 and 12.",
    },
    {
        "id": "phase-02", "order": 2, "title": "Transformer mathematics and training", "hours": 26,
        "prerequisites": ["phase-01"],
        "categories": ["Transformer Theory and Training"],
        "outcomes": ["Derive scaled dot-product attention", "Explain normalization, residuals, objectives, and preference tuning", "Estimate training and adaptation memory"],
        "milestone": "Derive attention, cross-entropy, LoRA, and DPO without notes.",
        "practice": "120 questions and one whiteboard derivation session.",
    },
    {
        "id": "phase-03", "order": 3, "title": "Retrieval theory and vector systems", "hours": 28,
        "prerequisites": ["phase-02"],
        "categories": ["Retrieval and Search Theory", "Vector Databases and Search Engines"],
        "outcomes": ["Compare lexical, dense, sparse, and hybrid retrieval", "Derive ranking metrics and fusion", "Select and tune exact, HNSW, IVF, and PQ indexes"],
        "milestone": "Choose pgvector or a dedicated vector service from a stated workload and prove the choice with filtered recall tests.",
        "practice": "260 questions plus a retrieval benchmark design.",
    },
    {
        "id": "phase-04", "order": 4, "title": "RAG construction, graphs, and evaluation", "hours": 30,
        "prerequisites": ["phase-03"],
        "categories": ["RAG Architecture and Evaluation", "Knowledge Graphs and GraphRAG"],
        "outcomes": ["Build traceable ingestion-to-answer pipelines", "Separate retrieval, generation, citation, and business evaluation", "Know when graphs add value over vector retrieval"],
        "milestone": "Localize a RAG regression to ingestion, retrieval, packing, generation, or judging.",
        "practice": "270 questions plus system designs 1, 2, and 3.",
    },
    {
        "id": "phase-05", "order": 5, "title": "Agents, MCP, orchestration, and sandbox control", "hours": 28,
        "prerequisites": ["phase-04"],
        "categories": ["Agents, MCP, and Control", "Orchestration Frameworks"],
        "outcomes": ["Separate agentic decisions from deterministic workflow boundaries", "Design durable state, retries, approvals, and compensation", "Apply least privilege to tools, sandboxes, and MCP servers"],
        "milestone": "Design a resumable agent that cannot duplicate a high-impact side effect.",
        "practice": "230 questions plus system designs 4 and 5.",
    },
    {
        "id": "phase-06", "order": 6, "title": "Serving and inference optimization", "hours": 28,
        "prerequisites": ["phase-02", "phase-01"],
        "categories": ["Inference Optimization", "Serving, Deployment, and LLMOps"],
        "outcomes": ["Calculate KV-cache and batching capacity", "Explain quantization, FlashAttention, GQA, and speculative decoding", "Design model routing, rollout, autoscaling, and fallback"],
        "milestone": "Meet a p95 TTFT target under a token-distribution workload and explain the cost model.",
        "practice": "250 questions plus system designs 7 and 10.",
    },
    {
        "id": "phase-07", "order": 7, "title": "Observability, evaluation, and quality monitoring", "hours": 20,
        "prerequisites": ["phase-04", "phase-05", "phase-06"],
        "categories": ["Observability and Monitoring"],
        "outcomes": ["Instrument traces across retrieval, model, and tool spans", "Define semantic SLOs and calibrated evaluators", "Detect cost, latency, and quality drift by cohort"],
        "milestone": "Write an incident runbook that ties alerts to traces, evaluation slices, and rollback.",
        "practice": "130 questions plus system design 6.",
    },
    {
        "id": "phase-08", "order": 8, "title": "Data, experiments, and ML lifecycle", "hours": 18,
        "prerequisites": ["phase-07"],
        "categories": ["Data and ML Lifecycle"],
        "outcomes": ["Version code, data, prompts, models, and environments together", "Prevent leakage with point-in-time joins", "Promote artifacts using reproducible evaluation evidence"],
        "milestone": "Reproduce an evaluation run from immutable lineage and promote or roll back its artifacts.",
        "practice": "120 questions plus system design 11.",
    },
    {
        "id": "phase-09", "order": 9, "title": "Security, safety, and governance", "hours": 18,
        "prerequisites": ["phase-05", "phase-07"],
        "categories": ["Security, Safety, and Governance"],
        "outcomes": ["Threat-model prompt, retrieval, tool, and model supply chains", "Design tenant isolation and auditable policy enforcement", "Connect evaluations to release gates and incident response"],
        "milestone": "Threat-model one agentic RAG architecture and close its three highest-risk paths.",
        "practice": "120 questions plus system design 9.",
    },
    {
        "id": "phase-10", "order": 10, "title": "Integrated AI system design", "hours": 26,
        "prerequisites": ["phase-06", "phase-08", "phase-09"],
        "categories": [],
        "outcomes": ["Translate ambiguous requirements into SLOs and workload models", "Build multi-stage architectures with explicit data and control planes", "Defend tradeoffs, degradation, migration, and rollback"],
        "milestone": "Complete all 12 designs aloud in 45 minutes each, including every twist.",
        "practice": "All 12 system designs; repeat the weakest four after 72 hours.",
    },
    {
        "id": "phase-11", "order": 11, "title": "Interview simulation and targeted repair", "hours": 18,
        "prerequisites": ["phase-10"],
        "categories": [],
        "outcomes": ["Answer at medium and hard depth under time pressure", "Use clarifying questions and quantitative estimates", "Convert misses into a short repair loop"],
        "milestone": "Score at least 80% on 200 unseen mixed questions and pass three timed mock loops.",
        "practice": "200 mixed questions, 3 mocks, and spaced repetition of every miss.",
    },
]


FORMULAS = [
    {
        "id": "bm25-score", "title": "BM25 relevance score", "topic_ids": ["bm25"],
        "latex": r"\operatorname{BM25}(q,d)=\sum_{t\in q}\operatorname{IDF}(t)\frac{f(t,d)(k_1+1)}{f(t,d)+k_1\left(1-b+b\frac{|d|}{\overline{|d|}}\right)}",
        "variables": ["f(t,d): term frequency", "|d| and average |d|: document lengths", "k1: saturation", "b: length normalization"],
        "derivation": [
            {"text": "Begin with an additive score over query terms; rare terms receive inverse-document-frequency weight.", "latex": r"S(q,d)=\sum_{t\in q}\operatorname{IDF}(t)\,g(f(t,d),|d|)"},
            {"text": "Use a rational response so marginal gain shrinks as a term repeats. The derivative is positive but approaches zero.", "latex": r"g(f)=\frac{f(k_1+1)}{f+K},\qquad \frac{\partial g}{\partial f}=\frac{(k_1+1)K}{(f+K)^2}"},
            {"text": "Let K grow for documents longer than average, controlled by b; substitution yields BM25.", "latex": r"K=k_1\left(1-b+b\frac{|d|}{\overline{|d|}}\right)"},
        ],
        "example": "With b=0, document length is ignored. With b=1, length is fully normalized. Larger k1 delays saturation, so repeated terms continue to matter longer.",
    },
    {
        "id": "tfidf", "title": "TF-IDF weighting", "topic_ids": ["tf-idf"],
        "latex": r"w_{t,d}=\operatorname{tf}(t,d)\operatorname{idf}(t),\qquad \operatorname{idf}(t)=\log\frac{N+1}{\operatorname{df}(t)+1}",
        "variables": ["N: number of documents", "df(t): documents containing t", "tf(t,d): within-document frequency"],
        "derivation": [{"text": "Term frequency rewards evidence inside a document; inverse document frequency discounts terms that occur in many documents. Multiplication requires both local presence and collection-level specificity.", "latex": r"\operatorname{df}(t)\uparrow\Rightarrow\operatorname{idf}(t)\downarrow;\quad \operatorname{tf}(t,d)=0\Rightarrow w_{t,d}=0"}],
        "example": "A token in 10 of 10,000 documents receives much more weight than a token in 9,000 documents, even when their local counts match.",
    },
    {
        "id": "vector-similarity", "title": "Cosine, dot product, and Euclidean distance", "topic_ids": ["embedding-geometry", "dense-retrieval"],
        "latex": r"\cos(\mathbf q,\mathbf x)=\frac{\mathbf q^\top\mathbf x}{\|\mathbf q\|_2\|\mathbf x\|_2},\qquad \|\mathbf q-\mathbf x\|_2^2=2-2\mathbf q^\top\mathbf x\ \text{when }\|\mathbf q\|=\|\mathbf x\|=1",
        "variables": ["q: query vector", "x: item vector", "unit normalization makes cosine equal dot product"],
        "derivation": [{"text": "Expand the squared distance and then impose unit norms.", "latex": r"\|\mathbf q-\mathbf x\|^2=\|\mathbf q\|^2+\|\mathbf x\|^2-2\mathbf q^\top\mathbf x=2-2\mathbf q^\top\mathbf x"}],
        "example": "For normalized embeddings, maximizing dot product, maximizing cosine, and minimizing squared Euclidean distance produce the same ranking; without normalization they need not.",
    },
    {
        "id": "contrastive-retrieval", "title": "Contrastive retrieval loss", "topic_ids": ["dense-retrieval", "cross-encoder-reranking"],
        "latex": r"\mathcal L_i=-\log\frac{\exp(s(q_i,d_i^+)/\tau)}{\sum_{j=1}^{B}\exp(s(q_i,d_j)/\tau)}",
        "variables": ["s: similarity score", "tau: temperature", "B: in-batch candidates", "d_i+: positive passage"],
        "derivation": [{"text": "Treat candidate passages as classes. Softmax converts similarities to a conditional probability and negative log-likelihood raises the positive score relative to negatives.", "latex": r"p(d_i^+\mid q_i)=\operatorname{softmax}_j(s(q_i,d_j)/\tau)_i,\quad\mathcal L_i=-\log p(d_i^+\mid q_i)"}],
        "example": "Lower temperature sharpens score differences but can destabilize training. Hard negatives increase learning signal and also magnify false-negative risk.",
    },
    {
        "id": "rrf", "title": "Reciprocal rank fusion", "topic_ids": ["reciprocal-rank-fusion", "hybrid-retrieval"],
        "latex": r"\operatorname{RRF}(d)=\sum_{r\in\mathcal R}\frac{1}{k+\operatorname{rank}_r(d)}",
        "variables": ["R: retriever lists", "rank_r(d): one-based rank", "k: rank-smoothing constant"],
        "derivation": [{"text": "Replace incomparable raw scores with monotone rank evidence, then add support across retrievers. The constant limits how much a single first-place rank dominates.", "latex": r"\Delta_{1,2}=\frac1{k+1}-\frac1{k+2}=\frac1{(k+1)(k+2)}"}],
        "example": "With k=60, the difference between ranks 1 and 2 is small; repeated appearance across lists often matters more than a tiny rank change.",
    },
    {
        "id": "retrieval-metrics", "title": "Recall, precision, MRR, MAP, and nDCG", "topic_ids": ["retrieval-metrics", "ann-recall", "rag-evaluation"],
        "latex": r"P@k=\frac{1}{k}\sum_{i=1}^{k}rel_i,\quad R@k=\frac{\sum_{i=1}^{k}rel_i}{|R_q|},\quad \operatorname{MRR}=\frac1{|Q|}\sum_q\frac1{\operatorname{rank}_q}",
        "variables": ["rel_i: relevance at rank i", "R_q: relevant set", "rank_q: first relevant rank"],
        "derivation": [{"text": "Precision normalizes hits by returned capacity; recall normalizes by all available relevant evidence. MRR cares only about the first hit.", "latex": r"\operatorname{DCG}@k=\sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)},\qquad \operatorname{nDCG}@k=\frac{\operatorname{DCG}@k}{\operatorname{IDCG}@k}"}],
        "example": "Use MRR for a single-answer lookup, Recall@k for evidence coverage, and nDCG when relevance is graded and ordering across several items matters.",
    },
    {
        "id": "hnsw-cost", "title": "HNSW latency-memory model", "topic_ids": ["hnsw", "ann-recall"],
        "latex": r"M_{\text{graph}}\approx N\,M\,b_{\text{edge}},\qquad T_{\text{query}}\propto ef_{\text{search}}\log N",
        "variables": ["N: vectors", "M: neighbors per node", "ef_search: candidate breadth", "b_edge: bytes per edge"],
        "derivation": [{"text": "Each node stores approximately M graph links, giving linear graph memory. Hierarchical navigation reduces the search depth while ef_search controls local exploration.", "latex": r"\operatorname{recall}\uparrow\ \text{as}\ ef_{\text{search}}\uparrow,\qquad \operatorname{latency}\uparrow\ \text{as}\ ef_{\text{search}}\uparrow"}],
        "example": "The relation is an engineering model, not an exact bound. Measure it separately for selective filters, deletes, and the target vector distribution.",
    },
    {
        "id": "ivfpq", "title": "IVF-PQ decomposition", "topic_ids": ["ivf-and-pq"],
        "latex": r"\mathbf x\approx\mathbf c_{a(\mathbf x)}+[\mathbf c^{(1)}_{j_1};\ldots;\mathbf c^{(m)}_{j_m}],\qquad B_{PQ}=m\log_2 K\ \text{bits/vector}",
        "variables": ["a(x): coarse IVF cell", "m: subspaces", "K: codewords per subspace", "c: centroids"],
        "derivation": [{"text": "IVF first limits candidates to nearby coarse centroids. PQ splits the residual vector into m subspaces and stores one codeword index per subspace.", "latex": r"\widehat{\mathbf r}=[c^{(1)}_{j_1};\dots;c^{(m)}_{j_m}],\quad \mathbf r=\mathbf x-\mathbf c_{a(\mathbf x)}"}],
        "example": "For m=16 and K=256, the PQ code uses 128 bits or 16 bytes per vector, excluding identifiers, centroids, and index overhead.",
    },
    {
        "id": "chunk-count", "title": "Chunk count and overlap", "topic_ids": ["chunking", "parent-child-retrieval", "context-packing"],
        "latex": r"n=1+\left\lceil\frac{L-C}{C-O}\right\rceil\quad(L>C),\qquad \rho_{dup}\approx\frac{O}{C-O}",
        "variables": ["L: document tokens", "C: chunk size", "O: overlap", "C-O: stride"],
        "derivation": [{"text": "After the first chunk, each new chunk advances by the stride C-O. Covering the remaining L-C tokens needs the ceiling of remaining length divided by stride.", "latex": r"(n-1)(C-O)\ge L-C\Rightarrow n\ge1+\frac{L-C}{C-O}"}],
        "example": "A 10,000-token document with C=500 and O=100 needs 25 chunks. Larger overlap raises storage and duplicate evidence roughly in proportion to O/(C-O).",
    },
    {
        "id": "faithfulness", "title": "Claim-level faithfulness", "topic_ids": ["faithfulness", "grounded-generation", "rag-evaluation"],
        "latex": r"F=\frac{\sum_{i=1}^{m}w_i\,\mathbf 1[\operatorname{entailed}(c_i,E)]}{\sum_{i=1}^{m}w_i}",
        "variables": ["c_i: answer claim", "E: supplied evidence", "w_i: claim importance"],
        "derivation": [{"text": "Decompose an answer into atomic claims, test evidence entailment for each claim, and normalize supported importance by total importance.", "latex": r"F\in[0,1],\quad F=1\Leftrightarrow\text{every weighted claim is supported}"}],
        "example": "A correct but uncited claim can be factually correct and still unfaithful to the supplied context. Human calibration is needed for claim segmentation and entailment thresholds.",
    },
    {
        "id": "graph-quality", "title": "Entity and edge extraction quality", "topic_ids": ["entity-resolution", "knowledge-graph-construction", "graph-quality-evaluation"],
        "latex": r"P=\frac{TP}{TP+FP},\quad R=\frac{TP}{TP+FN},\quad F_1=\frac{2PR}{P+R}",
        "variables": ["TP: correct entities or edges", "FP: hallucinated/incorrect", "FN: missed"],
        "derivation": [{"text": "Precision prices false graph facts; recall prices missing graph facts. The harmonic mean falls sharply when either is weak.", "latex": r"F_1=\frac{2}{1/P+1/R}"}],
        "example": "For a high-impact graph, optimize and report precision and provenance separately; one F1 value can hide unacceptable hallucinated edges.",
    },
    {
        "id": "attention", "title": "Scaled dot-product attention", "topic_ids": ["self-attention-math", "multi-head-attention", "flashattention"],
        "latex": r"\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V",
        "variables": ["Q,K,V: projected token matrices", "d_k: head dimension", "M: causal or padding mask"],
        "derivation": [{"text": "If independent query and key components have zero mean and unit variance, their dot product has variance d_k.", "latex": r"\operatorname{Var}(q^\top k)=\sum_{j=1}^{d_k}\operatorname{Var}(q_jk_j)=d_k"}, {"text": "Division by the standard deviation keeps logits order-one, preventing softmax saturation at initialization.", "latex": r"\operatorname{Var}\left(\frac{q^\top k}{\sqrt{d_k}}\right)=1"}],
        "example": "The scaling is a variance argument. It does not remove the quadratic n-by-n score matrix used by ordinary full attention.",
    },
    {
        "id": "softmax", "title": "Softmax and its gradient", "topic_ids": ["self-attention-math", "causal-language-modeling"],
        "latex": r"p_i=\frac{e^{z_i}}{\sum_j e^{z_j}},\qquad \frac{\partial p_i}{\partial z_j}=p_i(\delta_{ij}-p_j)",
        "variables": ["z: logits", "p: normalized probabilities", "delta: Kronecker delta"],
        "derivation": [{"text": "Differentiate the exponential numerator and shared denominator with the quotient rule.", "latex": r"\partial_{z_j}p_i=\frac{\delta_{ij}e^{z_i}Z-e^{z_i}e^{z_j}}{Z^2}=p_i(\delta_{ij}-p_j)"}],
        "example": "Subtract max(z) before exponentiation for numerical stability; the probability is unchanged because softmax is invariant to a common additive constant.",
    },
    {
        "id": "rope", "title": "Rotary position embedding", "topic_ids": ["positional-encoding"],
        "latex": r"R_\theta(m)=\begin{bmatrix}\cos(m\theta)&-\sin(m\theta)\\\sin(m\theta)&\cos(m\theta)\end{bmatrix},\quad (R(m)q)^\top(R(n)k)=q^\top R(n-m)k",
        "variables": ["m,n: positions", "theta: frequency per dimension pair"],
        "derivation": [{"text": "Rotation matrices are orthogonal and compose by angle addition. Therefore the query-key product depends on relative position n-m.", "latex": r"R(m)^\top R(n)=R(-m)R(n)=R(n-m)"}],
        "example": "RoPE injects relative-position structure into the attention product; extrapolation still depends on frequency scaling and the distribution seen in training.",
    },
    {
        "id": "normalization", "title": "LayerNorm and RMSNorm", "topic_ids": ["layer-normalization-and-rmsnorm", "residual-connections"],
        "latex": r"\operatorname{LN}(x)=\gamma\odot\frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta,\qquad \operatorname{RMSNorm}(x)=\gamma\odot\frac{x}{\sqrt{\frac1d\sum_i x_i^2+\epsilon}}",
        "variables": ["mu,sigma: feature mean and variance", "gamma,beta: learned affine parameters"],
        "derivation": [{"text": "LayerNorm centers and rescales each token vector; RMSNorm keeps only magnitude normalization. Both make sublayer scale more predictable, but only LayerNorm removes the mean.", "latex": r"\frac1d\sum_i\left(\frac{x_i-\mu}{\sigma}\right)^2=1"}],
        "example": "RMSNorm removes mean computation and the beta shift. Treat it as an architectural choice that requires validation, not a universally interchangeable optimization.",
    },
    {
        "id": "cross-entropy", "title": "Cross-entropy and perplexity", "topic_ids": ["causal-language-modeling", "cross-entropy-and-perplexity"],
        "latex": r"\mathcal L=-\frac1T\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{<t}),\qquad \operatorname{PPL}=e^{\mathcal L}",
        "variables": ["T: token count", "p_theta: next-token probability", "PPL: effective branching factor"],
        "derivation": [{"text": "Autoregressive factorization writes sequence likelihood as a product; negative log changes the product into an additive loss.", "latex": r"p(x_{1:T})=\prod_t p(x_t\mid x_{<t})\Rightarrow-\frac1T\log p(x_{1:T})=-\frac1T\sum_t\log p(x_t\mid x_{<t})"}],
        "example": "Perplexity 10 means an average negative log-likelihood of ln(10), but perplexities are comparable only with the same tokenization and evaluation distribution.",
    },
    {
        "id": "dpo", "title": "Direct Preference Optimization", "topic_ids": ["dpo"],
        "latex": r"\mathcal L_{DPO}=-\log\sigma\left(\beta\left[\log\frac{\pi_\theta(y_w\mid x)}{\pi_{ref}(y_w\mid x)}-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{ref}(y_l\mid x)}\right]\right)",
        "variables": ["y_w,y_l: preferred and rejected responses", "pi_ref: reference policy", "beta: preference strength / KL control"],
        "derivation": [{"text": "A Bradley-Terry preference model uses the difference between implicit rewards. DPO substitutes log policy ratios for those rewards and minimizes binary logistic loss.", "latex": r"P(y_w\succ y_l\mid x)=\sigma(r(x,y_w)-r(x,y_l))"}],
        "example": "DPO avoids an explicit reward-model-plus-PPO loop but remains sensitive to pair quality, support mismatch, beta, and reference policy choice.",
    },
    {
        "id": "ppo", "title": "PPO clipped objective", "topic_ids": ["rlhf-and-ppo"],
        "latex": r"L^{clip}=\mathbb E_t\left[\min\left(r_tA_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)A_t\right)\right],\quad r_t=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{old}(a_t\mid s_t)}",
        "variables": ["A_t: advantage estimate", "epsilon: update clip", "r_t: probability ratio"],
        "derivation": [{"text": "The unclipped policy-gradient surrogate rewards probability changes aligned with the advantage. Clipping removes incentive for a single update to move the ratio beyond a trusted interval.", "latex": r"r_t\notin[1-\epsilon,1+\epsilon]\Rightarrow\text{surrogate improvement is capped}"}],
        "example": "Clipping is only one control; RLHF systems also use KL penalties, reward calibration, value estimation, and careful rollout monitoring.",
    },
    {
        "id": "lora", "title": "LoRA low-rank adaptation", "topic_ids": ["lora", "qlora"],
        "latex": r"W'=W+\Delta W,\qquad \Delta W=\frac{\alpha}{r}BA,\quad A\in\mathbb R^{r\times d_{in}},\ B\in\mathbb R^{d_{out}\times r}",
        "variables": ["r: adapter rank", "alpha: scaling", "W: frozen base weight"],
        "derivation": [{"text": "A dense update has d_out*d_in parameters. Factorizing it through rank r uses r(d_in+d_out), which is smaller when r is much less than either dimension.", "latex": r"\frac{P_{LoRA}}{P_{dense}}=\frac{r(d_{in}+d_{out})}{d_{in}d_{out}}"}],
        "example": "For a 4096-by-4096 projection and r=16, the adapter has 131,072 parameters versus 16,777,216 for a dense update: about 0.78%.",
    },
    {
        "id": "kv-cache", "title": "KV-cache memory", "topic_ids": ["kv-caching", "pagedattention", "gqa-and-mqa", "capacity-planning"],
        "latex": r"M_{KV}=B\,L\,S\,2\,H_{kv}\,D_h\,b",
        "variables": ["B: sequences", "L: layers", "S: cached tokens", "2: keys and values", "H_kv: KV heads", "D_h: head dimension", "b: bytes per element"],
        "derivation": [{"text": "At every layer and token, the cache stores one key and one value for each KV head and head feature. Multiplying all axes gives element count, then bytes.", "latex": r"N_{elements}=B\times L\times S\times 2\times H_{kv}\times D_h"}],
        "example": "B=8, L=32, S=4096, Hkv=8, Dh=128, and FP16 gives 4 GiB. GQA lowers Hkv; paging reduces fragmentation, not the live tensor requirement.",
    },
    {
        "id": "attention-complexity", "title": "Attention compute and memory", "topic_ids": ["self-attention-math", "flashattention"],
        "latex": r"\operatorname{FLOPs}(QK^\top)\approx2n^2d,\qquad M_{scores}=\Theta(n^2),\qquad M_{Flash}=\Theta(nd)\ \text{auxiliary}",
        "variables": ["n: sequence length", "d: head/model width depending on accounting"],
        "derivation": [{"text": "Multiplying an n-by-d query matrix by a d-by-n key matrix creates n squared scores, each using d multiply-add work. FlashAttention tiles the exact computation so the full score matrix need not be written to high-bandwidth memory.", "latex": r"Q_{n\times d}K_{d\times n}^{\top}\rightarrow S_{n\times n}"}],
        "example": "FlashAttention reduces memory traffic and auxiliary storage but does not change exact full attention's quadratic arithmetic in sequence length.",
    },
    {
        "id": "gqa-reduction", "title": "GQA KV reduction", "topic_ids": ["gqa-and-mqa", "kv-caching"],
        "latex": r"\frac{M_{KV}^{GQA}}{M_{KV}^{MHA}}=\frac{H_{kv}}{H_q}",
        "variables": ["Hq: query heads", "Hkv: shared key/value heads"],
        "derivation": [{"text": "All KV-cache axes except the number of KV heads remain equal, so their memory ratio reduces to Hkv divided by Hq.", "latex": r"\frac{BL S2H_{kv}D_hb}{BL S2H_qD_hb}=\frac{H_{kv}}{H_q}"}],
        "example": "With 32 query heads and 8 KV heads, GQA uses one quarter of the KV-head storage of ordinary MHA, subject to architecture-specific quality effects.",
    },
    {
        "id": "quantization", "title": "Affine quantization", "topic_ids": ["quantization"],
        "latex": r"q=\operatorname{clip}\left(\operatorname{round}\left(\frac{x}{s}\right)+z,q_{min},q_{max}\right),\qquad \hat x=s(q-z)",
        "variables": ["s: positive scale", "z: zero point", "q: integer code", "x-hat: reconstructed value"],
        "derivation": [{"text": "Map a floating interval to the available integer range. For asymmetric min-max quantization, the scale divides the real range by the number of integer steps.", "latex": r"s=\frac{x_{max}-x_{min}}{q_{max}-q_{min}},\qquad z\approx q_{min}-\frac{x_{min}}s"}],
        "example": "Smaller groups adapt scales to local outliers but add metadata and kernel complexity. Accuracy depends on calibration, outliers, activation dynamics, and target hardware.",
    },
    {
        "id": "speculative", "title": "Speculative decoding speed condition", "topic_ids": ["speculative-decoding"],
        "latex": r"S\approx\frac{\mathbb E[A]+1}{C_T(\gamma)+\gamma C_D},\qquad \mathbb E[A]=\sum_{i=1}^{\gamma}P(A\ge i)",
        "variables": ["gamma: draft tokens", "A: accepted draft prefix", "C_T: target verification cost", "C_D: draft cost"],
        "derivation": [{"text": "One speculative cycle advances by the accepted prefix plus a target token. Divide expected progress by target verification plus draft cost; speedup requires this rate to exceed ordinary target decoding.", "latex": r"S>1\Leftrightarrow \mathbb E[A]+1>C_T(\gamma)+\gamma C_D\ \text{in target-token cost units}"}],
        "example": "High draft acceptance is insufficient if the draft is expensive or target verification kernels are inefficient; benchmark end-to-end on the output distribution.",
    },
    {
        "id": "little-law", "title": "Little's Law for capacity", "topic_ids": ["capacity-planning", "queues-and-backpressure", "continuous-batching", "asyncio"],
        "latex": r"L=\lambda W",
        "variables": ["L: average in-flight work", "lambda: arrival/throughput rate", "W: average time in system"],
        "derivation": [{"text": "Over a long interval T, approximately lambda*T jobs arrive. If each spends W time units in the system, accumulated job-time is lambda*T*W; divide by T to get average concurrency.", "latex": r"L=\frac{\lambda T\,W}{T}=\lambda W"}],
        "example": "At 20 requests/s and 3 s mean latency, average concurrency is 60. Tail-aware headroom is still required because Little's Law uses stable averages.",
    },
    {
        "id": "availability", "title": "Availability composition", "topic_ids": ["multi-region-design", "fault-isolation"],
        "latex": r"A_{series}=\prod_i A_i,\qquad A_{parallel}=1-\prod_i(1-A_i)",
        "variables": ["Ai: component availability", "series: every dependency required", "parallel: any independent replica suffices"],
        "derivation": [{"text": "Independent series success requires all successes, so probabilities multiply. Parallel failure requires every replica to fail, so availability is one minus joint failure.", "latex": r"P(\text{all fail})=\prod_i(1-A_i)"}],
        "example": "Two independent 99% replicas yield 99.99% parallel availability, but correlated region, configuration, or dependency failures invalidate independence.",
    },
    {
        "id": "retry-backoff", "title": "Exponential backoff with jitter", "topic_ids": ["retries-and-timeouts", "temporal"],
        "latex": r"d_n\sim U\left(0,\min(d_{max},d_0 2^n)\right),\qquad N_{attempts}\le 1+\left\lfloor\frac{B}{C_{attempt}}\right\rfloor",
        "variables": ["dn: nth delay", "B: retry budget", "jitter: random delay"],
        "derivation": [{"text": "Exponential growth separates repeated attempts; full jitter prevents synchronized clients from retrying together. A retry budget bounds amplification.", "latex": r"\sum_{n=0}^{m-1}d_0 2^n=d_0(2^m-1)\ \text{before caps and jitter}"}],
        "example": "Retry only transient, idempotent operations. Multiply retries across layers and a three-layer stack with three attempts each can cause up to 27 downstream attempts.",
    },
    {
        "id": "token-bucket", "title": "Token-bucket admission control", "topic_ids": ["rate-limiting", "queues-and-backpressure"],
        "latex": r"T(t)=\min\{B,\,T(t_0)+r(t-t_0)-c\},\qquad c\le T(t_0)+r(t-t_0)",
        "variables": ["B: bucket capacity", "r: refill rate", "c: request cost in tokens"],
        "derivation": [{"text": "Credits accumulate at rate r up to burst capacity B. Admit work only when its token-weighted cost is covered, then subtract it.", "latex": r"\text{sustained throughput}\le r,\qquad \text{instantaneous burst}\le B"}],
        "example": "Charge estimated prompt plus maximum output tokens rather than one request unit; otherwise a single long request can defeat fair admission.",
    },
    {
        "id": "amdahl", "title": "Amdahl's Law", "topic_ids": ["multiprocessing", "tensor-parallelism", "pipeline-parallelism", "data-parallel-inference"],
        "latex": r"S(N)=\frac{1}{(1-p)+p/N}",
        "variables": ["p: parallelizable fraction", "N: workers", "1-p: serial fraction"],
        "derivation": [{"text": "Normalize original runtime to one. The serial fraction remains 1-p and the ideal parallel fraction shrinks from p to p/N.", "latex": r"T_N=(1-p)+\frac pN,\qquad S(N)=\frac{T_1}{T_N}"}],
        "example": "If 95% is parallelizable, infinite workers cannot exceed 20x speedup. Communication and imbalance make real speedup lower.",
    },
    {
        "id": "cost-model", "title": "LLM request cost", "topic_ids": ["cost-observability", "llm-gateways", "capacity-planning"],
        "latex": r"C_{req}=\frac{T_{in}P_{in}+T_{out}P_{out}}{10^6}+C_{retrieval}+C_{tools}+C_{infra}",
        "variables": ["Tin,Tout: token counts", "Pin,Pout: price per million tokens", "other terms: per-request allocated costs"],
        "derivation": [{"text": "Allocate each metered component to the request, then aggregate by tenant, route, model, and outcome. Expected cost includes route probabilities and retry/fallback branches.", "latex": r"\mathbb E[C]=\sum_r P(r)C_r+P(\text{retry})C_{retry}+P(\text{fallback})C_{fallback}"}],
        "example": "Track cost per successful, quality-qualified outcome; a cheap route that fails and falls back can cost more than a reliable primary route.",
    },
    {
        "id": "slo-error-budget", "title": "SLO error budget", "topic_ids": ["metrics-and-slos", "evaluation-in-production", "fault-isolation"],
        "latex": r"B_{error}=N(1-SLO),\qquad \operatorname{burn}=\frac{\text{observed bad-event fraction}}{1-SLO}",
        "variables": ["N: eligible events", "SLO: target good-event fraction", "burn > 1: budget consumed too quickly"],
        "derivation": [{"text": "If the target permits 1-SLO bad events, multiply that fraction by eligible traffic. Burn rate normalizes observed badness by the permitted rate.", "latex": r"\operatorname{burn}=1\Rightarrow\text{budget exhausted exactly over the SLO window}"}],
        "example": "Define separate indicators for availability, TTFT, completion, and semantic quality; one composite can hide a severe dimension failure.",
    },
    {
        "id": "drift", "title": "Distribution drift with KL and JS divergence", "topic_ids": ["prompt-and-model-drift", "online-rag-monitoring"],
        "latex": r"D_{KL}(P\|Q)=\sum_i P_i\log\frac{P_i}{Q_i},\qquad JS(P,Q)=\frac12D_{KL}(P\|M)+\frac12D_{KL}(Q\|M),\ M=\frac{P+Q}{2}",
        "variables": ["P: reference distribution", "Q: current distribution", "JS: symmetric bounded divergence under common log base"],
        "derivation": [{"text": "KL measures expected log density ratio under P but is asymmetric and can diverge when Q assigns zero mass. JS compares each distribution with their mixture, making it symmetric and finite.", "latex": r"JS(P,Q)=JS(Q,P)"}],
        "example": "Drift is a trigger for investigation, not proof of quality loss. Segment by tenant, language, route, and document version, then connect to delayed outcome labels.",
    },
    {
        "id": "sampling", "title": "Temperature and top-p sampling", "topic_ids": ["causal-language-modeling", "streaming-generation"],
        "latex": r"p_i(T)=\frac{\exp(z_i/T)}{\sum_j\exp(z_j/T)},\qquad \mathcal V_p=\min\left\{V:\sum_{i\in V}p_i\ge p\right\}",
        "variables": ["T: temperature", "Vp: smallest high-probability nucleus", "z: logits"],
        "derivation": [{"text": "Temperature divides logit gaps. Lower T magnifies relative gaps; higher T flattens them. Top-p then retains the smallest sorted set with cumulative mass at least p and renormalizes.", "latex": r"\log\frac{p_i(T)}{p_j(T)}=\frac{z_i-z_j}{T}"}],
        "example": "At T approaching zero, selection approaches argmax. Determinism also depends on kernels, batching, floating-point order, and provider behavior.",
    },
]


VISUALS = [
    {
        "id": "retrieval-saturation", "category": "Retrieval and Search Theory", "topic_ids": ["bm25", "tf-idf", "retrieval-metrics"],
        "kind": "plot", "title": "Why BM25 saturates repeated terms", "kicker": "RANKING INTUITION",
        "intuition": "The first matching term is strong evidence. Each repetition adds less information, so the score bends toward a ceiling instead of growing forever.",
        "x_label": "term frequency", "y_label": "relative contribution", "x_labels": ["1", "2", "4", "8", "16", "32"],
        "series": [{"label": "linear count", "values": [3, 6, 13, 25, 50, 100]}, {"label": "BM25-like saturation", "values": [47, 65, 80, 90, 96, 100]}],
        "takeaway": "If a document repeats a query token 32 times, it should not automatically outrank a concise document with better coverage.",
    },
    {
        "id": "ann-recall-latency", "category": "Vector Databases and Search Engines", "topic_ids": ["hnsw", "ann-recall", "ivf-and-pq"],
        "kind": "plot", "title": "ANN search moves along a frontier", "kicker": "INDEX TUNING",
        "intuition": "Searching more candidates usually improves recall, but tail latency and compute rise. The useful operating point is a measured frontier, not a universal index setting.",
        "x_label": "search effort", "y_label": "normalized percent", "x_labels": ["tiny", "low", "medium", "high", "max"],
        "series": [{"label": "recall", "values": [58, 74, 86, 94, 98]}, {"label": "latency cost", "values": [12, 21, 37, 66, 100]}],
        "takeaway": "Tune filtered recall and p95 latency together on representative queries; either number alone can hide a bad index configuration.",
    },
    {
        "id": "rag-evidence-loop", "category": "RAG Architecture and Evaluation", "topic_ids": ["document-ingestion", "rag-evaluation", "faithfulness"],
        "kind": "flow", "title": "RAG is an evidence supply chain", "kicker": "DATA + MODEL FLOW",
        "intuition": "A correct-looking answer can fail in five different places. Preserve identifiers so a bad claim can be traced backward to retrieval, source version, and parsing.",
        "steps": [{"label": "Source", "detail": "version + ACL"}, {"label": "Chunk", "detail": "span + metadata"}, {"label": "Retrieve", "detail": "candidate + score"}, {"label": "Generate", "detail": "claim + citation"}, {"label": "Evaluate", "detail": "localize failure"}],
        "takeaway": "Measure retriever recall, context quality, claim support, and answer usefulness separately.",
    },
    {
        "id": "graph-abstraction-ladder", "category": "Knowledge Graphs and GraphRAG", "topic_ids": ["property-graphs", "knowledge-graph-construction", "graphrag-global-search"],
        "kind": "flow", "title": "Graphs add structure in layers", "kicker": "GRAPH INTUITION",
        "intuition": "A knowledge graph is not merely another vector index. It turns mentions into resolved entities, explicit relationships, communities, and queryable summaries.",
        "steps": [{"label": "Mentions", "detail": "raw spans"}, {"label": "Entities", "detail": "resolved identity"}, {"label": "Relations", "detail": "typed edges"}, {"label": "Communities", "detail": "global structure"}, {"label": "Answers", "detail": "traceable paths"}],
        "takeaway": "Each higher layer adds reasoning power and a new source of extraction or resolution error.",
    },
    {
        "id": "agent-control-loop", "category": "Agents, MCP, and Control", "topic_ids": ["agent-loop", "tool-calling", "sandbox-runs"],
        "kind": "flow", "loop": True, "title": "An agent is a controlled feedback loop", "kicker": "CONTROL FLOW",
        "intuition": "The model proposes; policy authorizes; a typed tool changes the world; observation updates state. The loop must have budgets and deterministic stop conditions.",
        "steps": [{"label": "Observe", "detail": "state + evidence"}, {"label": "Propose", "detail": "structured action"}, {"label": "Authorize", "detail": "policy + approval"}, {"label": "Execute", "detail": "idempotent tool"}, {"label": "Record", "detail": "result + audit"}],
        "takeaway": "Do not let natural-language intent bypass authorization or make an external effect invisible to the state machine.",
    },
    {
        "id": "durable-orchestration", "category": "Orchestration Frameworks", "topic_ids": ["langgraph", "temporal", "state-machines"],
        "kind": "flow", "loop": True, "title": "Durability separates decisions from effects", "kicker": "WORKFLOW STATE",
        "intuition": "Persist state before and after risky effects. A retry should replay a decision safely or reuse a recorded result, not duplicate the side effect.",
        "steps": [{"label": "State", "detail": "checkpoint"}, {"label": "Decision", "detail": "pure transition"}, {"label": "Effect", "detail": "idempotency key"}, {"label": "Result", "detail": "durable record"}, {"label": "Resume", "detail": "continue safely"}],
        "takeaway": "Crash recovery is a data-model property before it is a framework feature.",
    },
    {
        "id": "trace-waterfall", "category": "Observability and Monitoring", "topic_ids": ["opentelemetry", "distributed-tracing", "llm-tracing"],
        "kind": "timeline", "title": "A trace explains where latency went", "kicker": "REQUEST WATERFALL",
        "intuition": "End-to-end latency is a composition of queueing, retrieval, model prefill, decoding, tools, and retries. A single aggregate hides the critical path.",
        "steps": [{"label": "Queue", "detail": "0-80 ms"}, {"label": "Retrieve", "detail": "80-210 ms"}, {"label": "Prefill", "detail": "210-430 ms"}, {"label": "Decode", "detail": "430-1250 ms"}, {"label": "Tool", "detail": "overlap/retry"}],
        "takeaway": "Correlate traces with quality, cost, model version, prompt version, and user cohort.",
    },
    {
        "id": "batching-frontier", "category": "Serving, Deployment, and LLMOps", "topic_ids": ["vllm", "autoscaling-for-llms", "continuous-batching"],
        "kind": "plot", "title": "Batching trades latency for utilization", "kicker": "SERVING FRONTIER",
        "intuition": "Larger effective batches fill the accelerator and raise throughput, but waiting and head-of-line blocking eventually dominate request latency.",
        "x_label": "effective batch", "y_label": "normalized percent", "x_labels": ["1", "2", "4", "8", "16", "32"],
        "series": [{"label": "throughput", "values": [12, 23, 43, 68, 86, 92]}, {"label": "p95 latency", "values": [8, 12, 19, 31, 55, 94]}],
        "takeaway": "Choose a workload-specific knee using TTFT, decode rate, queue time, and quality-qualified cost.",
    },
    {
        "id": "lineage-chain", "category": "Data and ML Lifecycle", "topic_ids": ["data-lineage", "dvc", "experiment-tracking"],
        "kind": "flow", "title": "Reproducibility is a chain of identities", "kicker": "LINEAGE",
        "intuition": "A model version is insufficient. You need immutable links among data, code, parameters, environment, prompts, evaluations, and the deployed artifact.",
        "steps": [{"label": "Data", "detail": "snapshot"}, {"label": "Code", "detail": "commit"}, {"label": "Run", "detail": "params + env"}, {"label": "Artifact", "detail": "content hash"}, {"label": "Release", "detail": "evidence + rollback"}],
        "takeaway": "When one link is mutable, exact reproduction and impact analysis become guesses.",
    },
    {
        "id": "attention-grid", "category": "Transformer Theory and Training", "topic_ids": ["self-attention-math", "multi-head-attention", "causal-language-modeling"],
        "kind": "matrix", "title": "Attention builds a token-to-token routing table", "kicker": "TENSOR SHAPES",
        "intuition": "Queries choose where to read; keys advertise what each position contains; softmax turns similarities into routing weights; values carry the information mixed into the output.",
        "steps": [{"label": "QK^T", "detail": "n by n scores"}, {"label": "Scale", "detail": "divide by sqrt(d)"}, {"label": "Mask", "detail": "hide future tokens"}, {"label": "Softmax", "detail": "row probabilities"}, {"label": "Multiply V", "detail": "weighted content"}],
        "takeaway": "Track the n-by-n score matrix separately from the n-by-d token representation.",
    },
    {
        "id": "kv-memory-growth", "category": "Inference Optimization", "topic_ids": ["kv-caching", "pagedattention", "gqa-and-mqa"],
        "kind": "plot", "title": "KV memory grows linearly with live context", "kicker": "MEMORY MODEL",
        "intuition": "Caching avoids recomputing old keys and values, but every live token consumes memory in every layer. GQA lowers the slope; paging reduces fragmentation, not live tensor bytes.",
        "x_label": "context tokens (thousands)", "y_label": "relative KV memory", "x_labels": ["1", "2", "4", "8", "16"],
        "series": [{"label": "multi-head KV", "values": [6, 13, 25, 50, 100]}, {"label": "grouped-query KV", "values": [2, 3, 6, 13, 25]}],
        "takeaway": "Capacity planning must use the distribution of concurrent sequence lengths, not one advertised context maximum.",
    },
    {
        "id": "backpressure-path", "category": "Backend, APIs, and Microservices", "topic_ids": ["rest-api-design", "websockets-and-sse", "rate-limiting"],
        "kind": "flow", "title": "Backpressure must travel toward the caller", "kicker": "SERVICE FLOW",
        "intuition": "When downstream work saturates, bounded queues, deadlines, admission control, and cancellation prevent hidden overload from becoming an outage.",
        "steps": [{"label": "Client", "detail": "deadline"}, {"label": "Gateway", "detail": "admit/reject"}, {"label": "Queue", "detail": "bounded"}, {"label": "Worker", "detail": "cancelable"}, {"label": "Dependency", "detail": "timeout + breaker"}],
        "takeaway": "An unbounded queue converts visible rejection into invisible latency and memory growth.",
    },
    {
        "id": "python-concurrency", "category": "Python Engineering", "topic_ids": ["python-threading-and-the-gil", "asyncio", "multiprocessing"],
        "kind": "timeline", "title": "Choose concurrency from the waiting pattern", "kicker": "EXECUTION MODEL",
        "intuition": "Asyncio overlaps many cooperative waits, threads overlap blocking I/O with shared memory, and processes provide CPU parallelism with serialization and coordination costs.",
        "steps": [{"label": "Asyncio", "detail": "many waits, one loop"}, {"label": "Threads", "detail": "blocking I/O"}, {"label": "Processes", "detail": "CPU parallelism"}, {"label": "Queues", "detail": "ownership boundary"}, {"label": "Cancel", "detail": "structured cleanup"}],
        "takeaway": "Start with whether work is CPU-bound, blocking, or awaitable; syntax comes afterward.",
    },
    {
        "id": "trust-boundaries", "category": "Security, Safety, and Governance", "topic_ids": ["prompt-injection", "tool-authorization", "sandboxing"],
        "kind": "layers", "title": "Authority narrows at every trust boundary", "kicker": "DEFENSE IN DEPTH",
        "intuition": "Prompts, retrieved text, and model outputs are untrusted data. Capabilities come from deterministic policy, scoped credentials, sandbox limits, and explicit approval.",
        "steps": [{"label": "Untrusted text", "detail": "no authority"}, {"label": "Typed proposal", "detail": "schema validation"}, {"label": "Policy", "detail": "allowlist + limits"}, {"label": "Sandbox", "detail": "isolated effect"}, {"label": "Audit", "detail": "evidence + revocation"}],
        "takeaway": "A stronger prompt is not a security boundary; enforce effects outside the model.",
    },
    {
        "id": "reliability-feedback", "category": "Distributed Systems and Reliability", "topic_ids": ["queues-and-backpressure", "retries-and-timeouts", "fault-isolation"],
        "kind": "flow", "loop": True, "title": "Reliability controls form a stabilizing loop", "kicker": "OVERLOAD CONTROL",
        "intuition": "Measure saturation, shed excess work, isolate failures, recover gradually, and feed the outcome into safer limits. Retries without this loop amplify overload.",
        "steps": [{"label": "Measure", "detail": "queue + tails"}, {"label": "Admit", "detail": "budgeted load"}, {"label": "Isolate", "detail": "bulkhead"}, {"label": "Recover", "detail": "backoff + probe"}, {"label": "Learn", "detail": "update limits"}],
        "takeaway": "Design for bounded degradation rather than assuming every dependency remains healthy.",
    },
]


CATEGORY_TEACHING = {
    "Retrieval and Search Theory": {
        "lens": "Model retrieval as a ranking function over a corpus, then separate candidate generation from final ranking.",
        "metrics": ["Recall@k on judged evidence", "nDCG or MRR matched to the task", "latency and cost by query slice", "robustness on identifiers, paraphrases, and out-of-domain queries"],
        "operation": ["Version corpus, tokenizer, embedding, and index", "Run lexical, dense, and hybrid baselines", "Inspect misses before changing the model", "Keep rollback-compatible index snapshots"],
    },
    "Vector Databases and Search Engines": {
        "lens": "Treat the database as a stateful retrieval system whose index, filters, updates, tenancy, and backup behavior are one design.",
        "metrics": ["Filtered ANN recall against exact search", "p50/p95/p99 latency", "index build and update lag", "memory, storage, and total cost"],
        "operation": ["Benchmark representative vector and metadata distributions", "Test selective filters and deletes", "Version embeddings and migration state", "Exercise backup, restore, and reindex procedures"],
    },
    "RAG Architecture and Evaluation": {
        "lens": "Decompose RAG into ingestion, retrieval, packing, generation, and evaluation so a final-answer failure can be localized.",
        "metrics": ["Ingestion correctness and freshness", "Evidence recall and context precision", "Claim faithfulness and citation entailment", "answer quality, latency, and cost"],
        "operation": ["Keep source-to-chunk provenance", "Trace every ranking and packing decision", "Calibrate model judges with humans", "Define abstention and rollback thresholds"],
    },
    "Knowledge Graphs and GraphRAG": {
        "lens": "Use graphs when entities, relations, paths, communities, or temporal structure carry information that flat similarity loses.",
        "metrics": ["Entity and relation precision/recall", "path or subgraph recall", "answer lift on graph-shaped questions", "freshness and provenance coverage"],
        "operation": ["Attach edges to source spans", "Version schema and extraction models", "Resolve duplicates with auditable rules", "Rebuild affected subgraphs incrementally"],
    },
    "Agents, MCP, and Control": {
        "lens": "An agent is a policy choosing actions under partial information; production safety comes from deterministic boundaries around that policy.",
        "metrics": ["Task success and intervention rate", "tool-call validity and side-effect accuracy", "steps, tokens, latency, and cost", "policy violations and recovery rate"],
        "operation": ["Use scoped capabilities and short-lived credentials", "Persist idempotency keys before side effects", "Require approval by risk, not by UI convenience", "Replay traces in an isolated evaluation environment"],
    },
    "Orchestration Frameworks": {
        "lens": "Represent long-running work as explicit state and transitions, with durable checkpoints around nondeterministic or side-effecting boundaries.",
        "metrics": ["Completion and resume success", "duplicate-effect rate", "time in each state and queue", "human-interrupt and compensation outcomes"],
        "operation": ["Keep state schemas versioned", "Make activities idempotent", "Bound loops and retries", "Test crash recovery at every checkpoint"],
    },
    "Observability and Monitoring": {
        "lens": "Connect request traces, semantic evaluation, infrastructure metrics, and business outcomes without treating any single signal as ground truth.",
        "metrics": ["TTFT, inter-token, and end-to-end latency", "token and cost attribution", "quality metrics by cohort", "SLO burn and incident recovery"],
        "operation": ["Propagate correlation IDs across every stage", "Redact content by policy", "Version prompts, models, and evaluators", "Link alerts to actionable runbooks"],
    },
    "Serving, Deployment, and LLMOps": {
        "lens": "Serving is a token-and-memory scheduling problem wrapped in release engineering, routing, and reliability controls.",
        "metrics": ["TTFT and time per output token", "tokens per second and queue time", "KV-cache occupancy and fragmentation", "quality-qualified cost per request"],
        "operation": ["Load-test realistic length distributions", "Use canary and shadow evidence", "Scale on queued work and memory, not only CPU", "Keep deterministic fallback and rollback paths"],
    },
    "Data and ML Lifecycle": {
        "lens": "A reproducible result is a graph of immutable code, data, parameters, environment, model, prompt, and evaluation versions.",
        "metrics": ["Reproduction success", "lineage completeness", "feature or data freshness", "promotion-gate pass rate and drift"],
        "operation": ["Use content-addressed artifacts", "Enforce point-in-time correctness", "Separate registry metadata from artifact bytes", "Retain promotion and rollback evidence"],
    },
    "Transformer Theory and Training": {
        "lens": "Track tensor shapes, probability objectives, gradient paths, and memory movement; architecture names are shorthand for these mechanisms.",
        "metrics": ["Loss and perplexity on held-out slices", "task and safety evaluation", "gradient, activation, and optimizer memory", "throughput and convergence stability"],
        "operation": ["Record tokenizer and data mixture", "Monitor numerical stability", "Evaluate distribution shifts and regressions", "Checkpoint optimizer and model state reproducibly"],
    },
    "Inference Optimization": {
        "lens": "Optimization changes compute, memory capacity, memory traffic, or scheduling; measure which bottleneck moved and what quality was lost.",
        "metrics": ["Prefill and decode latency separately", "throughput at controlled concurrency", "memory and bandwidth utilization", "quality delta by task slice"],
        "operation": ["Benchmark target hardware and kernels", "Use realistic batch and sequence distributions", "Track numerical format and model version", "Retain a correctness reference path"],
    },
    "Backend, APIs, and Microservices": {
        "lens": "Define contracts, ownership, concurrency, backpressure, and failure semantics before choosing a web framework.",
        "metrics": ["request and stream latency", "queue depth and cancellation lag", "error rate by dependency", "resource use and saturation"],
        "operation": ["Use bounded queues and timeouts", "Propagate cancellation", "Version schemas and idempotency contracts", "Test partial dependency failure"],
    },
    "Python Engineering": {
        "lens": "Reason from Python's object model, execution model, and concurrency boundaries rather than memorizing syntax trivia.",
        "metrics": ["correctness tests", "CPU and wall-clock profiles", "allocation and memory behavior", "contention and cancellation behavior"],
        "operation": ["Prefer clear ownership and typing", "Measure before optimizing", "Keep side effects explicit", "Test concurrency and serialization boundaries"],
    },
    "Security, Safety, and Governance": {
        "lens": "Start from assets, actors, trust boundaries, and allowed effects; prompts and model outputs are untrusted data, not authority.",
        "metrics": ["attack success by threat class", "false allow and false block rates", "privilege and data exposure", "detection and containment time"],
        "operation": ["Default-deny tools and networks", "Separate tenant and execution contexts", "Log policy decisions without leaking secrets", "Exercise incident and revocation procedures"],
    },
    "Distributed Systems and Reliability": {
        "lens": "Make failure assumptions explicit, then reason about state, time, delivery, coordination, and overload.",
        "metrics": ["availability and SLO burn", "queue and tail latency", "retry amplification", "recovery point and recovery time"],
        "operation": ["Use idempotency and deduplication", "Bound retries and queues", "Isolate blast radius", "Practice failover with realistic traffic"],
    },
}


def build_tutorials(topics):
    """Generate a complete teaching note for every catalog topic.

    The question bank creates ten prompts per topic: seven MCQs, two
    flashcards, and one long answer.  These lessons explicitly cover each fact
    those prompts test, plus the production reasoning expected in interviews.
    """
    formula_index = {}
    for formula in FORMULAS:
        for topic_id in formula["topic_ids"]:
            formula_index.setdefault(topic_id, []).append(formula["id"])

    tutorials = []
    for topic in topics:
        playbook = CATEGORY_TEACHING[topic["category"]]
        refs = formula_index.get(topic["id"], [])
        quantitative = (
            "Work the linked derivation symbol by symbol, state its assumptions, then explain which parameter moves quality, latency, memory, or cost."
            if refs else
            "No single canonical equation defines this topic. Quantify it with a workload model: arrival rate, item or token volume, service-time distribution, resource limit, quality metric, and error budget."
        )
        tutorials.append({
            "topic_id": topic["id"],
            "name": topic["name"],
            "category": topic["category"],
            "objective": f"Explain {topic['name']} from first principles, choose it for a stated workload, measure it, and recover when it fails.",
            "first_principles": f"{topic['summary']} {playbook['lens']}",
            "mental_model": f"Start with the input and output contract. Identify the state or representation being changed, the algorithm that changes it, and the resource that becomes limiting. For {topic['name']}, never stop at a feature list: connect the mechanism to an observable behavior in a real workload.",
            "quantitative_reasoning": quantitative,
            "formula_ids": refs,
            "decision_reasoning": f"Choose {topic['name']} when its mechanism matches the workload and its benefits survive a representative benchmark. The central tradeoff is: {topic['tradeoff']} Compare against the simplest viable baseline and make the decision reversible where possible.",
            "failure_reasoning": f"The key production trap is: {topic['pitfall']} Trace that failure backward to the violated assumption, define the earliest observable signal, isolate the blast radius, and name a rollback or degraded mode.",
            "evaluation": playbook["metrics"],
            "operations": playbook["operation"],
            "worked_reasoning": [
                f"Requirement: state the workload, quality target, latency percentile, scale, update rate, and risk boundary that matter for {topic['name']}.",
                f"Baseline: implement or measure the least complex alternative before adding {topic['name']}.",
                f"Experiment: vary the mechanism's controlling parameters and evaluate the listed metrics by important cohort, not only as one average.",
                f"Decision: accept the design only if the observed gain justifies this cost: {topic['tradeoff']}",
                f"Production gate: instrument the critical path and block or roll back release when this failure appears: {topic['pitfall']}",
            ],
            "answer_blueprint": {
                "definition": f"Open with one sentence: {topic['summary']}",
                "tradeoff": f"Then state both sides without hedging: {topic['tradeoff']}",
                "failure": f"Name a concrete failure and its detection signal: {topic['pitfall']}",
                "production": "Finish with workload-specific metrics, a trace or dashboard, an SLO or quality threshold, failure isolation, and a rollback condition.",
                "long_answer": "Use the sequence mechanism -> assumptions -> quantitative model -> alternatives -> experiment -> operations -> failure recovery. This directly answers the topic's long-answer prompt.",
            },
            "question_coverage": "This lesson contains the definition, tradeoff, failure association, scenario diagnosis, design explanation, and production rubric tested by all seven MCQs, both flashcards, and the long-answer question for this topic.",
            "references": topic["references"],
        })
    return tutorials
