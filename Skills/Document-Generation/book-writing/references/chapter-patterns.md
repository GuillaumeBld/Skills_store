# Chapter Structural Patterns

## The Origin Story Pattern

**Best for:** Projects with interesting motivation, pivots, or domain context.

### Structure
1. **The World Before** — What existed before this project? What was broken, slow, or painful?
2. **The Insight** — What realization or event triggered the project?
3. **The Approach** — High-level strategy chosen. Why this approach over alternatives?
4. **The Result** — What does the project look like today? Key metrics or outcomes.
5. **What's Next** — Where is the project heading?

### Example Opening
> "In 2023, deploying a change to production took our team an average of 4 hours. Not because the deployment itself was complex, but because the manual verification checklist had grown to 47 items. This project was born the day someone asked: 'What if the checklist verified itself?'"

---

## The Guided Tour Pattern

**Best for:** Complex systems where understanding flow matters more than individual components.

### Structure
1. **The Entry Point** — Where does a user/request/data enter the system?
2. **Stop 1** — First component encountered. What happens here? Why?
3. **Stop 2** — Next component. How did we get here from Stop 1?
4. **Stop N** — Continue through the system
5. **The Exit** — What comes out the other end?
6. **Behind the Scenes** — Infrastructure, monitoring, error handling

### Example Opening
> "Let's follow a search query from the moment a user types 'running shoes' to the moment they see results. Along the way, we'll meet the tokenizer, the ranking engine, and the cache — and understand why each exists."

---

## The Building Blocks Pattern

**Best for:** Modular projects, libraries, plugin systems.

### Structure
1. **The Foundation** — Core concepts that everything else builds on
2. **Block A** — First module, self-contained explanation
3. **Block B** — Second module, with connections to A
4. **Block C** — Third module, with connections to A and B
5. **Assembly** — How the blocks combine into the full system
6. **Extending** — How to add new blocks

### Example Opening
> "This project is built from five independent modules, each of which can be understood on its own. But the real power emerges when they work together. Let's start with the simplest one."

---

## The Problem-Solution Pattern

**Best for:** Tools, utilities, CLIs, focused libraries.

### Structure
1. **Problem 1** — Describe the pain point
2. **Solution 1** — Show how the tool solves it
3. **Problem 2** — Next pain point
4. **Solution 2** — Next solution
5. **Advanced Usage** — Combining solutions for complex scenarios
6. **Under the Hood** — How the tool works internally (optional)

### Example Opening
> "Managing database migrations shouldn't require a PhD. But if you've ever had a migration fail halfway through production data, you know the fear. Here's how this tool makes migrations safe."

---

## The Onboarding Pattern

**Best for:** Projects where getting started is the priority, developer tools, frameworks.

### Structure
1. **Quick Start** — Install and run in under 5 minutes
2. **First Real Task** — Build something useful, guided step-by-step
3. **What Just Happened** — Explain the concepts behind what they just did
4. **Going Deeper** — More advanced features, building on the first task
5. **Architecture** — Now that they have hands-on experience, explain the design
6. **Reference** — Where to find detailed documentation

### Example Opening
> "By the end of this chapter, you'll have a working API with authentication, database access, and automatic documentation. It'll take about 10 minutes. Let's start."

---

## The Decision Record Pattern

**Best for:** Projects with non-obvious architecture decisions, enterprise systems.

### Structure
1. **The Requirement** — What did the system need to do?
2. **Options Considered** — What approaches were evaluated?
3. **Trade-offs** — Pros and cons of each option
4. **The Decision** — What was chosen and why
5. **Consequences** — What this decision means for the codebase
6. **Living With It** — How to work within these constraints

### Example Opening
> "Every architecture has opinions. This project chose PostgreSQL over MongoDB, REST over GraphQL, and monolith over microservices. Each choice was deliberate. Here's why."

---

## Combining Patterns

Most books use different patterns for different chapters:

| Chapter | Pattern | Why |
|---------|---------|-----|
| Introduction | Origin Story | Sets context and motivation |
| Architecture | Guided Tour | Best way to understand complex systems |
| Modules | Building Blocks | Each module is self-contained |
| Getting Started | Onboarding | Hands-on learning |
| Design Decisions | Decision Record | Explains non-obvious choices |

The scanner agent selects patterns per chapter based on the project's characteristics.
