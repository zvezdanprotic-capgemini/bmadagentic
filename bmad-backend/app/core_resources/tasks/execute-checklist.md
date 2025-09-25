# Execute Checklist Task

## Description

This task guides the execution of a checklist against a document or system to validate its completeness and quality. It's designed to provide a structured review process with detailed feedback.

## Parameters

- `checklist`: The checklist to execute (e.g., architect-checklist, qa-checklist)
- `target`: The document or system to validate against the checklist

## Process

1. **Checklist Selection**
   - If no checklist is specified, default to one appropriate for your agent role
   - For Architect agents, default to architect-checklist.md
   - Confirm access to the checklist file before proceeding

2. **Target Identification**
   - Determine what you're validating (document, system, code, etc.)
   - If no specific target is provided, ask the user what should be validated
   - For document validation, ensure you have access to the complete document

3. **Validation Preparation**
   - Review the checklist structure and validation criteria
   - Understand the methodology required for validation
   - Explain to the user the validation process you'll follow

4. **Systematic Review**
   - Process each section of the checklist in order
   - For each item, evaluate the target against the checklist criteria
   - Document compliance level (full, partial, non-compliant, or not applicable)
   - Provide specific evidence supporting your assessment

5. **Results Compilation**
   - Summarize the validation results
   - Highlight strengths and areas for improvement
   - Quantify the level of compliance where appropriate
   - Prioritize recommendations based on impact and implementation effort

## Output Format

```
# Checklist Execution Report: [Checklist Name]

## Executive Summary
- Overall Assessment: [High/Medium/Low]
- Key Strengths: [List 3-5 key strengths]
- Critical Gaps: [List 3-5 critical gaps]
- Recommendations: [Summarize top recommendations]

## Detailed Results

### [Section Name]
- Pass Rate: [x/y items]
- Strengths:
  - [Specific strength with evidence]
  - [Specific strength with evidence]
- Gaps:
  - [Specific gap with evidence]
  - [Specific gap with evidence]
- Recommendations:
  - [Specific recommendation]
  - [Specific recommendation]

[Repeat for each section]

## Improvement Action Plan
1. [High priority action]
2. [High priority action]
3. [Medium priority action]
4. [Medium priority action]
5. [Lower priority action]
```

## Best Practices

1. **Be Specific**: Provide concrete examples from the target that support your assessment
2. **Be Balanced**: Highlight both strengths and improvement areas
3. **Be Practical**: Ensure recommendations are actionable and prioritized
4. **Be Thorough**: Cover all applicable checklist items systematically
5. **Be Clear**: Use evidence-based reasoning for each assessment

## Completion

When you've completed the checklist execution, ask the user if they would like:
1. More details on specific areas
2. Guidance on implementing key recommendations
3. A prioritized action plan for addressing gaps