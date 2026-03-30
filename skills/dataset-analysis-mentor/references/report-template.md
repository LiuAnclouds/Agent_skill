# Report Template Guidance

## Main Report Sections

Use this order unless the user requests a different structure:

1. 数据概况
2. 特征分布与缺失机制
3. 结构/关系模式
4. 时间与漂移
5. 风险点与建模建议
6. 产物索引与阅读顺序

## Section Intent

### 数据概况

State:

- dataset size
- schema or modality
- label space
- split semantics
- task framing

### 特征分布与缺失机制

State:

- which features differ most across classes
- where sentinel values or missingness dominate
- whether missingness itself carries information
- whether strong correlations imply redundancy

### 结构/关系模式

State:

- degree behavior
- directionality
- node-group interaction
- bridge or context-node effects

### 时间与漂移

State:

- activity windows
- time-aware risks
- drift across windows or phases
- whether validation should be chronological

### 风险点与建模建议

Translate observations into:

- feature handling
- split design
- model family implications
- robustness checks

### 产物索引与阅读顺序

Tell the reader what to inspect first and why.

## Style Rules

- Use Chinese prose by default.
- Keep field names and code identifiers in English if they map directly to files or columns.
- Write short evidence-first paragraphs.
- Prefer “现象 -> 解释 -> 启发” over loose commentary.
