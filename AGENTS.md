# Project Rules

## Project Description
- This is a Python CLI budget app.
- It uses CSV files as the primary data source for income and expense records.
- The app should focus on simple command-line workflows for reading, filtering, and managing budget transactions.

## Coding Rules
- Type hints are required for all functions and public interfaces.
- Keep each function to 20 lines or fewer whenever practical.
- Prefer small, focused functions over large multi-purpose blocks.

## TDD Rules
- Write tests before implementing new behavior.
- Follow the red-green-refactor cycle for every feature or bug fix.
- Do not add production code without first adding or updating the relevant test.

## Quality Rules
- Keep cyclomatic complexity at 5 or below.
- Prefer early returns, small helpers, and simple branching to stay within the complexity limit.

## Test Commands
- Run unit tests with `pytest`.
- Check cyclomatic complexity with `radon cc`.
