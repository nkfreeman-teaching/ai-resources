# Module 4: Loops and Harness Engineering

This module covers the agentic loop, i.e., the cycle in which an agent plans an action, acts, observes the result, and repeats until the goal is met or a decision requires a person. Harness engineering is the companion subject, and it concerns the tools, permissions, checks, and feedback (e.g., a test suite, a linter, or a rule that asks before a file is deleted) an agent works inside so that it can run, test, and correct its own work. The harness is the part of the system an analyst can actually design, since the model arrives fixed and the surrounding software determines whether a mistake surfaces early or late. Much of the work here is about feedback, i.e., arranging matters so that a failing test, a type error, or a rejected permission reaches the agent while it can still act on the information. The scope of this module is the loop and the software around it rather than the choice of model.

A student who finishes this module should be able to set up an agent so that it verifies its own work rather than reporting completion on faith. That means giving the agent a way to run the code it writes, a check that fails loudly when the output is wrong (e.g., a row count that must match a known total), and a permission boundary that keeps destructive actions under review. It also means reading an agent transcript critically, i.e., following the plan, act, and observe sequence to find the step at which the agent lost track of the goal. Students should be able to explain why a task that fails in one harness can succeed in another with the same model behind it. The measure of success in this module is whether the loop closes without a person patching each step by hand.

The resources below cover the practice, the tooling, and the surrounding conversation. Matt Pocock (AI Hero) publishes tutorials and courses on working effectively with AI coding agents, including how to build skills for them, which is the closest match to the subject of this module among these entries. GitHub Copilot Student is available at no cost to verified students and includes unlimited code completions plus an allowance of GitHub AI Credits, with limited chat and agent usage confined to models available through auto model selection, so a loop can be run without a paid subscription. Cursor can be started on a general free plan open to anyone rather than a student-specific offer, and it also runs student promotions and discounts through on-campus and online events and a campus newsletter that students can join for early access. Latent Space: The AI Engineer Podcast describes itself as made by and for the rising class of AI Engineers, covering the business and technology of AI, and it states that it has crossed 200,000 subscribers and 10 million viewers across all its channels. We recommend running a small task in one of the two editors before listening widely, since the vocabulary of the podcast reads more clearly once a loop has been closed at least once.

## Resources for this module

<!-- resources: ids=matt-pocock,github-copilot-student,cursor-ai-editor,latent-space-podcast -->
### [Matt Pocock (AI Hero)](https://www.aihero.dev/)

**Person**, Matt Pocock. Tutorials and courses on working effectively with AI coding agents, i.e., tools that read, write, and run code on a developer's behalf, including how to build skills for those agents. Featured in [Module 2](module-02.md). *Last verified 2026-09-07.*

### [GitHub Copilot Student](https://education.github.com/pack)

**Tool**, GitHub (Microsoft). Available at no cost to verified students, the plan includes unlimited code completions plus an allowance of GitHub AI Credits, with chat and agent usage limited and restricted to models available through auto model selection. *Last verified 2026-09-07.*

### [Cursor](https://cursor.com/students)

**Tool**, Anysphere (Cursor). Anyone, including students, can begin on the general free plan, which is not a student-specific offer, and a campus newsletter carries early access to events and exclusive discounts through on-campus and online promotions. *Last verified 2026-09-07.*

### [Latent Space: The AI Engineer Podcast](https://www.latent.space/about)

**Podcast**, swyx, with rotating cohosts. Made by and for the rising class of AI engineers, this show covers the business and the technology of AI together, and it has crossed 200,000 subscribers and 10 million viewers across all its channels. *Last verified 2026-09-07.*
<!-- /resources -->
