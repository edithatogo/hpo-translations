# External-action safety policy

All work in this repository is local-only by default.

Do not push, open or update a pull request, open or update an issue, post a
comment or review, add a reaction or label, close or reopen an item, create a
release, publish an artifact, submit a form, or contact an external person or
project unless the user gives explicit approval for that external action in
the current conversation.

General continuation language such as "proceed", "continue", "next steps",
or approval to implement or commit local work is not approval for an external
write. Approval must identify, or unambiguously accept a proposal identifying,
the external target and action. Ask before acting when the scope is uncertain.

Read-only inspection of public or already-authorized hosted state is allowed.
Never use a read-only audit as a reason to reply, acknowledge, close, label,
react to, or otherwise modify an external item.

Repository commits do not authorize pushes. The local pre-push hook is an
additional fail-closed control and must not be bypassed without the user's
explicit approval for the exact push.
