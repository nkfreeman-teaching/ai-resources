# Module 3: Working with Context

This module covers the context window, i.e., the working memory an assistant holds while it composes an answer, and the material a student chooses to place in it. Every document, data file, prior turn, and instruction competes for that space, and the quality of an answer depends as much on what is present there as on how the question is phrased. Grounding refers to the practice of pointing an assistant at specific material and requiring it to answer from that material rather than from its general training, which is what makes an answer checkable against a source. Selecting material deliberately is a skill distinct from writing a clever request, because an assistant given the wrong sources will answer confidently from the wrong sources. Managing context also means removing what has gone stale, since a long conversation carries forward earlier turns that may no longer describe the task at hand.

After working through this module, a student should be able to assemble the material an assistant needs before asking anything, write a request that actually uses that material, and judge when an answer is grounded in the supplied sources rather than invented around them. The Prompting Guide 101: Gemini for Google Workspace (October 2024 edition) gives a concrete target for how much context a request should carry, since Google reports that the most fruitful prompts average around 21 words of relevant context while the prompts people typically try run under nine words, and it advises writing prompts in natural language as complete sentences addressed to another person. ChatGPT Prompt Engineering for Developers extends that habit across nine video lessons covering effective prompting and the use of large language models for summarizing, inferring, transforming, and expanding text, which are the four operations a student most often performs on material already supplied as context. Course access is free for a limited time during the DeepLearning.AI learning platform beta. Taken together, the guide and the course move a student from short, underspecified requests toward requests that carry the sources, the task, and the constraints in one place.

The featured tools show what grounded work looks like once the material is assembled. Gemini Notebook (formerly NotebookLM) is built around a set of sources a student supplies, with free-tier notebooks holding up to 50 sources, and it can write and execute code to perform data analysis grounded in those uploaded sources, a capability available to Google AI Ultra users and to Workspace business customers with AI Ultra Access and AI Expanded Access, rolling out to Pro users on the web as of July 2026 and not stated to be part of the free tier. Grammarly for Students, which is free to sign up for as a student, offers an AI Grader that gives feedback based on the student's syllabus along with an estimated grade, although the students page does not state which plan includes the AI Grader. The syllabus case is a compact illustration of the module's argument, since the same draft receives different feedback depending on whether the grading criteria were supplied as context. Students should treat tier and pricing details as subject to change and confirm the current terms on each vendor page before relying on a feature for coursework.

## Resources for this module

<!-- resources: ids=google-notebooklm,google-gemini-workspace-prompting-guide-101,deeplearning-ai-chatgpt-prompt-engineering,grammarly-students -->
### [Gemini Notebook (formerly NotebookLM)](https://notebook.google/)

**Tool**, Google. A notebook tool that works from a student's own uploaded material, up to 50 sources per notebook on the free tier, and can write and execute code for data analysis, although code execution is not stated to be free. *Last verified 2026-09-07.*

### [Prompting Guide 101: Gemini for Google Workspace (October 2024 edition)](https://services.google.com/fh/files/misc/gemini_for_workspace_prompt_guide_october_2024_digital_final.pdf)

**Reading**, Google Workspace. Advice on writing prompts in natural language as complete sentences addressed to another person, noting that the most fruitful prompts average around 21 words of relevant context while typical attempts run under nine. Featured in [Module 2](module-02.md). *Last verified 2026-09-07.*

### [ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/courses/chatgpt-prompt-eng/)

**Course**, DeepLearning.AI (with OpenAI). Nine video lessons on effective prompting and on using large language models to summarize, infer, transform, and expand text, free for a limited time during the learning platform beta. Featured in [Module 2](module-02.md). *Last verified 2026-09-07.*

### [Grammarly for Students](https://www.grammarly.com/students)

**Tool**, Grammarly. Free for a student to sign up for, with an AI Grader that returns feedback based on a course syllabus plus an estimated grade, although the students page does not state which plan includes that grader. *Last verified 2026-09-07.*
<!-- /resources -->
