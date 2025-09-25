# Document Project Task

## Description

This task guides the process of documenting an existing project's architecture, structure, and implementation details. It's designed to create comprehensive documentation for projects that lack proper documentation or need documentation updates.

## Parameters

- `project_path`: Path to the project to document (defaults to current workspace)
- `output_format`: Format for the documentation (markdown, HTML, etc.)
- `detail_level`: Level of detail (overview, standard, comprehensive)

## Process

1. **Project Exploration**
   - Analyze the project structure to understand its organization
   - Identify key components, services, and modules
   - Review configuration files to understand the environment setup
   - Examine build scripts and deployment configurations
   - Review dependencies and external integrations

2. **Architecture Discovery**
   - Identify the architectural pattern(s) being used
   - Map out component relationships and dependencies
   - Discover data models and database schemas
   - Identify API endpoints and service interfaces
   - Understand authentication and authorization mechanisms

3. **Technology Stack Documentation**
   - Document languages, frameworks, and libraries used
   - List development tools and their versions
   - Document build and deployment tooling
   - Identify testing frameworks and approaches
   - Document external services and integrations

4. **Documentation Creation**
   - Create a structured documentation outline
   - Draft each section based on discovered information
   - Include diagrams for visual clarity where appropriate
   - Document code organization and patterns
   - Include setup instructions and prerequisites

5. **Validation and Refinement**
   - Verify accuracy of documented information
   - Ensure documentation is comprehensive yet clear
   - Add examples for key concepts where helpful
   - Ensure consistent terminology throughout

## Output Format

```
# [Project Name] Documentation

## Project Overview
- Purpose: [Brief description of project purpose]
- Status: [Current status]
- Key Features: [List of key features]
- Target Users: [Who uses this project]

## Architecture
- Architectural Style: [e.g., Microservices, Monolith, Event-driven]
- High-level Architecture Diagram: [Include or describe diagram]
- Key Components: [List and briefly describe major components]
- Data Flow: [Describe how data flows through the system]

## Technology Stack
- Languages: [Languages used with versions]
- Frameworks: [Frameworks used with versions]
- Database(s): [Databases used with versions]
- External Services: [External APIs or services integrated]
- Development Tools: [Tools used in development]

## Project Structure
```
[Directory structure with explanations]
```

## Setup Instructions
- Prerequisites: [Required software/accounts]
- Environment Setup: [Steps to set up development environment]
- Configuration: [Configuration options and how to set them]
- Build Process: [How to build the project]
- Run Instructions: [How to run the project]

## Key Components

### [Component 1 Name]
- Purpose: [What this component does]
- Key Files: [Important files in this component]
- Interfaces: [APIs or interfaces exposed]
- Dependencies: [What this component depends on]

[Repeat for each major component]

## Data Models
[Document key data models/entities and their relationships]

## API Documentation
[Document key APIs, endpoints, request/response formats]

## Testing
- Testing Approach: [How the project is tested]
- Test Execution: [How to run tests]
- Test Coverage: [Current test coverage status]

## Deployment
- Deployment Strategy: [How the project is deployed]
- Environments: [Different environments available]
- Deployment Process: [Steps in the deployment process]

## Known Issues and Limitations
[Document any known issues, limitations, or technical debt]

## Future Enhancements
[Planned or suggested improvements]
```

## Best Practices

1. **Be Accurate**: Ensure all documented information is correct
2. **Be Comprehensive**: Cover all major aspects of the project
3. **Be Clear**: Write for developers who are new to the project
4. **Be Structured**: Organize information logically
5. **Use Visuals**: Include diagrams where they add clarity
6. **Document Why, Not Just How**: Explain reasoning behind key decisions
7. **Include Examples**: Provide examples for complex concepts

## Completion

When you've completed the project documentation, review it to ensure:
1. All major components and features are documented
2. Setup instructions are clear and complete
3. Architecture and data flow are clearly explained
4. Technical information is accurate and up-to-date

Then provide the completed documentation to the user for review and feedback.