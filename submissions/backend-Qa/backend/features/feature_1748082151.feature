Feature: Online Bookstore
As a user
I want to perform various operations on an online bookstore

  Background:
    Given the bookstore is available online
    And the database contains books and user accounts

  @Registration

  Scenario: Successful user registration
    Given I am on the registration page
    When I enter a valid email "test@example.com"
    And I enter a valid password "Test@1234"
    And I confirm the password "Test@1234"
    Then a registration confirmation email should be sent

  @Registration @EdgeCase

  Scenario: Duplicate email registration
    Given I am on the registration page
    And a user with email "existing@example.com" already exists
    When I enter the email "existing@example.com"
    And I enter a valid password "Test@1234"
    And I confirm the password "Test@1234"

  @Registration @ErrorCondition

  Scenario: Invalid password registration
    Given I am on the registration page
    When I enter a valid email "test@example.com"
    And I enter an invalid password "password"

  @Registration @EdgeCase

  Scenario: Missing required fields
    Given I am on the registration page
    When I leave the email field empty
    And I leave the password field empty
    And I click the register button

  @Registration @Security

  Scenario: Email format validation
    Given I am on the registration page
    When I enter an invalid email "invalid-email"
    And I enter a valid password "Test@1234"
    And I confirm the password "Test@1234"

  @Login

  Scenario: Successful user login
    Given I am on the login page
    And a user with email "test@example.com" exists
    When I enter the email "test@example.com"
    And I enter the password "Test@1234"
    And I click the login button

  @Login @ErrorCondition

  Scenario: Invalid credentials login
    Given I am on the login page
    When I