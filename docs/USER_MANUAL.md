# User manual

## From a URL to the essential ideas

![Four stages from a source link to evidence-aware essentials](../assets/workflow.svg)

Install the skill using the [installation guide](INSTALLATION.md), or use a complete prompt directly in chat. Pick a lens from the [prompt catalog](../skills/essentiabot-content/prompts/README.md), paste your URL, and say what you want to understand. The assistant extracts what is available, discloses that coverage, and applies the chosen behavior.

```text
Use Essentiabot with the essence prompt. Here is the URL: [paste URL]. Give me the central idea, the useful substance, the weakest supported claim, and one takeaway. Keep it concise.
```

If the named prompt file is unavailable to the host, paste its full code block. The [prompt guide](PROMPT_GUIDE.md) explains file references, prompt URLs, and persistent chat defaults.

## Choose the question before choosing the lens

- For fast triage, use `essence`.
- To stress-test persuasion, use `antithesis` or `socratic-inquiry`.
- For purpose and agency, use `existentialist-meaning` or `stoic-control`.
- To turn an idea into an experiment, use `pragmatist-test`.
- For empirical claims, use `critical-rationalism` or `evidence-audit`.
- For explanations and engineering choices, use `first-principles`, `systems-thinking`, or `technical-tradeoffs`.
- For a slide, chart, or screenshot, use `visual-claims`.

These lenses ask different questions. A philosophical lens does not turn an unsupported factual claim into a verified one.

## Images, carousels, and captions

Attach the image directly or provide its public URL. Ask the assistant to open it and distinguish visible text from interpretation. The helper's `--download-images` option retrieves files; the host's vision capability reads them. If the host cannot inspect images, it must disclose that limitation.

For Instagram carousels, include the actual `img_index` URL or attach the specific slide. The post caption refers to the whole post. A public cover image is insufficient evidence for what appears on a later slide.

## YouTube and short videos

When accessible, YouTube captions provide the spoken-text basis for analysis. Automatic captions can contain errors. The helper does not listen to audio or watch the full video. TikTok's public route supplies captions and a thumbnail, which may support only a limited reading of the post's framing.

![Existing user-supplied chat with a transcript coverage statement and core ideas](../assets/real-chat-example.png)

This is the user's supplied screenshot, not a newly reproduced test. Its Spanish status label belongs to the original interface. See [validation](VALIDATION.md) for checks actually performed on this repository.

## Keep the conversation useful

Ask for your preferred language, audience, and length. Follow up with “Which claim has the weakest support?”, “Now apply antithesis,” or “What one piece of evidence would change your conclusion?” The assistant should reuse recovered material unless a fresh extraction is necessary.

For multiple links, ask for separate coverage statements before comparing their claims. Do not confuse several repetitions of the same claim with independent corroboration.

## Interpret the result

Look for a main thesis, useful ideas, evidence boundaries, missing context, and a practical verdict. A full SWOT or long report is optional. With only metadata, the answer should remain limited. Removing filler should make the reasoning easier to see while preserving qualifications that matter.

The [worked examples](EXAMPLES.md) show copyable requests and a fictional antithesis response. The [troubleshooting guide](TROUBLESHOOTING.md) covers missing execution, inaccessible sources, and partial retrieval. You can always supply text, captions, or images directly.
