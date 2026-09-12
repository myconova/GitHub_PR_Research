--Overview--
This project searches GitHub pull requests and organizes them by purpose. 
The goal is to create a searchable database of recent, focused pull requests that may be useful for research and training. 

--Initial Criteria--
A pull request should:
- be recent, within the last 180 days
- change fewer than 500 lines total
- have one primary purpose
- contain enough information to classify its purpose

--Planned Categories--
- Bug fix
- Performance Improvement
- Refactor
- New Feature
- Documentation
- Testing
- Dependency Update
- Build or CI
- Security
- Maintenance

--Planned Workflow
1. Search GitHub for recent pull requests
2. Filter pull requests by size
3. Identify pull requests with a single purpose
4. Classify each pull request
5. Save the result in a structured database
6. Review and improve the classification process
