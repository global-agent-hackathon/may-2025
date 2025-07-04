Feature: Login Page
As a registered user, I want to log into my account using my credentials so that I can access my account securely

  Background:
    Given I am on the login page
    And I have a valid user account

  @functional @happy_path

  Scenario: Successful login with valid credentials
    When I enter a valid email "user@example.com"
    And I enter a valid password "Password123"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message

  @validation @error_handling

  Scenario: Login with empty email field
    When I leave the email field empty
    And I enter a valid password "Password123"
    And I click the login button
    Then I should see an error message "Email is required"
    And I should remain on the login page

  @validation @error_handling

  Scenario: Login with empty password field
    When I enter a valid email "user@example.com"
    And I leave the password field empty
    And I click the login button
    Then I should see an error message "Password is required"
    And I should remain on the login page

  @validation @error_handling

  Scenario: Login with invalid email format
    When I enter an invalid email "invalid-email"
    And I enter a valid password "Password123"
    And I click the login button
    Then I should see an error message "Please enter a valid email address"
    And I should remain on the login page

  @error_handling @security

  Scenario: Login with incorrect password
    When I enter a valid email "user@example.com"
    And I enter an incorrect password "WrongPassword"
    And I click the login button
    Then I should see an error message "Invalid email or password"
    And I should remain on the login page

  @security

  Scenario: Account lockout after multiple failed attempts
    When I enter a valid email "user@example.com"
    And I enter an incorrect password "WrongPassword" 5 times
    Then my account should be temporarily locked
    And I should see a message "Too many failed attempts. Please try again later"

  @ui @accessibility

  Scenario: Show/hide password toggle
    When I enter a password "Password123"
    And I click the show password toggle
    Then the password should be visible as plain text
    When I click the hide password toggle
    Then the password should be masked

  @functional

  Scenario: Remember me functionality
    When I enter a valid email "user@example.com"
    And I enter a valid password "Password123"
    And I check the "Remember me" checkbox
    And I click the login button
    And I close the browser
    And I reopen the browser and navigate to the login page
    Then my email should be pre-filled
    And I should remain logged in

  @functional

  Scenario: Forgot password link
    When I click on the "Forgot password" link
    Then I should be redirected to the password reset page

  @ui

  Scenario: Loading indicator on login
    When I enter a valid email "user@example.com"
    And I enter a valid password "Password123"
    And I click the login button
    Then I should see a loading indicator while the request is processing

  @functional @navigation

  Scenario: Successful login redirection
    When I enter a valid email "user@example.com"
    And I enter a valid password "Password123"
    And I click the login button
    Then I should be redirected to the dashboard page