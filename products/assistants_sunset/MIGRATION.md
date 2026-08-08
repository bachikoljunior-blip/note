# Migration checklist

1. Run `scan.py` and save the JSON report.
2. Inventory every Assistant's model, instructions, tools and response format.
3. Recreate each configuration as a versioned Prompt in the OpenAI dashboard.
4. Replace Threads with Conversations. If a Thread is created with messages, convert those messages to Conversation `items`; do not only rename the method.
5. Replace Runs with Responses. Supply a model or Prompt, input, and a Conversation where state should persist.
6. Rewrite polling, streaming and tool-call loops for the Responses lifecycle.
7. Decide how stored `assistant_id`, `thread_id` and `run_id` records will be retired or mapped. Back up data before changing it.
8. Revalidate file search, vector stores and code interpreter against current tool documentation.
9. Run `codemod.py` without `--apply`, review the unified diff, then apply the safe subset if appropriate.
10. Run unit, integration and end-to-end tests in a non-production environment.
11. Deploy gradually, monitor errors and keep a rollback path until the migration is stable.

The official guide makes clear that Assistants become Prompts, Threads become Conversations, and Runs become Responses. These are conceptual migrations, not universal text substitutions.
