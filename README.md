# DENNIFY STORE API

Dennify Store API is a RESTFul  service for managing api endpoints of an imaginary ecommerce application. 

## Features

- [x] Anonymous users can only view products unless authenticated as admin for other operations
- [x] Pagination, Filtering, and Sorting at the products endpoint
- [x] Anonymous users can add items to their cart without a login
- [x] Authenticated users can create, retrieve, update and delete an order
- [x] Customers can view their profile
- [x] Users are automatically profiled as customers when they are registered
- [x] Admin (staff) Users have access within their control
- [x] SuperAdmin users have all accesses and permissions


### FOR LOCAL DEVELOPMENT

- CLONE THE REPOSITORY

```bash
git clone https://github.com/dennisappiah/dennify-store-api.git
```

- INSTALL DEPENDENCIES USING PACKAGE MANAGER

```bash
cd dennify-store-api
pipenv install
pipenv shell
```
- INSTALL DEPENDENCIES DOCKER-COMPOSE
- 
```bash
cd dennify-store-api
run "docker-compose" build to build application image
run "docker-compose up -d" to start application
```
