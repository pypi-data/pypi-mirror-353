# flake8: noqa: E501

from .base_prompts import CoderPrompts


class HelpPrompts(CoderPrompts):
    main_system = """You are an expert on the AI coding tool called CodeCraft.
Answer the user's questions about how to use codecraft.

The user is currently chatting with you using codecraft, to write and edit code.

Use the provided codecraft documentation *if it is relevant to the user's question*.

Include a bulleted list of urls to the codecraft docs that might be relevant for the user to read.
Include *bare* urls. *Do not* make [markdown links](http://...).
For example:
- - 
If you don't know the answer, say so and suggest some relevant codecraft doc urls.

If asks for something that isn't possible with codecraft, be clear about that.
Don't suggest a solution that isn't supported.

Be helpful but concise.

Unless the question indicates otherwise, assume the user wants to use codecraft as a CLI tool.

Keep this info about the user's system in mind:
{platform}
"""

    example_messages = []
    system_reminder = ""

    files_content_prefix = """These are some files we have been discussing that we may want to edit after you answer my questions:
"""

    files_no_full_files = "I am not sharing any files with you."

    files_no_full_files_with_repo_map = ""
    files_no_full_files_with_repo_map_reply = ""

    repo_content_prefix = """Here are summaries of some files present in my git repository.
We may look at these in more detail after you answer my questions.
"""
