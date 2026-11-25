# The study artefact

Read this when building or revising a study artefact. Flags as in SKILL.md: **[general]** works in any harness, **[claude]** relies on a Claude or Anthropic feature.

## Format [general]

One self-contained HTML page: CSS, JavaScript and data inline, no build step, no server. It runs in any browser, from a file or a host. Load nothing from the network unless the delivery route allows it (published Claude artifacts only allow a short list of CDNs and fonts).

## Structure [general]

1. **Prediction card** at the top: 4–8 questions aimed at likely misconceptions. Collect answer and confidence, do not reveal answers, reuse the same items in the final test for a before/after comparison. If the learner already read the material, say this is now a retrieval test rather than a prediction.
2. **One section per big idea.**
   - The heading states the point.
   - 3–6 key claims, each labelled as paper-reported, synthesis or critique, with tier, learning type and source.
   - One instrument the learner manipulates: a model simulator with sliders, a predict-then-reveal classifier, a sequencing task, a calculator applied to the learner's own data, or a small self-experiment with a note on its confounds.
3. **Instruments ask before they show.** The learner commits a prediction (a number, a choice, a sketch described in words) before the result or the optimum is revealed. Show one relationship, one step or one comparison at a time. An instrument that displays the whole mechanism or the optimal value up front is the answer in prettier clothes.
4. **"Explain it" prompt per section**: a textarea; the model answer unlocks only after a minimum attempt (e.g. 80 characters). Drafts kept in local storage.
5. **Final interleaved test**: all sections shuffled, no two consecutive questions from the same section; confidence before checking; elaborative feedback after. Results: score, Brier score, calibration plot, before/after on the prediction items, missed items with explanations.
6. **Spaced return queue**: wrong or unsure items return after 1 day; correct and confident ones after 3, 7, then 21 days. A "review due" button runs only due items. State that the queue lives in this browser only.
7. **Progress loop** across the top: Predict → Study → Explain → Retrieve → Return.
8. **Optional**: a section mapping the material onto the learner's own projects or study system, when it relates.

## Delivery

- [claude] **claude.ai / Claude apps:** list the available artifact types first. When none fits an interactive study page, publish the HTML page as an artifact (private until the learner shares it). Read the artifact guide before the first publish.
- [claude] **Claude Code:** write the file into the project or a folder the learner names, and give the path.
- [general] **Any other harness:** write `study-<topic>.html` where the learner can open it, give the path, and say it opens in any browser. Attach the file if the harness can send files.

## Checks before delivering [general]

- Validate every embedded model numerically before writing the page (run it in Node or Python, check the outputs are plausible). Label illustrative parameters as such, next to the instrument they affect. Without code execution, keep instruments analytic and say the parameters are unvalidated.
- Wrap local storage in try/catch; the page must work without it. No alert/confirm dialogs; build confirmation into the page.
- If a headless browser is available (e.g. Playwright), load the page at desktop width and ~400 px, light and dark: zero console errors, no horizontal overflow. If not, say the page was not checked in a browser.

## Revising on return sessions [general]

Revise the same file or artifact rather than starting over: add sections, move missed items into the review queue, fade scaffolds the learner no longer needs. [claude] A published artifact keeps its link across revisions.
