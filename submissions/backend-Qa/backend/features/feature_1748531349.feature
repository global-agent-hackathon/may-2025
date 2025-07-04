Feature: Online Bookstore

  @security @validation

  Scenario: User registration with weak password
    Given I am on the registration page
    When I enter a weak password "password"
    Then I should see an error message "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one special character"

  @security @error_case

  Scenario: Multiple failed login attempts
    Given I am on the login page
    When I enter invalid credentials 5 times in a row
    Then I should see an error message "Account locked due to multiple failed attempts. Please reset your password."

  @validation @error_case

  Scenario: Search for books with special characters
    Given I am on the search page
    When I search for books with the query "!@#$%^&*()"
    Then I should see a message "No books found matching your search criteria"

  @security @error_case

  Scenario: Unauthorized access to order history
    Given I am not logged in
    When I try to access the order history page
    Then I should be redirected to the login page with a message "Please log in to view your order history"

  @security @validation

  Scenario: Adding last available book to cart
    Given There is only one copy of a book in stock
    When I add it to my cart
    Then I should see a success message "Book added to cart"
    And The book should no longer be available for other users to add to cart

  @security @validation

  Scenario: Leaving a review without purchasing the book
    Given I am logged in but have not purchased a book
    When I try to leave a review for that book
    Then I should see an error message "You must purchase this book to leave a review"