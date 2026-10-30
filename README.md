**E-Commerce Data Warehouse & ETL Automation Platform**

**Project Overview**
An end-to-end data engineering portfolio project that processes e-commerce transactional data through an automated ETL pipeline and loads it into a SQL Server data warehouse for analytical reporting.

**Objectives**
Build a structured ETL pipeline using Python and SQL Server.
Implement data quality validation and error handling.
Design a Star Schema data warehouse.
Automate data loading and maintain execution logs.
Demonstrate SQL Server Integration Services (SSIS) data integration.

**Tech Stack**
Database: Microsoft SQL Server 2025, T-SQL
ETL: Python, Pandas, PyODBC, SSIS
Testing: Pytest
Version Control: Git, GitHub
Data Source: CSV files

**Architecture**
CSV Source Files
↓
Python ETL Pipeline
↓
Data Quality Validation & Profiling
↓
SQL Server Staging Database
↓
Star Schema Data Warehouse

SSIS is also used to demonstrate CSV-to-SQL Server data integration.

**Data Warehouse Design**
The warehouse uses a Star Schema consisting of:

dw.DimCustomer
dw.DimProduct
dw.DimDate
dw.FactSales
The fact table contains sales transactions and references the dimension tables through surrogate keys.

**ETL Features**
Source file validation
Data profiling and quality checks
Duplicate record detection
Invalid quantity and missing value handling
Referential integrity validation
Automated staging and warehouse loading
Logging and error handling
Unit testing with Pytest
Project Structure
data/       Raw, processed, and rejected datasets
database/   SQL scripts and database documentation
python/     Python ETL scripts and utilities
ssis/       SSIS packages and solution
tests/      Unit tests
screenshots/Project execution

**How to Run**
1. Clone the repository
git clone (https://github.com/yogaaditya/ecommerce-data-warehouse-etl.git)
cd ecommerce-data-warehouse-etl
2. Create a Python environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
3. Configure SQL Server
Update the SQL Server name and connection settings in python/config.py.

Ensure the required staging and warehouse databases have been created.

4. Run the ETL pipeline
.\.venv\Scripts\python.exe python\pipeline.py
5. Run unit tests
.\.venv\Scripts\python.exe -m pytest tests -v
Data Quality
The sample dataset intentionally contains data quality issues, including:

**Duplicate order records**
Missing customer email values
Invalid quantities
Unknown product references
Duplicate order items
The pipeline identifies and handles these issues according to the implemented ETL rules.

**Project Status**
Python ETL pipeline, SQL Server staging, Star Schema warehouse, unit tests, and initial SSIS data integration packages have been implemented and tested.

Additional integrations and analytics components may be extended in future iterations.

Author
Yoga Aditya
