# Code Coverage for Unit & Integration Tests



## Steps to Run Tests & Coverage

- Ensure you have the correct libraries downloaded. Libraries requiried are:
    - [Pytest](https://docs.pytest.org/en/stable/getting-started.html)
    - Unittest
    - [Coverage.py](https://coverage.readthedocs.io/en/coverage-5.2.1/)
- Navigate to the directory containing the tests. For example, [tests/integration/JobApplication/](https://github.com/maxgala/aspire-sam/tree/master/tests/integration/JobApplications)
- Execute: ```coverage run -m pytest```. This will run all the tests in all the files of that directory.
- Execute: ```coverage report -m ../../../src/lambda/JobApplications/*/*lambda_function.py``` This will generate a report of all the tests and only match against relevant files (i.e all the lambda_function.py files in the Job Applications endpoint). Change the file structure in that command as necessary.

# Current Coverage Reporting
### Industry Tags
##### Integration Test Total Coverage: 100%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| Create |              19 | 0 | 100% | 
| DeleteById |          19 | 0 | 100% | 
| GetAll |              18 | 0 | 100% | 
| GetById |             16 | 0| 100% | 

##### Unit Test Total Coverage: 100%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| Create |              19 | 0 | 100% | 
| DeleteById |          19 | 0 | 100% | 
| GetAll |              18 | 0 | 100% | 
| GetById |             16 | 0| 100% | 
---
### Job
##### Integration Test Total Coverage: 41%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| CloseJobById |         20 | 9 | 55% | 19-37
| CreateJob |            23 | 10 | 57% | 22-87
| DeleteJobById |        22 | 11 | 50% | 19-42
| EditJobById |          23 | 12| 48% | 19-39
| GetAllJobs |           38 | 27| 29% | 19-52
| GetJobById |           24 | 13| 46% | 19-39
| JobContactById |       49 | 36| 27% | 22-136

##### Unit Test Total Coverage: 88%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| CloseJobById |         20 | 9 | 100% | 
| CreateJob |            23 | 10 | 83% | 72-87
| DeleteJobById |        22 | 11 | 100% | 
| EditJobById |          23 | 12| 96% | 27
| GetAllJobs |           38 | 27| 66% | 25-28, 32, 34, 36, 40-45
| GetJobById |           24 | 13| 96% |  29
| JobContactById |       49 | 36| 92% | 53-54, 91, 136



---
### Job Applications 

##### Integration Test Coverage: 100%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| CreateJobApplication |          21 | 0 | 100% | 
| DeleteJobApplicationById |      22 | 0 | 100% | 
| EditJobApplicationById |        23 | 3 | 100% | 
| GetAllJobApplications |         32 | 0 | 100% | 
| GetJobApplicationById |         19 | 0 | 100% | 

##### Unit Test Coverage: 93%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| CreateJobApplication |          21 | 0 | 100% | 
| DeleteJobApplicationById |      22 | 0 | 100% | 
| EditJobApplicationById |        23 | 3 | 96% | 27
| GetAllJobApplications |         32 | 0 | 78% | 46-56
| GetJobApplicationById |         19 | 0 | 100% | 
---
### Chat 

##### Integration Test Coverage: 79%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| CreateChat |          44 | 0 | 100% | 
| DeleteChatById |      15 | 0 | 100% | 
| EditChatById |        23 | 3 | 87% | 20-23
| GetAllChats |         23 | 0 | 100% | 
| GetChatById |         20 | 0 | 100% | 
| ReserveChatById |     60 | 27 | 55% | 12-42, 63-68, 89, 101, 123
| UnreserveChatById |   46 | 19 | 59% | 17-47

##### Unit Test Coverage: 75%

| Name | Statements | Missed | Covered | Missing Lines 
| --- | --- | --- | --- | ---|
| CreateChat |          44 | 0 | 100% | 
| DeleteChatById |      15 | 0 | 100% | 
| EditChatById |        23 | 3 | 87% | 20-23
| GetAllChats |         23 | 0 | 100% | 
| GetChatById |         20 | 0 | 100% | 
| ReserveChatById |     60 | 27 | 55% | 12-42, 63-68, 89, 101, 123
| UnreserveChatById |   46 | 19 | 59% | 17-47

