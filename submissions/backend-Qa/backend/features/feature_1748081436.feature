Feature: feature_1748081436

    Alright, I need to create a comprehensive Gherkin feature file for an online bookstore project. The user has provided the initial feature files for User Registration and User Login, but they want all user stories covered.

    First, I'll list out all the user stories to ensure each is addressed:

    1. User Registration
    2. User Login
    3. Search for Books
    4. Add Book to Cart
    5. Checkout
    6. View Order History
    7. Leave Book Review

    I notice the initial response only covers Registration and Login. I need to create separate feature files for each of the remaining user stories.

    For each feature, I'll include scenarios covering happy paths, edge cases, error conditions, security, and performance.

    Starting with Search functionality, I'll think about different search criteria and edge cases like no results or special characters. Also, performance under load is important.

    Next, Add to Cart should handle adding multiple copies and out-of-stock situations. I'll include scenarios for these and guest access.

    Checkout needs to cover successful payments, declined payments, coupon usage, and guest checkout. Also, handling an updated cart during checkout.

    Viewing Order History should include scenarios for users with and without orders, reordering, and unauthorized access.

    Leaving a Review should handle valid submissions, invalid attempts, and API errors.

    I'll structure each feature with a Background if needed, use Examples for data tables, and ensure each step is clear and automatable. I'll also include security tests, like preventing SQL injection in registration and handling invalid login attempts.

    Finally, I'll compile all these into separate feature files, ensuring each user story is thoroughly covered with all necessary scenarios.


Feature: User Registration
As a new user, I want to register an account with my email and password so that I can make purchases and track my orders.

  Background:
    Given the user is on the registration page
    And the database is empty

  Scenario: Happy Path - Successful Registration
    When the user enters a valid email "test@example.com" and password "Test@1234"
    And clicks the Register button
    Then the user should be redirected to the login page
    And a confirmation email should be sent to "test@example.com"
    And the user should see a message "Registration successful. Please verify your email."

  Scenario: Registration with Existing Email
    Given a user with email "existing@example.com" already exists in the database
    When the user enters email "existing@example.com" and password "Test@1234"
    And clicks the Register button
    Then the user should see an error message "Email already exists. Please use a different email."

  Scenario: Registration with Invalid Password
    When the user enters a password with less than 8 characters "test"
    And clicks the Register button
    Then the user should see an error message "Password must be at least 8 characters long."

  Scenario: Registration with Invalid Email Format
    When the user enters an invalid email format "test.example"
    And clicks the Register button
    Then the user should see an error message "Please enter a valid email address."

  Scenario: Data Variation - Different Email Formats
    Examples:
      | email           |
      | test@example.com |
      | test@example.net |
      | test@example.org |
    When the user enters email "<email>" and password "Test@1234"
    And clicks the Register button
    Then the user should be registered successfully

  Scenario: Error Handling - API Failure
    Given the registration API is down
    When the user enters a valid email and password
    And clicks the Register button
    Then the user should see an error message "Registration failed. Please try again later."

  Scenario: Security Test - Prevent SQL Injection
    When the user enters email "test@example.com" and password "Test@1234"
    And includes malicious SQL characters in the password
    And clicks the Register button
    Then the registration should fail
    And the system should log the attempt as a security incident

Feature: User Login
As a registered user, I want to log into my account using my credentials so that I can view and manage my account.

  Background:
    Given the user is on the login page
    And a user with email "test@example.com" and password "Test@1234" exists in the database

  Scenario: Happy Path - Successful Login
    When the user enters email "test@example.com" and password "Test@1234"
    And clicks the Login button
    Then the user should be redirected to the home page
    And the user should see a welcome message "Welcome, test@example.com"

  Scenario: Login with Invalid Credentials
    When the user enters email "test@example.com" and password "wrongpassword"
    And clicks the Login button
    Then the user should see an error message "Invalid email or password."

  Scenario: Login with Inactive Account
    Given the user's account is