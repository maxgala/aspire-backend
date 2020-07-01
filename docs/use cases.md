Sample API Endpoint Use Cases
========
This document is designed to outline and concisely illustrate _some_ sample use cases that the front-end team may encounter. This will hopefully reduce confusion on which endpoints should be used for different scenarios. /n 
 
Use cases are categorized by routes


## Industry Tags

## Jobs

## Job Applications

### 1. I would like to retrieve all job applications in the database
   * **Route:**   ```/job-applications```
   * **Type:** ```GET```
   * **Key-Value Parameters:** ```no keys required``` 
   * **Example:** ```/job-applications/```

### 2. I would like to retrieve all job applications submitted for a specific job
   * **Route:**   ```/job-applications```
   * **Type:** ```GET```
   * **Key-Value Parameters:** ```jobId``` 
   * **Example:** ```/job-applications/?jobId=0010```

### 3. I would like to retrieve all job applications that a specific user has made
   * **Route:**   ```/job-applications```
   * **Type:** ```GET```
   * **Key-Value Parameters:** ```userId``` 
   * **Example:** ```/job-applications/?userId=007```

### 4. I would like to retrieve all job applications that a specific user has used for a specific job
   * **Route:**   ```/job-applications```
   * **Type:** ```GET```
   * **Key-Value Parameters:** ```userId``` and ```jobId```
   * **Example:** ```/job-applications/?userId=007```



   