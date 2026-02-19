In this repository, I want to create a Mock API for use in a training class. 

The class is called: Create a Multi-Agent Application using CX Agent Studio

In the class exercise, students will create a multi-agent application using CX Agent Studio. This API will be used to demonstrate how to use Conversational Agents and Playbooks to create an Agent with Tools. 

Technical Requirements: 
- The API will be deployed in Cloud Run with no authentication reequired
- I want to program it with Python Fast API
- It does not need "real" behavior, but will simulate API functions from a ficticious online sporting goods store called "Cymbal Sports" (Cymbal is a made-up company name that Google sometimes uses for demos).
- Let's use Firestore (since it is free) to store inventory, users, and carts.
- Let's create a CSV file with realistic-looking inventory for about 100 items. We will load this into Firestore
- Here is an example of 1 inventory item:
```
id: SKU-12345
category: Shoes (or whatever, let's create 6 categories for a Sports store)
title: "Cymbal Aero Running Shoes"
description: "Lightweight performance..."
price: 95.00
inventory_status: IN_STOCK or LOW_STOCK
rating: 4.8
image_url: (Link to a public placeholder image)
```
- Here is a list API functions we need: 
  - saveInventory() - 1-time management function to save CS inventory to Firestore
  - getOrderStatus(order_id)
  - returnOrder(order_id, reason)
  - getProductDetails(item_id)
  - addItemtoCart(item_id, quantity)
  - removeItemfromCart(item_id)
  - createAccount(user_name, password)
  - login(user_name, password)

- Conversational Agents use an OpenAPI Specification when adding tools. We need to provide that, but let's keep the specafication as short as possible. Include the information needed for the Agent to call the API. The serice URL will be required, but will not be known until we deploy the app. Maybe we can read that dynamically from an Environment Variable. 
- Let's keep the code clean and simple. Remember, this is not a real API, but nonetheless we don't want to create a mess. 
- We will need a Dockerfile for Deployment to Cloud Run. 
- Add a Readme.md file that describes the app. 
- Add unit tests


Do you understand what I need? Please ask any questions required to implement the application. 