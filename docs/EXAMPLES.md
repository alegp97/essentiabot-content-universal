# Copy-and-paste examples

Replace `[paste URL]` with your source. Examples that reference a file require the host to read that file; otherwise open the linked template and copy its full code block.

## 1. Reach the essentials

```text
Use Essentiabot Content and load prompts/essence.md from the installed skill. Analyze [paste URL]. Give me the central idea, up to five useful points, what is mostly filler, the weakest supported claim, and one practical takeaway. State whether you used page text, captions, metadata, or inspected images. Answer in English in under 250 words.
```

Template: [essence (v1)](../skills/essentiabot-content/prompts/essence.md).

## 2. Cite and apply an antithesis prompt

```text
Read and apply this behavioral prompt:
https://raw.githubusercontent.com/alegp97/essentiabot-content-universal/main/skills/essentiabot-content/prompts/antithesis.md

Analyze this content source: [paste URL]. Retrieve the source's available text, captions, or relevant images first. State the coverage and preserve uncertainty. Give the strongest thesis, the strongest objection, the evidence test, and what survives. Do not manufacture equal support for both sides.

Finish with "Prompt: antithesis (v1)". Cite the content source separately. If you cannot read the prompt URL, tell me and I will paste its text.
```

Template: [antithesis (v1)](../skills/essentiabot-content/prompts/antithesis.md).

## 3. Read a chart or carousel slide

```text
Use Essentiabot and load prompts/visual-claims.md. Inspect the image at [paste URL] or the attachment. First identify visible text and chart labels, marking unreadable details. Then distinguish the actual visual evidence from what the design suggests. If this is a carousel, analyze the selected slide and keep the whole-post caption separate.
```

Template: [visual-claims (v1)](../skills/essentiabot-content/prompts/visual-claims.md).

## 4. Assess a technical tutorial

```text
Use Essentiabot and load prompts/technical-tradeoffs.md. Analyze [paste URL] for a small team maintaining a production service. Explain the mechanism, compare it with a simpler baseline, identify missing benchmarks or version information, and propose one representative trial before adoption.
```

Template: [technical-tradeoffs (v1)](../skills/essentiabot-content/prompts/technical-tradeoffs.md).

## 5. Examine a claim about meaning

```text
Use Essentiabot and load prompts/existentialist-meaning.md. Analyze [paste URL]. Identify its view of purpose, freedom, and responsibility; separate descriptions from prescriptions; and give a plausible alternative interpretation. Keep the analysis in Spanish and cite the prompt ID.
```

Template: [existentialist-meaning (v1)](../skills/essentiabot-content/prompts/existentialist-meaning.md).

## 6. A follow-up using the same evidence

```text
Now load prompts/antithesis.md and apply it to the same material you already retrieved. Focus on the claim with the largest practical consequences. Do not repeat the whole summary.
```

## Worked response: a fictional claim

The following source and response are illustrative. They are not a live extraction or a report about a real study.

**Supplied excerpt:** “Every meeting reduces productivity. Our team removed all meetings for one week and closed more tickets. Therefore every company should eliminate meetings.”

**Coverage:** User-provided excerpt only. No team records, ticket-quality data, or external studies were supplied.

**Thesis:** Replacing meetings with asynchronous communication may recover time for individual work. The excerpt's broader claim is that this should apply to every company.

**Antithesis:** Some meetings resolve coordination or ambiguity that asynchronous messages handle poorly. Removing all of them may increase individual output while shifting costs elsewhere. This is an analytical objection, not a separately verified source finding.

**Evidence test:** One team's one-week observation does not establish a universal causal effect. Ticket counts do not reveal quality, rework, workload changes, or delayed coordination costs. A useful comparison would track delivery quality and coordination outcomes alongside time spent meeting.

**What survives:** Audit low-value meetings and trial selective reductions. The evidence supplied does not justify eliminating every meeting in every organization. The most informative missing evidence is whether better outcomes persist without increased defects or coordination failures.

Prompt: antithesis (v1). Content source: the fictional excerpt above.

![Illustrative antithesis analysis distilled into a compact chat-style card](../assets/antithesis-example.svg)
