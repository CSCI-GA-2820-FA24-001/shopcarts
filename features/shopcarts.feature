Feature: The shopcarts service back-end
    As a Shopcarts Service Administrator
    I need a RESTful service
    So that I can manage items and shopcarts for users

Background:
    Given the following shopcarts
        | name       |
        | sa         |
        | sb         |
        | sc         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart and Item Management" in the title
    And I should not see "404 Not Found"