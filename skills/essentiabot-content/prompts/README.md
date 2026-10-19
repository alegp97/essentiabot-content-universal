# Prompt library

Choose how the assistant should examine the material. The extractor supplies available evidence; the prompt supplies an analytical lens. These are original practical templates, inspired by broad philosophical traditions and technical methods. They do not impersonate historical thinkers or claim to summarize entire schools.

| Prompt | ID | Family | Best use |
| --- | --- | --- | --- |
| [Essential ideas](essence.md) | `essence` | Everyday | Get to the point of almost any source. |
| [Thesis, antithesis, and what survives](antithesis.md) | `antithesis` | Everyday | Stress-test a persuasive argument without reflexive disagreement. |
| [Socratic inquiry](socratic-inquiry.md) | `socratic-inquiry` | Philosophical | Find ambiguous definitions and hidden premises. |
| [Stoic perspective on agency](stoic-control.md) | `stoic-control` | Philosophical | Evaluate advice about adversity, choices, and personal agency. |
| [Pragmatist consequences](pragmatist-test.md) | `pragmatist-test` | Philosophical | Turn a sweeping idea into a useful, revisable experiment. |
| [Existentialist meaning and responsibility](existentialist-meaning.md) | `existentialist-meaning` | Philosophical | Examine narratives about purpose, freedom, authenticity, and commitment. |
| [Critical rationalism and falsifiability](critical-rationalism.md) | `critical-rationalism` | Philosophical | Test whether an empirical claim can survive serious criticism. |
| [First-principles reconstruction](first-principles.md) | `first-principles` | Technical | Unpack a claim that relies on buzzwords, analogies, or inherited assumptions. |
| [Evidence and uncertainty audit](evidence-audit.md) | `evidence-audit` | Technical | Assess research claims, benchmarks, statistics, and confident headlines. |
| [Systems thinking](systems-thinking.md) | `systems-thinking` | Technical | Understand incentives, feedback, delays, and unintended effects. |
| [Technical tradeoff review](technical-tradeoffs.md) | `technical-tradeoffs` | Technical | Evaluate tool recommendations, engineering tutorials, and architecture claims. |
| [Visual claims and infographic audit](visual-claims.md) | `visual-claims` | Technical | Read screenshots, slides, charts, thumbnails, and carousels critically. |

## Three ways to load a prompt

1. **Installed skill:** ask the agent to load `prompts/antithesis.md` relative to the installed Essentiabot skill directory. The agent must actually read the file.
2. **Repository-aware chat:** reference `skills/essentiabot-content/prompts/antithesis.md` in this repository, or provide its GitHub URL and ask the host to read it.
3. **Any chat:** open the prompt file, copy the text inside its code block, paste it into your message, and replace the final source placeholder. This works without repository-file access, but extraction still requires the host's browsing, execution, or vision capabilities.

A filename, prompt ID, or URL alone does not automatically load instructions in every host. If the agent cannot read the prompt file, paste the prompt text. The citation `Prompt: antithesis (v1)` identifies the template applied; it is not evidence for the analyzed claim.

## Start small

Use `essence` for the first pass, then one focused lens if needed. For example: “Now apply antithesis to the same material, using the content already extracted.” Avoid stacking every prompt into one answer.

## Set a chat default

```text
For URLs I share in this chat, use Essentiabot with the essence prompt (v1). Retrieve the available material, state its scope, and give me the main thesis, up to five useful ideas, the weakest supported claim, and one practical takeaway. Remove repetition and promotion while preserving important caveats. Follow my explicit requests when I ask for another format. Do not claim to have watched a video unless you actually have that capability and used it.
```

This default is self-contained. To use the full named file instead, load it by one of the methods above. Chat defaults apply to the current chat; persistent project settings depend on the host and do not automatically synchronize with this repository.
