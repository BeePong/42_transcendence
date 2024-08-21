# ELK Stack Setup for BeePong Project

This README provides instructions on setting up, running, and testing the ELK stack for the BeePong project. The ELK stack is used to collect, analyze, and visualize log data from your application.

## Overview

The ELK stack consists of Elasticsearch, Logstash, and Kibana, supplemented by Metricbeat and Filebeat for log and metric collection. These components work together to provide a solution for monitoring and analyzing application logs and metrics.

## ELK Components and Their Roles

### 1. Elasticsearch

- **Role**: Elasticsearch is a search and analytics engine that stores and indexes log and metric data. It serves as the central repository for all data collected by Logstash and Beats, enabling search capabilities.
- **Configuration**: Configured with SSL/TLS for secure communication, using certificates to authenticate clients and encrypt data in transit.
- **Port**: Accessible on port `9200` (HTTPS).
- **Environment Variables**: 
  - `ELASTIC_PASSWORD`: Password for the `elastic` user.
  - `STACK_VERSION`: Version of the Elastic Stack being used.
- **Data Volume**: Uses a Docker volume `es_data` for persistent data storage.

### 2. Logstash

- **Role**: Logstash is responsible for ingesting and processing log data. It applies filters to transform and enrich the data before sending it to Elasticsearch for storage and indexing.
- **Configuration**: Processes data from multiple sources, including Filebeat and direct file inputs, using a custom `logstash.conf`.
- **Port**: Listens on port `5044` for Beats input.
- **Pipeline Configuration**: The pipeline configuration (`logstash.conf`) defines inputs, filters, and outputs for flexible data processing.

### 3. Kibana

- **Role**: Kibana provides a web interface for visualizing and analyzing data stored in Elasticsearch. It enables the creation of dashboards, charts, and reports to gain insights from the collected data.
- **Configuration**: Connects to Elasticsearch over HTTPS using SSL certificates.
- **Port**: Accessible on port `5601` (HTTPS).
- **Environment Variables**: 
  - `KIBANA_PASSWORD`: Password for the `kibana_system` user.
  - `ENCRYPTION_KEY`: Encryption key for securing saved objects and reporting features.

### 4. Metricbeat

- **Role**: Metricbeat is a lightweight shipper that collects system and service metrics and sends them to Elasticsearch. It provides insights into resource usage, performance, and availability of your infrastructure.
- **Configuration**: Configured to collect metrics from Docker containers, host systems, and other supported modules.
- **Configuration File**: Uses `metricbeat.yml` to define modules and metricsets for data collection.

## 5. Setup

- **Role**: The setup service is a temporary container used to generate and configure SSL/TLS certificates for Elasticsearch and Kibana. It creates certificate authority (CA) files and certificates necessary for secure communication between components.
- **Operation**: Runs a setup script that checks for existing certificates, generates new ones if needed, and sets passwords for the `elastic` and `kibana_system` users.

## How to Run the ELK Stack

### Prerequisites:

- **Docker**: Ensure Docker and Docker Compose are installed on your system.
- **Environment Variables**: Configure the `.env` file with necessary environment variables, including passwords and configuration settings.

### Starting the ELK Stack

To start the ELK stack to monitor the BeePong project, use the following command:

```bash
make up_all_elk
```

This command will build and start the following services additionaly to the BeePong services:

- **Elasticsearch**
- **Kibana**
- **Logstash**
- **Metricbeat**
- **setup:** service will also run initially to generate necessary certificates.

### Verify the Services
After starting the stack, verify that all services are running:

```bash
make ps
```
This command will display the status of all running containers.

### Accessing the Kibana Interface
To access the Kibana interface, follow these steps:

- **Open a Web Browser:** Navigate to https://localhost:5601.

- **Login Credentials:**
    - Username: elastic
    - Password: changeme
    - Important: Change the default password after logging in to ensure security.

- **Explore Dashboards:** Once logged in, you can explore pre-built dashboards, create visualizations, and analyze data stored in Elasticsearch.

## Monitor the ELK Stack

### Monitor globally

```bash
make logs_elk       # Tail all service's logs
make logs_errors    # Tail specifically for ERROR in logs
```

### Monitor logs of services individually

```bash
docker-compose -f ./docker-compose.yml logs -f setup
docker-compose -f ./docker-compose.yml logs -f elasticsearch
docker-compose -f ./docker-compose.yml logs -f logstash
docker-compose -f ./docker-compose.yml logs -f metricbeat
```

## Index Lifecycle Management

### Create Policy
In Kibana's left pane go to `Management / Stack  Management`:
- in `Index Lifecycle Management` click on `Create Policy`:
    - **Name** the policy
    - Configure `Hot Phase` for **testing purposes**:
        - Untick `recommended defaults`, set `Maximum age` to 5 minutes and unset other defaults
        - Click on `Keep data in this phase forever` to switch it to `Delete data after this phase`
    - A new `Delete phase` is now availabel at the bottom of the page, change the `Move data into phase when` set at 365 days to 2 days
    - `Save Policy`

### Create Template
In Kibana's left pane go to `Management / Stack  Management`:
- in `Index Management / Index Template` click on `Create Template`:
    - `Name` your template
    - Add your indexes into `Index patterns` (in the form: whatever-*) 
    - Untick `Create data stream` 
    - `Next` until definition of `Index settings`: 
    ```
       {
         "index": {
           "lifecycle": {
             "name": "Name of choosen policy",
               "rollover_alias": "ilm_rollover_alias defined in output of logstash.conf"
           }
         }
       }
    ```
    - `Next`
    - Aliases will be defined in logstash.conf directly.
    - `Review template` and `Create template`
    

## Future Improvements
- **Enhanced Security:** Implement additional security measures, such as RBAC, IP whitelisting, and encrypted data storage.
- **Advanced Monitoring:** Integrate additional monitoring tools and alerts for proactive system management.
- **Scalability:** Consider scaling Elasticsearch nodes and optimizing configurations for large-scale data ingestion.


