Feature: User Registration
As a new user
I want to register an account with my email and password
So that I can make purchases and track my orders

  @functional @security

  Scenario: Successful registration with valid email and password
    Given I am on the registration page
    When I enter a valid email "user@example.com" and password "StrongPass123!"
    And I click the Register button
    Then I should be redirected to the login page
    And I receive a confirmation email

  @functional @security

  Scenario: Registration with duplicate email
    Given I am on the registration page
    And there is already a user with email "existing@example.com"
    When I enter email "existing@example.com" and password "Pass123"
    And I click the Register button
    Then I should see an error message "Email already exists"
    And I remain on the registration page

  @functional @security

  Scenario: Registration with invalid password
    Given I am on the registration page
    When I enter a valid email "user@example.com" and invalid password "weak"
    And I click the Register button
    Then I should see an error message "Password must be at least 8 characters long"
    And I remain on the registration page

  @functional @security

  Scenario: Registration with missing email
    Given I am on the registration page
    When I leave the email field empty
    And I enter a valid password "StrongPass123!"
    And I click the Register button
    Then I should see an error message "Email is required"
    And I remain on the registration page

  @functional @security

  Scenario: Registration with missing password
    Given I am on the registration page
    When I enter a valid email "user@example.com"
    And I leave the password field empty
    And I click the Register button
    Then I should see an error message "Password is required"
    And I remain on the registration page

  @functional @security

  Scenario: Registration with invalid email format
    Given I am on the registration page
    When I enter an invalid email "invalid_email" and password "StrongPass123!"
    And I click the Register