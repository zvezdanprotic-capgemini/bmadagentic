# Create Deep Research Prompt Task

## Description

This task helps you create a comprehensive research prompt on a technical topic that can be used to gather in-depth information before making architectural decisions. The goal is to produce a well-structured prompt that will yield thorough, practical, and applicable research results.

## Parameters

- `topic`: The technical topic to research (required)
- `context`: Additional context about how the research will be applied (optional)
- `format`: Desired output format (default: structured markdown)

## Process

1. **Topic Analysis**
   - Break down the topic into key components and subtopics
   - Identify different perspectives or approaches that should be covered
   - Consider technical depth required for the research

2. **Objective Definition**
   - Define clear research objectives based on the topic
   - Articulate how the research will be applied to the project
   - Specify the scope boundaries (what's included/excluded)

3. **Prompt Construction**
   - Create a comprehensive but focused research prompt
   - Include background context for relevance
   - Specify the required depth and technical detail
   - Define the expected output format and structure
   - Include specific questions that must be addressed

4. **Format Guidance**
   - Structure the prompt to encourage organized output
   - Request comparisons where appropriate
   - Ask for evidence-based recommendations
   - Request real-world examples and case studies

## Output Format

The output should be a well-structured research prompt that can be used directly. Example format:

```
# Research Prompt: [Topic]

## Background Context
[Relevant project context and why this research is needed]

## Research Objectives
- [Objective 1]
- [Objective 2]
- [Objective 3]

## Key Questions
1. [Foundational question about the topic]
2. [Question about alternative approaches]
3. [Question about best practices]
4. [Question about implementation considerations]
5. [Question about performance/scalability/security implications]
6. [Question about real-world applications]
7. [Question about limitations or challenges]

## Required Analysis
- [Specific comparison or analysis needed]
- [Trade-offs to be evaluated]
- [Technical details to be explored]

## Output Format
Please structure your response as follows:
1. Executive Summary (3-5 sentences)
2. Technical Overview
3. Approach Comparison
4. Best Practices
5. Implementation Guidance
6. Case Studies or Examples
7. Recommendations
8. References

## Additional Requirements
- Include code examples where relevant
- Provide references to authoritative sources
- Highlight performance considerations
- Note any security implications
```

## Best Practices

1. **Be Specific**: Avoid vague requests; specify exactly what information is needed
2. **Provide Context**: Include why the research is needed and how it will be used
3. **Set Boundaries**: Define the scope to prevent overly broad responses
4. **Request Evidence**: Ask for sources, examples, and justifications
5. **Consider Alternatives**: Request comparison of different approaches
6. **Practical Focus**: Emphasize practical application over theoretical discussion
7. **Structure the Output**: Define how the response should be organized

## Completion

When you've completed the research prompt, review it to ensure:
1. It addresses all aspects of the topic needed for decision-making
2. It's specific enough to yield practical results
3. It includes clear guidance on the expected format and depth
4. It provides enough context for meaningful research

Then provide the completed prompt to the user for review and execution.