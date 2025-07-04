Feature: User Registration

  @security @validation

  Scenario: User attempts to register with an insecure password
    Given the user is on the registration page
    When they enter a password with less than 8 characters and no special characters
    Then the system should display an error message requiring a stronger password
    And the registration should not be completed

  @validation @boundary

  Scenario: User tries to register with an already used email address
    Given an existing user with email "test@example.com" already exists
    When a new user tries to register with the same email "test@example.com"
    Then the system should display an error message indicating the email is already registered
    And the registration should not be completed

  @security @performance

  Scenario: Multiple concurrent registration attempts with the same credentials
    Given 10 users attempt to register with the same credentials simultaneously
    When they submit their registration requests at the same time
    Then the system should handle the concurrent requests gracefully
    And only one registration should be successful
    And subsequent attempts should display an error message

Feature: User Login

  @security @validation

  Scenario: User enters invalid credentials multiple times
    Given the user is on the login page
    When they enter an incorrect username and password 5 times consecutively
    Then the system should lock the account
    And display a message indicating the account is locked due to excessive failed attempts

  @security @session

  Scenario: User attempts to access protected pages without being logged in
    Given the user is not logged in
    When they navigate to the order history page
    Then the system should redirect them to the login page
    And display a message requiring authentication

Feature: Search for Books

  @validation @search

  Scenario: User searches for a book with special characters in the query
    Given the user is on the search page
    When they enter a search query containing SQL injection characters (e.g., "DROP TABLE books")
    Then the system should sanitize the input and return relevant search results
    And no error should occur

  @performance @search

  Scenario: Search for books with a very large dataset
    Given the system has a large dataset of 1 million books
    When the user performs a search for "programming"
    Then the search results should be returned within 2 seconds
    And the results should be relevant to the search query

Feature: Add Book to Cart

  @validation @inventory

  Scenario: User tries to add more books to cart than available in stock
    Given the user is on the book details page
    And the book has only 2 copies available in stock
    When they attempt to add 3 copies to the cart
    Then the system should display an error message indicating the maximum available quantity
    And the cart should not be updated with the invalid quantity

  @integration @cart

  Scenario: Add book to cart and verify inventory update
    Given the user is on the book details page
    And the book has 5 copies available in stock
    When they add 2 copies to the cart
    Then the cart should show 2 copies of the book
    And the inventory count should decrease by 2
    And the database should reflect the updated inventory

Feature: Checkout

  @security @payment

  Scenario: User tries to checkout with invalid payment details
    Given the user is on the checkout page
    When they enter invalid credit card information
    Then the system should display a payment failure message
    And the order should not be processed
    And the user should remain on the checkout page

  @integration @payment

  Scenario: Successful payment processing through a third-party gateway
    Given the user is on the checkout page