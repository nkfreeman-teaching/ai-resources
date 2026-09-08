# Module 5: Building a Small Agent End to End

This module assembles one small working agent from its parts and then runs it on a real task. An agent, in the sense used here, is a goal handed to a model together with a tool or two (e.g., a function that reads a file or queries a table), a loop that lets the model act and observe the result, and a runtime, i.e., the environment in which the code actually executes. The work of the module is putting those parts in one place rather than studying each of them in isolation, since the parts reveal their behavior only when they run together. Students choose a task small enough to finish in a single sitting (e.g., summarizing each file in a folder into one table), wire the pieces together, and then inspect the record of what the agent did at each step. The inspection matters as much as the building, because an agent that reached the right answer by the wrong route will fail on the next task.

A student who finishes this module should be able to name each part of a small agent and say what breaks when that part is missing. The practical outcome is a running program, however modest, built from four pieces: a goal stated in a prompt, a model call, one or two tools the model may invoke, and a loop that continues until the goal is met or a limit is reached. A second outcome is the habit of reading the trace, i.e., the sequence of model outputs, tool calls, and tool results that a run produces. Students should also be able to judge when an agent is the wrong shape for a problem, since many tasks are better served by a single prompt or by ordinary code. The scope of the module stops at one agent on one task, and questions of scale, cost, and deployment are left to later work.

The featured resources supply both the instruction and the place to run the code. OpenAI Academy teaches practical AI skills through hands-on learning about how AI works and how to build agents and workflows, sign-up is free and open to anyone, and learners can earn OpenAI Course Completion Certificates. Generative AI for Beginners offers 21 lessons on building generative AI applications, each covering its own topic and each able to be studied in any order, so a student may take the first lesson on what generative AI is and how large language models work and then move to whichever lesson matches the part under construction. Google Colab gives free access to computing resources including GPUs and TPUs for machine learning projects, and it lets users generate, explain, and debug code in natural language in real time, which keeps the runtime out of the way while the agent itself is being assembled. Allie K. Miller offers The AI Fast Track, a free five-day email course that moves from AI basics to building tools without coding, taught using Claude. Miller previously led Amazon Web Services' Global Machine Learning for Startups and Venture Capital organization and now works as an AI advisor and investor who trains and advises Fortune 500 companies, and the course suits a student who wants the shape of this work before writing any code.

## Resources for this module

<!-- resources: ids=openai-academy-courses,microsoft-generative-ai-for-beginners,google-colab-ai,allie-k-miller -->
### [OpenAI Academy](https://academy.openai.com/pages/courses)

**Course**, OpenAI. Sign-up is free and open to anyone, and the courses teach practical AI skills through hands-on learning about how AI works and how to build agents and workflows, with course completion certificates available. *Last verified 2026-09-07.*

### [Generative AI for Beginners](https://github.com/microsoft/generative-ai-for-beginners)

**Course**, Microsoft Cloud Advocates. Twenty-one lessons on building generative AI applications, each covering its own topic and open to study in any order, beginning with what generative AI is and how large language models work. *Last verified 2026-09-07.*

### [Google Colab](https://colab.research.google.com/)

**Tool**, Google. Free access to computing resources including GPUs and TPUs for machine learning projects, with the ability to generate, explain, and debug code in natural language in real time. *Last verified 2026-09-07.*

### [Allie K. Miller](https://www.alliekmiller.com/)

**Person**, Allie K. Miller. A former leader of Amazon Web Services' Global Machine Learning for Startups and Venture Capital organization who now advises and trains Fortune 500 companies, and who offers The AI Fast Track, a free five-day email course taught using Claude. Featured in [Module 7](module-07.md). *Last verified 2026-09-07.*
<!-- /resources -->
