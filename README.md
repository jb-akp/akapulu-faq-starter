# Give your website a talking FAQ

A reusable agent skill that reads your website, prepares source-backed knowledge and an Akapulu scenario, and helps create a hosted avatar link. Use your coding agent for setup; Akapulu hosts the conversation. The first website integration is a normal link to a call page.

## Quick start (GitHub)

1. Clone or download this repository: `git clone https://github.com/jb-akp/akapulu-faq-starter.git` (or **Code → Download ZIP** and extract it).
2. Open the folder (`akapulu-faq-starter`, or `akapulu-faq-starter-main` from the ZIP) as a project in Codex, Claude Code, or Cursor. You need a coding agent that can read files, run Python and open public web pages.
3. Follow **Start here** below: install the skill, add your Akapulu key to the local `.env` (never in chat, website code or a recording), prepare and review the facts from your website, then create the assistant.

This starter creates a **hosted Akapulu call link** your site can open with a normal button. It is not an embedded SDK widget, and it adds no server, tunnel, screen access or action tools.

## What you need

- Codex, Claude Code, or Cursor Agent with permission to read project files, inspect public pages, and run Python. These are coding-agent workflows, not ordinary web chat uploads.
- Python 3.10 or newer. The helpers use the standard library; no pip packages, Node server, or tunnel are required.
- An Akapulu account and API key for live creation. Put the key in the local `.env`; keep it out of chat, recordings and website code.
- An avatar selected from the Akapulu catalog.

Your coding agent and Akapulu have their own usage costs and limits. Choose a live conversation model your Akapulu account supports; using a model to build the assistant does not mean that model runs its calls. Python runs during setup, not on your website.

## Start here

1. Download and extract the starter ZIP (from GitHub it unzips as `akapulu-faq-starter-main`). Open the extracted folder in your coding agent. That folder can be your new project; you do not have to copy hidden folders by hand.
2. Paste this, replacing the agent name with **Codex**, **Claude Code**, or **Cursor**:

> Read README.md and inspect install.py in this starter. I am using [AGENT NAME]. Check for Python 3.10 or newer, then run install.py for this project with the matching --agent option. Preserve existing instructions, skills and credentials. Do not create live resources yet. Tell me where to add my Akapulu API key locally, without asking me to paste the key into chat.

3. Put `AKAPULU_API_KEY=your-key` in the project's `.env` file, off camera. Keep other existing entries. The installer creates a blank entry only if `.env` does not exist.
4. Start a new agent chat in that same project if the new skill is not discovered. Use the preparation prompt below.

For an existing website project, open that project and give your agent the path to the extracted starter instead. Ask it to install into your website project, preserving existing files. You can also use a fresh folder with a public website URL.

### Installation options

These commands are for your coding agent to run, not required typing for the tutorial. Replace paths with your actual folders.

| App | Command | Installed skill | How to ask for it |
| --- | --- | --- | --- |
| Codex | `python3 /path/to/starter/install.py /path/to/project --agent codex` | `.agents/skills/akapulu-faq/` | `$akapulu-faq` |
| Claude Code | `python3 /path/to/starter/install.py /path/to/project --agent claude` | `.claude/skills/akapulu-faq/` | `/akapulu-faq` |
| Cursor Agent | `python3 /path/to/starter/install.py /path/to/project --agent cursor` | `.agents/skills/akapulu-faq/` | Ask to use the `akapulu-faq` skill |

Only the chosen destination is installed. Codex and Cursor share a supported project directory. Claude Code gets the same files in its own project directory. Repeating the installer preserves files; conflicting versions stop for review. Existing AGENTS.md, CLAUDE.md, credentials and unrelated skills are not replaced.

If discovery fails, use the explicit path: “Read [installed skill path]/SKILL.md and follow it for this task, including its referenced scripts and API instructions.” You need an agent with file, terminal and website access; this is not a promise that every chat app can execute the workflow.

## Prepare first

This wording works without an app-specific slash command:

> Use the installed akapulu-faq skill to prepare an FAQ assistant from [MY WEBSITE URL]. Read the relevant pricing, FAQ and policy pages. Show me the facts you captured, pages you read and anything missing. Validate the draft. Prepare only; do not create live resources yet. Do not add screen access or action tools.

Review `akapulu/knowledge.txt` alongside your site. Check prices, billing periods, limits and exceptions. The skill produces text, not a PDF. If facts are absent or contradictory, resolve that before publishing.

## Create after reviewing

Select an avatar at https://akapulu.com/catalog/ and copy its ID. Then say:

> The reviewed facts look correct. Create a new knowledge base and FAQ scenario in my Akapulu account using this project's .env key and avatar ID [MY AVATAR UUID]. Choose a conversation model my account supports. Wait for knowledge processing, verify the saved setup, and return the hosted call URL. Save returned resource IDs immediately so an interrupted run can resume without duplicates. Do not modify an existing assistant.

Use the URL returned by **your own run**. No example URL or avatar ID belongs in your new assistant's configuration.

## Test, then link

Ask about a documented fact, ask a follow-up, and ask something the website does not answer. Confirm that the avatar does not claim to contact staff, change accounts, or see your screen. Listen to the actual replies; passing file checks does not prove conversation quality.

After testing:

> Add a clearly labeled “Talk to our AI assistant” link to my website using [MY HOSTED CALL URL]. Keep the readable FAQ available. Open the hosted Akapulu call page; do not embed an iframe or put an API key in website code.

If you use a website builder, add a normal button and paste your hosted URL into its link setting. This does not require switching website platforms.

## Compatibility and verification

Installation and offline helper checks are tested for all three target directories. The hosted workflow was previously rehearsed with Codex. Claude Code and Cursor have **not** had a complete agent-driven website-to-live-call rehearsal in this package. Their setup paths follow their documented skill support; do not treat that as proof of identical agent behavior.

References checked October 1, 2026: [Claude Code skills](https://code.claude.com/docs/en/skills) and [Cursor skills](https://cursor.com/docs/skills).

The source helper captures selected pages; it is not a full-site crawler. JavaScript-only pages may need browser inspection. Every knowledge passage is checked against captured source text, but this cannot guarantee current policy or complete context. Updated website content must be recaptured, reviewed and uploaded; editing a local text file alone does not update a live knowledge base.
