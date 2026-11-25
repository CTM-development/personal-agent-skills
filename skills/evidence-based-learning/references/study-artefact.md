# Interactive visual study experience

Read this when building or revising a study experience. Build at least one visual representation the learner can act on. Design its controls around the relationship, procedure or distinction they need to learn.

## Choose a format

Use a host-native interactive component, a runnable notebook with controls, a single self-contained HTML file or another surface the learner can open and operate. Self-contained HTML is a portable default when the host lacks a suitable interactive surface. Use inline CSS, JavaScript and data so it can run offline. Use a live preview where available and give the learner a download or launch route.

If the surface cannot host controls, provide a runnable artefact when possible. If it can only render visuals in conversation, use a sequence of visual states the learner can control by choosing the next action. State the limitation and update the displayed visual after each choice.

## Build the interaction

1. **Diagnose.** Use a short starting prediction or retrieval item when it informs instruction. Reuse what the learner already attempted in conversation. Preserve the initial response when it will help reveal a misconception later.
2. **Represent the material.** Use one section per major idea and group related ideas into one visual when it helps. Choose a representation that makes the relevant structure visible, such as a plot, diagram, annotated source, timeline or simulation. Give a worked example or orient the learner when they need prerequisites.
3. **Let the learner act.** Have them change a variable, step through a process, classify a case, compare two states or otherwise alter the representation. At a useful decision point, prompt a prediction before the outcome appears. Ask the learner to inspect the updated visual and explain the relationship. For example, change the number of attention heads at a fixed model width, inspect the changed per-head projection shapes and explain which dimensions stay fixed.
4. **Ask for a substantive explanation.** Prompt for the relevant mechanism, assumption or counterexample and give criteria for a good response. Reveal feedback after an attempt or on request. Keep drafts where the surface supports it.
5. **Check independently.** Use fresh items matched to the objectives, plus a transfer task when application is a goal. Mix confusable cases when choosing the method is part of the objective. Give feedback after submission, including why tempting alternatives fail. Report any repeat-item comparison separately. Use confidence chiefly to flag individual high-confidence errors.
6. **Plan returns.** Store the objective, whether the answer was unaided, observed errors and the next due date. Choose intervals based on the retention goal and performance. Give feedback after misses and schedule another attempt. Lengthen gaps after repeated unaided success. Include fresh cases where the objective involves transfer, and give the learner a due-items view or a dated list.

## Deliver and verify

- For a hosted or downloadable artefact, open it in the intended surface and try a complete interaction. Check that the learner’s action changes the visual as intended and that the prompt and feedback fit the displayed state. For browser-based artefacts, check controls and layout at desktop and narrow viewport widths when browser tools are available.
- Validate computed or simulated examples against simple cases with known answers. Label illustrative parameters where they appear. Explain any verification limits.
- If review state or drafts depend on browser storage, handle storage failures and identify where the data lives. Provide export and import for cross-session state when the format supports it. If persistence is unavailable, give the learner a copyable review record.
- [claude] For Claude apps, use a compatible interactive artifact type or publish the HTML if the available delivery tools require it. Read the artifact guide before publishing. For Claude Code, write the artefact to the project or a location the learner names.
- [general] For ChatGPT or Codex, use the interactive preview if supported or attach or link the runnable artefact and explain how to open it.

## Revisit

Reuse the interactive experience. Begin with unaided retrieval, revisit the visual where it helps repair a specific misconception, then ask the learner to explain or solve a fresh case. Add sections and fade scaffolds as performance warrants.
