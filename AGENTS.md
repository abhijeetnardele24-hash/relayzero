# Autonomous Execution Directive

## 1. Zero Routine Permission Prompts
- **Never pause to ask for permission** for standard engineering tasks: running terminal commands, creating files, modifying code, building projects, running tests, or making Git commits.
- **Never use interactive modals (`ask_question`)** for routine architectural choices, minor clarifications, or routine decisions. Autonomously choose the most robust, high-performance, and standard solution and execute it directly.

## 2. End-to-End Autonomous Execution
- When given a task or bug, proceed end-to-end autonomously through analysis, implementation, automated testing, quality validation, and commits until the goal is fully achieved.
- Proactively fix errors, linter warnings, or test failures encountered along the way without stopping to request user guidance.

## 3. High-Impact Safeguard Threshold
- ONLY halt or request explicit user confirmation for irreversible catastrophic data loss (such as permanently deleting an entire unbacked-up project directory or running an unrecoverable hard reset on remote repositories).
- All normal development, refactoring, and verification tasks must proceed directly without interruption.
