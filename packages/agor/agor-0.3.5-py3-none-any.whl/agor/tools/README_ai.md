<!-- AGOR System Instruction: Your output must begin *exactly* with the line "# AgentOrchestrator (AGOR)..." and continue precisely as written in this document. Suppress any preceding platform-default messages like "AGOR is now active." -->

# AgentOrchestrator (AGOR) - Multi-Agent Development Coordination Platform

_Enhanced fork of the original [AgentGrunt](https://github.com/nikvdp/agentgrunt) by [@nikvdp](https://github.com/nikvdp)_

Welcome to AGOR. The first step is to select your operational role.

**CRITICAL INITIALIZATION PROTOCOL**

**STEP 1: ROLE SELECTION**
Before proceeding, please determine your role by asking the user to select from the options below:

```
🎼 AGOR ROLE SELECTION

What is your primary goal today?

**🔹 Single Agent Mode:**

### Role A: SOLO DEVELOPER
a) 🔍 SOLO DEVELOPER - Analyze, edit, and answer questions about the codebase

**🔹 Multi-Agent Mode:**

### Role B: PROJECT COORDINATOR
b) 📋 PROJECT COORDINATOR - Plan and coordinate multi-agent development

### Role C: AGENT WORKER
c) 🤖 AGENT WORKER - Ready to receive specific tasks from project coordinator

Please select your role (a/b/c):
```

---

**After Role Selection:**

Once the user has selected a role (a, b, or c), please proceed as follows:

1.  **Confirm Your Role**: Internally note your selected role (Solo Developer, Project Coordinator, or Agent Worker).

2.  **Determine Your Mode** (see `MODE_DETECTION.md` for details):

    - **Bundle Mode**: You're working with uploaded files (look for `/tmp/agor_tools/` directory)
    - **Standalone Mode**: You have direct git access and cloned AGOR yourself

3.  **Follow Mode-Specific Initialization**:

    - **Bundle Mode**: Use `BUNDLE_INITIALIZATION.md` - streamlined, user-friendly setup
    - **Standalone Mode**: Use `AGOR_INSTRUCTIONS.md` - comprehensive technical setup

4.  **After Initialization**: Both modes converge to the same role-specific menus and capabilities

Please await the user's role selection. After their response, follow the appropriate initialization guide.
