Feature: Login Page
As a registered user, I want to log into my account using my credentials so that I can view and manage my account.

  Background:
    Given I am on the login page
    And I have a valid user account with email "user@example.com" and password "securepassword"

  @functional @integration

  Scenario: Successful login with valid credentials (Happy Path)
    Given I have entered my email "user@example.com"
    And I have entered my password "securepassword"
    When I click the "Login" button
    Then I should be redirected to the dashboard page
    And I should see a welcome message with my username

  @functional @validation

  Scenario: Login with empty email and password
    When I click the "Login" button without entering any credentials
    Then I should see an error message indicating "Email and password are required"

  @functional @validation

  Scenario: Login with invalid email format
    Given I have entered an invalid email "invalid_email"
    And I have entered my password "securepassword"
    When I click the "Login" button
    Then I should see an error message indicating "Please enter a valid email address"

  @functional @error_handling

  Scenario: Login with wrong credentials
    Given I have entered my email "user@example.com"
    And I have entered an incorrect password "wrongpassword"
    When I click the "Login" button
    Then I should see an error message indicating "Invalid email or password"

  @ui

  Scenario: Show/hide password functionality
    Given I have entered my password "securepassword"
    When I click the "Show Password" toggle
    Then the password field should display the password in plain text
    And I can click the toggle again to hide the password

  @ui

  Scenario: Loading indicator during login
    Given I have entered my email "user@example.com"
    And I have entered my password "securepassword"
    When I click the "Login" button
    Then I should see a loading spinner while the login is being processed

  @functional @security

  Scenario: Remember me functionality
    Given I have entered my email "user@example.com"
    And I have entered my password "securepassword"
    And I have checked the "Remember me" checkbox
    When I click the "Login" button