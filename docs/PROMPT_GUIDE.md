# Prompt guide: where the behavior lives and how to use it

The source URL identifies **what to read**. The behavioral prompt specifies **how to examine it**. The installed skill handles source selection and coverage; the host assistant performs the analysis. The Python extractor returns evidence as JSON and does not run prompt files itself.

## Where are the prompts?

The canonical directory is `skills/essentiabot-content/prompts/` in the repository, or `prompts/` relative to the installed skill directory. Keeping it inside the skill means it is included in the standalone skill ZIP. The [catalog](../skills/essentiabot-content/prompts/README.md) lists all 12 templates.

Each template has a stable ID, version, intended use, expected result, and one complete code block to copy. Philosophy-inspired prompts are modern analytical lenses; they are not quotations, historical reenactments, or comprehensive accounts of a philosophical school.

## Method 1 — installed skill

Paste this in the chat's normal message box:

```text
Use Essentiabot. Load prompts/antithesis.md relative to the installed skill directory. Apply that prompt to this URL: [paste URL]. State extraction coverage and cite the prompt ID and version.
```

The agent should read that file. A prompt ID is a locator, not a special command implemented by the Python scripts. If the agent cannot access the file, use Method 3.

## Method 2 — cite a repository prompt by URL

In a chat with browsing, paste:

```text
Read the behavioral prompt at:
https://raw.githubusercontent.com/alegp97/essentiabot-content-universal/main/skills/essentiabot-content/prompts/antithesis.md

Use its instructions to analyze the content source below with Essentiabot. Cite the template as "Prompt: antithesis (v1)" and cite the content source separately. If you cannot access the prompt, ask me to paste its text; do not claim to have loaded it.

Content source: [paste the article, video, or post URL here]
```

The prompt URL is the chosen behavior, not the content to criticize. The content URL is the evidence source. For an audit that must be reproducible, record the repository commit as well as the template version; a `main` URL can change.

## Method 3 — copy the full prompt text

Open [antithesis.md](../skills/essentiabot-content/prompts/antithesis.md), copy everything inside its code block, paste it as a normal chat message, and replace the `Source:` placeholder. This is the most portable method because the instructions are already present in the message. A host without browsing needs supplied text, transcripts, or image attachments.

## Make a behavior the default for later URLs

Use the self-contained chat-default example in the [prompt catalog](../skills/essentiabot-content/prompts/README.md). Once acknowledged, you can paste a URL on its own in that conversation. An explicit later request, such as “translate this paragraph,” takes precedence over the default analysis format.

If your host provides persistent project instructions, you may paste that default there yourself. Keep permanent instructions short and select detailed lenses per task. This repository does not install global instructions, change host settings, or grant access to tools automatically.

## Tune the output

Add one or two constraints to the request: “under 250 words,” “answer in Spanish,” “explain for a beginner,” or “focus on the engineering tradeoffs.” Ask for external verification explicitly when you need it; the host may also need to verify uncertain or consequential claims under its own rules.

Filler means repetition, unsupported certainty, generic slogans, or promotion that does not help the question. It does not mean inconvenient evidence, nuance, or a view you disagree with.

## Follow-ups and combinations

Start with `essence`, then ask “Apply `antithesis` to the same extracted material.” For a chart-heavy post, inspect images with `visual-claims`, then use `evidence-audit` for consequential assertions. For a tool tutorial, use `technical-tradeoffs`, then `first-principles` on one disputed mechanism. Avoid requesting all 12 lenses at once.

## Prompt citation versus evidence citation

`Prompt: antithesis (v1)` records the analytical method. A source URL, reliable timestamp, or document location supports a content claim. The prompt citation does not verify the source. The assistant should distinguish the author's claims, external verification, and its own objections or hypotheses.

## Add your own prompt

Create one Markdown file inside `prompts/` with a unique kebab-case ID. Describe the decision it helps with, then write a complete copyable prompt. Include coverage disclosure, evidence boundaries, and the expected output. Link it from the catalog. Increase its version when its behavior materially changes. Follow the review guidance in [maintenance](MAINTENANCE.md).
