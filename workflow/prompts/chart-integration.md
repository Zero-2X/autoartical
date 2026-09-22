# writing.2 - Chart Integration

Integrate generated charts into the experiments narrative.

## Goals
- Align each chart with the claim it supports.
- Place charts where they help the paper instead of dumping them at the end.
- Keep captions and text consistent with the actual data.

## Required Behavior
- Map each chart to a claim id or experiment question.
- Preserve the visual language from the selected `styled_plot_templates` template family so charts look like one coherent paper set.
- When the experiments section uses richer table styling, keep charts visually compatible with that choice: muted blue / teal / orange / sand / gray palettes are allowed, but the section should still read like a paper rather than a poster.
- Insert or update figure references in the target section.
- Write chart captions in a compact paper style: usually one to two sentences, enough to state what is compared and what the main takeaway is, with a caveat only when it materially changes interpretation.
- If a chart weakens the current narrative, revise the narrative rather than hiding the chart.

## Outputs
- updated experiments section
- updated chart manifest integration status
- chart notes on placement and captioning
