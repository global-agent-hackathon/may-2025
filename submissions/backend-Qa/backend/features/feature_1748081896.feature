Feature: Online Bookstore
As a user of the Online Bookstore
I want to perform various actions related to registration, login, searching, shopping, and managing my account
So that I can have a seamless and efficient user experience

  Background:
    Given the browser is opened
    And the user is on the homepage

  @registration

  Scenario: Successful User Registration
    Given the user is on the registration page
    When the user enters a valid email "test@example.com"
    And the user enters a valid password "Test1234"
    And the user enters the password again "Test1234"
    Then the user should be redirected to the login page
    And a registration confirmation message should be displayed

  @registration @edge-case

  Scenario: Registration with Invalid Email
    Given the user is on the registration page
    When the user enters an invalid email "invalid-email"
    And the user enters a valid password "Test1234"
    And the user enters the password again "Test1234"
    Then an error message "Please enter a valid email address" should be displayed

  @registration @edge-case

  Scenario: Registration with Missing Fields
    Given the user is on the registration page
    When the user leaves the email field empty
    And the user leaves the password field empty
    Then an error message "Email and password are required" should be displayed

  @registration @edge-case

  Scenario: Registration with Weak Password
    Given the user is on the registration page
    When the user enters a valid email "test@example.com"
    And the user enters a weak password "test"
    And the user enters the password again "test"
    Then an error message "Password must be at least 8 characters long" should be displayed

  @registration @edge-case

  Scenario: Registration with Duplicate Email
    Given the user is on the registration page
    When the user enters an email "existing@example.com" that already exists
    And the user enters a valid password "Test1234"
    And the user enters the password again "Test1234"
    Then an error message "Email already exists" should be displayed

  @login

  Scenario: Successful User Login
    Given the user is on the login page
    When the user enters a valid email "test@example.com"
    And the user enters a valid password "Test1234"
    Then the user should be redirected to the homepage
    And a welcome message should be displayed

  @login @edge-case

  Scenario: Login with Invalid Credentials
    Given the user is on the login page
    When the user enters an invalid email "invalid@example.com"
    And the user enters an invalid password "wrongpass"
    Then an error message "Invalid email or password" should be displayed

  @login @security

  Scenario: Account Lockout After Multiple Failed Attempts