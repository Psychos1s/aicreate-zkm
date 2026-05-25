# /interview Command

When this command is used, activate the interview skill to guide structured conversations using Advanced Elicitation methodology.

Description:
- Interactive interview agent that guides users through structured Advanced Elicitation workflows
- Automatically selects from 50 heuristic methods in references/methods.csv based on context
- Loads interview goals from references/target.yaml
- Generates interview reports upon completion

Usage:
- `/interview` - Start an interactive interview session

The interview skill will:
1. Load method library and analyze current context
2. Automatically select the most appropriate elicitation method
3. Guide conversation through structured questions
4. Dynamically adapt based on user responses
5. Apply additional methods as needed
6. Generate a summary report (interview.md) when complete
