---
name: superpowers
description: Foundational skill that teaches agents how to use skills to their best capabilities. Enables structured development workflows using test-driven development, systematic debugging, collaborative planning, subagent-driven development, and proper code review. Helps agents work systematically rather than ad-hoc, emphasizing TDD, YAGNI, DRY principles, and evidence-based verification. Use when agents need to work on software development tasks, debug issues, plan implementations, execute tasks in batches, or collaborate on code reviews. Based on obra/superpowers methodology for Claude Code.
---

# Superpowers: Using Skills to Best Capabilities

**Foundational skill that enables agents to use skills to their best capabilities.**

This skill teaches agents how to work systematically using structured workflows, test-driven development, systematic debugging, collaborative planning, and proper code review practices. It transforms ad-hoc development into structured, repeatable, high-quality workflows.

**Inspired by:** [obra/superpowers](https://github.com/obra/superpowers) - Core skills library for Claude Code

## Core Philosophy

**Skills employ progressive disclosure architecture for efficiency:**
1. **Metadata loading** (~100 tokens): Claude scans available Skills to identify relevant matches
2. **Full instructions** (<5k tokens): Load when Claude determines the Skill applies
3. **Bundled resources**: Files and executable code load only as needed

This design allows multiple Skills to remain available without overwhelming Claude's context window.

## Key Principles

### Test-Driven Development (TDD)
- **RED-GREEN-REFACTOR** cycle: Write failing test first, watch it fail, write minimal code, watch it pass, refactor
- Always write tests before code
- Delete code written before tests
- Tests verify correctness, not just coverage

### Systematic over Ad-hoc
- Process over guessing
- Evidence-based decisions
- Structured workflows for complex tasks
- Root cause analysis before fixes

### Complexity Reduction
- Simplicity as primary goal
- YAGNI (You Aren't Gonna Need It)
- DRY (Don't Repeat Yourself)
- Remove unnecessary abstractions

### Evidence over Claims
- Verify before declaring success
- Show proof, not just assertions
- Test actual behavior, not assumptions
- Measure, don't guess

## Core Workflow

### 1. Before Writing Code: Brainstorming

**When to use:** Before starting implementation, especially for complex features.

**Process:**
- Step back and ask what the user is really trying to do
- Refine rough ideas through questions
- Explore alternatives
- Present design in digestible chunks for validation
- Save design document for reference

**Key Questions:**
- What problem are we actually solving?
- What are the constraints?
- What are alternative approaches?
- What does success look like?
- How will we verify it works?

### 2. After Design Approval: Git Worktrees

**When to use:** After design is approved, before implementation.

**Process:**
- Create isolated workspace on new branch
- Run project setup
- Verify clean test baseline
- Isolate changes from main branch

**Benefits:**
- Parallel development without conflicts
- Clean testing environment
- Easy rollback if needed

### 3. With Approved Design: Writing Plans

**When to use:** After design approval, before implementation.

**Process:**
- Break work into bite-sized tasks (2-5 minutes each)
- Every task has:
  - Exact file paths
  - Complete code implementation
  - Verification steps
- Emphasize TDD: tests first, then code

**Output Format:**
```
Task 1: Create test for X
- File: tests/test_x.py
- Code: [complete test code]
- Verification: Run tests, should fail (RED)

Task 2: Implement X
- File: src/x.py
- Code: [complete implementation code]
- Verification: Run tests, should pass (GREEN)
```

### 4. With Plan: Executing Plans

**When to use:** After plan is created.

**Two Approaches:**

**A. Subagent-Driven Development:**
- Dispatch fresh subagent per task
- Two-stage review:
  1. Spec compliance (does it match the plan?)
  2. Code quality (is it well-written?)
- Continue forward after approval

**B. Batch Execution:**
- Execute tasks in batches with human checkpoints
- Review progress at checkpoints
- Adjust plan if needed

### 5. During Implementation: Test-Driven Development

**When to use:** Throughout implementation.

**RED-GREEN-REFACTOR Cycle:**

1. **RED**: Write failing test
   ```python
   def test_new_feature():
       result = my_function()
       assert result == expected_value
   ```
   - Run test, watch it fail
   - Commit (tests failing is expected)

2. **GREEN**: Write minimal code to pass
   ```python
   def my_function():
       return expected_value  # Minimal implementation
   ```
   - Run test, watch it pass
   - Commit (now tests pass)

3. **REFACTOR**: Improve code quality
   - Extract common patterns
   - Remove duplication
   - Improve naming
   - Ensure tests still pass
   - Commit (improved, tests still pass)

**Rules:**
- Never write code without a test first
- If code exists without tests, write tests first, then refactor
- Delete code written before tests
- Tests verify correctness, not just coverage

### 6. Between Tasks: Code Review

**When to use:** After task completion, before moving to next.

**Requesting Code Review:**
- Review against plan (spec compliance)
- Check code quality (readability, maintainability)
- Report issues by severity:
  - **Critical**: Blocks progress, must fix
  - **Major**: Should fix, but can proceed
  - **Minor**: Nice to have, optional

**Receiving Code Review:**
- Respond to feedback constructively
- Ask clarifying questions if needed
- Fix issues systematically
- Verify fixes with tests

### 7. When Tasks Complete: Finishing Development Branch

**When to use:** After all tasks are complete.

**Process:**
- Verify all tests pass
- Review all changes
- Present options:
  - Merge to main
  - Create pull request
  - Keep for further work
  - Discard if abandoned
- Clean up worktree if merged/discarded

## Systematic Debugging

**When to use:** When encountering bugs or unexpected behavior.

**4-Phase Process:**

1. **Reproduce**: Make the bug happen reliably
   - Write a test that reproduces the issue
   - Minimize to simplest case
   - Document steps to reproduce

2. **Isolate**: Narrow down the cause
   - Root cause tracing: Trace execution path
   - Defense in depth: Check multiple layers
   - Condition-based waiting: Wait for specific states

3. **Fix**: Apply minimal fix
   - Fix only what's broken
   - Don't refactor while fixing
   - Write test first (if not exists)

4. **Verify**: Ensure it's actually fixed
   - Run all tests
   - Test edge cases
   - Verify no regressions
   - Document fix

## Using Skills Effectively

### Skill Discovery
- Skills trigger automatically via Claude's built-in system
- Skills match based on description in SKILL.md frontmatter
- Multiple skills can compose automatically
- No manual "calling" needed

### Skill Composition
- Skills can work together
- Loaded on-demand when relevant
- Progressive disclosure: metadata first, full content when needed
- Resources load only as needed

### Best Practices
- Let skills trigger automatically (don't force them)
- Trust the skill discovery system
- Compose multiple skills when appropriate
- Focus on task, skills will activate when needed

## Integration with skill-library-manager

**How superpowers works with skill-library-manager:**

- **skill-library-manager**: Manages lifecycle of skills (create, search, update, sync) in the Skills Librairie repository
- **superpowers**: Teaches how to USE skills effectively for development workflows
- **Together**: Complete skill ecosystem - management + effective usage

**They complement each other but serve different purposes:**

**skill-library-manager:**
- Focus: Skill lifecycle management (create, search, update, sync)
- Scope: Skills Librairie repository management
- Purpose: Organize and maintain the skills collection

**superpowers:**
- Focus: Teaching agents how to work systematically with skills
- Scope: Development workflow methodology
- Purpose: Enable agents to use skills to their best capabilities

**They work together, not in hierarchy:**
- skill-library-manager helps discover and manage skills
- superpowers helps agents use skills effectively in workflows
- Both are meta-skills but serve complementary roles
- skill-library-manager is NOT included within superpowers - they are separate, complementary skills

**Workflow:**
1. Use `skill-library-manager` to discover/install relevant skills from Skills Librairie
2. Use `superpowers` to work systematically with those skills using TDD and structured workflows
3. Skills trigger automatically based on task context
4. Follow TDD, systematic debugging, and review practices from superpowers
5. Use `skill-library-manager` to create new skills following superpowers best practices

## Mandatory Workflows

**These workflows are mandatory, not suggestions:**

- **Before coding**: Brainstorm and design
- **With design**: Write implementation plan
- **During coding**: Follow TDD (RED-GREEN-REFACTOR)
- **Between tasks**: Request code review
- **After tasks**: Finish development branch properly
- **When debugging**: Use systematic debugging (4-phase process)
- **Before completion**: Verify everything works

## Examples

### Example 1: Feature Development

```
User: "Add user authentication"

Agent (using superpowers):
1. Brainstorm: Questions about auth method, requirements, security
2. Design: Present authentication flow, security considerations
3. Plan: Break into tasks (test for login, implement login, test for logout, etc.)
4. Execute: Follow TDD for each task
5. Review: Request code review after each major task
6. Finish: Verify tests, create PR
```

### Example 2: Bug Fix

```
User: "Login is broken"

Agent (using superpowers):
1. Reproduce: Write test that reproduces login failure
2. Isolate: Debug to find root cause (e.g., session not persisting)
3. Fix: Write test first, then fix session handling
4. Verify: Run all tests, check edge cases, verify no regressions
```

### Example 3: Refactoring

```
User: "Refactor payment processing code"

Agent (using superpowers):
1. Brainstorm: Identify what needs refactoring and why
2. Plan: Break into small refactoring tasks
3. Execute: For each task, write tests first (RED), refactor (GREEN), verify (REFACTOR)
4. Review: Request code review after each major change
5. Finish: Verify all tests pass, no regressions
```

## Resources

- **Superpowers Repository**: https://github.com/obra/superpowers
- **Superpowers Lab**: https://github.com/obra/superpowers-lab (experimental skills)
- **Skills Explained**: Official Anthropic guide on progressive disclosure
- **TDD Best Practices**: Test-Driven Development by Example (Kent Beck)

## Key Takeaways

1. **Skills trigger automatically** - Trust the system, don't force them
2. **Test-driven development** - Always tests first (RED-GREEN-REFACTOR)
3. **Systematic workflows** - Process over guessing
4. **Evidence-based** - Verify before declaring success
5. **Composable** - Multiple skills work together automatically
6. **Progressive disclosure** - Efficient context usage

**Remember**: Skills are tools that help you work better. Use them systematically, not ad-hoc.
