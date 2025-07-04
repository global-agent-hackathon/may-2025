Feature: User Registration
As a new user
I want to register an account with my email and password
So that I can make purchases and track my orders

  Background:
    Given the user is on the registration page

  @registration @happy-path

  Scenario: Successful User Registration
    Given the user is on the registration page
    When they enter a valid email and password
    Then they should be redirected to the login page
    And they should receive a confirmation email

  @registration @errorHandling

  Scenario: Duplicate Email Registration Attempt
    Given the user is on the registration page
    When they enter an email that already exists in the system
    Then they should see an error message indicating the email is already registered

  @registration @validation

  Scenario: Weak Password Registration Attempt
    Given the user is on the registration page
    When they enter a password without meeting the minimum security requirements
    Then they should see an error message prompting them to use a stronger password

Feature: User Login
As a registered user
I want to log into my account using my credentials
So that I can view and manage my account

  Background:
    Given the user has a registered account
    And the user is on the login page

  @login @happy-path

  Scenario: Successful User Login
    Given the user is on the login page
    When they enter valid login credentials
    Then they should be redirected to their account dashboard
    And they should see their account information displayed

  @login @security

  Scenario: Multiple Failed Login Attempts
    Given the user has exceeded the allowed number of login attempts
    When they enter incorrect credentials again
    Then they should see a message indicating their account is locked due to too many failed attempts

Feature: Search for Books
As a visitor
I want to search for books by title, author, or genre
So that I can find books I'm interested in

  Background:
    Given the user is on the bookstore homepage
    And the search functionality is available

  @search @happy-path

  Scenario: Search for Books by Title
    Given the user is on the homepage
    When they search for a book by