# Instructions for Claude

## Project context
Read `CONTEXT.md` at the root of the project at the start of each session. It contains the current state of the code, the file structure, and the next pending step.

## Language
- Respond to the user in Spanish or English.
- All project edits — code, configuration files, documentation, comments, docstrings — must be written in English without exception.

## Collaboration approach

The user is a Python beginner. The priority is understanding — not writing code independently.

### Core rule
**Never implement anything without first explaining what will be done and why, and waiting for the user's approval.**

### How to work together
- Implement code collaboratively — Claude writes, user supervises and asks questions freely
- Before any change: explain the reasoning, the approach, and what the result will look like
- After the user approves: implement and explain key decisions inline
- Answer questions at any point — no need to follow a fixed sequence

### What to avoid
- Implementing features silently or without explanation
- Forcing the user to write code on their own
- Assuming the user wants to figure it out — default to explaining
