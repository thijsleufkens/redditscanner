# Daily local filter: themes

From June to July 2026 a small service read the scanner's database once a day and
picked candidates without a large language model:

1. Take the posts from the last 26 hours that it hadn't seen before.
2. Embed each post (title + the first part of the text) with `nomic-embed-text`
   via Ollama, on CPU.
3. Compare it with each of the five themes below (cosine similarity) and keep
   the best-matching theme.
4. Keep the top 8 posts with a similarity of at least 0.45, plus the best post
   of up to 3 themes that weren't in that top 8 yet, for variety.
5. Mark every post it looked at as seen, so nothing comes back the next day.

A local LLM then wrote a one-line angle for each candidate, and at most six a day
became cards to approve or reject.

The themes are written in English because the posts are. Write your own: the
filter is only as good as these descriptions.

| Theme | Description |
|---|---|
| translating | translating between business and data: turning a vague business question into the right analysis and explaining results back to non-technical managers, bridging the gap between business stakeholders and technical data teams, getting requirements right and understanding what actually needs to be built before building it |
| deciding | using data to make better business decisions, which KPIs and metrics actually matter and drive action, reports and dashboards that change how a company is run, avoiding vanity metrics, asking the right question of the data |
| adoption | why business intelligence and data projects succeed or fail for human and organizational reasons, data adoption and data literacy, getting people to trust and actually use dashboards, stakeholder buy-in, dashboards nobody uses |
| manufacturing | business and operational decision problems in manufacturing SMEs (engineer-to-order, make-to-order): planning, costing, margins, lead times, and where better data or reporting would help management decide |
| strategy | where a small or mid-size business should start with data, building a data-driven culture, the role of a consultant who translates between management and IT, practical data strategy without a big budget |
