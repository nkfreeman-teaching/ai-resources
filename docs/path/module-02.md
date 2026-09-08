# Module 2: Skills and Structured Prompting

This module covers structured prompting, i.e., the practice of writing a request with named parts (role, task, constraints, output format, and examples) rather than as a single unstructured sentence. A structured prompt states what part the assistant is playing, what work is being asked for, what limits apply, what shape the answer should take, and what a good answer looks like. The module then covers skills, i.e., a written procedure that an assistant or coding agent can follow whenever a task recurs, which turns a prompt that worked once into one that can be run again. The distinction matters for analytics work, where the same request (e.g., a weekly summary of a standing data pull) is issued many times with small variations. A prompt written for one occasion is discarded after use, whereas a skill is stored, revised, and shared with other people on a team.

A student who completes this module should be able to write a prompt whose parts are explicit and to say what each part is doing in the request. The student should also be able to state the intended output format before asking for the work, since a request that names the shape of the answer produces a result that needs less rework. A further outcome is the ability to recognize when a prompt has been reused often enough to be worth packaging as a skill, and to write that skill as a procedure another person could read and follow. These outcomes concern ordinary business tasks (e.g., drafting a summary, reformatting a table, or classifying a list of open-ended comments) rather than programming problems. Students who reach this point are ready for agent work, where the same structure governs longer sequences of actions.

Best Practices for Prompt Engineering for 2026 (Claude) advises telling the assistant exactly what output is wanted, asking explicitly when a full and detailed answer is needed, and stating what the output should include rather than only what task to perform. Prompting Guide 101: Gemini for Google Workspace (October 2024 edition) reports that the most fruitful prompts average around 21 words of relevant context, while the prompts people typically try run under nine words, and it advises writing prompts in natural language, as complete sentences addressed to another person. ChatGPT Prompt Engineering for Developers runs nine video lessons on effective prompting and on using large language models for summarizing, inferring, transforming, and expanding text, with access free for a limited time during the DeepLearning.AI learning platform beta. Claude 101 (Anthropic Academy) consists of 13 lessons and one quiz, takes about 2.5 hours to complete, and is marked free to access in its course page's structured data, which makes it a reasonable single sitting for a student who wants a guided start. Matt Pocock (AI Hero) publishes tutorials and courses on working effectively with AI coding agents, including how to build skills for them, and is the resource to follow once the packaging of prompts becomes the main interest. We recommend the two guides before either course, since both guides can be read in a sitting and they establish the habits the courses then exercise at length.

## Resources for this module

<!-- resources: ids=claude-prompt-engineering-best-practices,google-gemini-workspace-prompting-guide-101,deeplearning-ai-chatgpt-prompt-engineering,anthropic-academy-claude-101,matt-pocock -->
### [Best Practices for Prompt Engineering for 2026 (Claude)](https://claude.com/blog/best-practices-for-prompt-engineering)

**Reading**, Anthropic. Guidance on telling Claude exactly what output is wanted, stating what that output should include rather than only what task to perform, and asking explicitly when a full and detailed answer is needed. *Last verified 2026-09-07.*

### [Prompting Guide 101: Gemini for Google Workspace (October 2024 edition)](https://services.google.com/fh/files/misc/gemini_for_workspace_prompt_guide_october_2024_digital_final.pdf)

**Reading**, Google Workspace. Advice on writing prompts in natural language as complete sentences addressed to another person, noting that the most fruitful prompts average around 21 words of relevant context while typical attempts run under nine. Featured in [Module 3](module-03.md). *Last verified 2026-09-07.*

### [ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/courses/chatgpt-prompt-eng/)

**Course**, DeepLearning.AI (with OpenAI). Nine video lessons on effective prompting and on using large language models to summarize, infer, transform, and expand text, free for a limited time during the learning platform beta. Featured in [Module 3](module-03.md). *Last verified 2026-09-07.*

### [Claude 101 (Anthropic Academy)](https://academy.claude.com/courses/claude-101)

**Course**, Anthropic. Thirteen lessons and one quiz taking about 2.5 hours to complete, marked free to access in the course page's structured data, which gives students a first structured pass at working with Claude. *Last verified 2026-09-07.*

### [Matt Pocock (AI Hero)](https://www.aihero.dev/)

**Person**, Matt Pocock. Tutorials and courses on working effectively with AI coding agents, i.e., tools that read, write, and run code on a developer's behalf, including how to build skills for those agents. Featured in [Module 4](module-04.md). *Last verified 2026-09-07.*
<!-- /resources -->
