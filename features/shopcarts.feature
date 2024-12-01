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
    And the following items
        | shopcart_id| item_id    | description| quantity   | price      |
        | sb         | knife      | to stab    | 1          | 30         |
        | sb         | rope       | to hang    | 5          | 5          |
        | sb         | charcoal   | to burn    | 20         | 2          |
        | sc         | diamond    | 5 ct       | 5          | 700000     |
        | sc         | house      | NYC        | 1          | 12500000   |

######################################################################
# SHOPCART BDD
######################################################################

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart Service" in the title
    And I should not see "404 Not Found"

Scenario: Create and Read a Shopcart
    When I visit the "Home Page"
    And I set the "shopcart_name" to "shopcart1"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I press the "Clear" button
    And I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "shopcart1" in the "shopcart_name" field

Scenario: Update a Shopcart
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I set the "shopcart_name" to "sd"
    And I copy the "shopcart_id" field
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "shopcart_id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "sd" in the "shopcart_name" field

Scenario: Delete a Shopcart
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I press the "Delete" button
    Then I should see the message "Deleted Shopcart!"
    When I press the "Clear" button
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: List Shopcarts
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "sb" in the results
    And I should see "sc" in the results

Scenario: Query Shopcart by Name
    When I visit the "Home Page"
    And I press the "Clear" button
    # Filtering by Name
    When I set the "shopcart_name" to "sc"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "sc" in the results
    And I should not see "sb" in the results

######################################################################
# ITEM BDD
######################################################################

Scenario: Create and Read Item
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I paste the "shopcart_id_item" field
    Then I should see the message "Success"
    When I set the "item_name" to "pills"
    And I set the "item_description" to "to take"
    And I set the "item_quantity" to "50"
    And I set the "item_price" to "1"
    And I press the "Create Item" button
    Then I should see the message "Success"

    # Read to Verify
    When I leave the "item_name" field empty
    And I leave the "item_description" field empty
    And I leave the "item_quantity" field empty
    And I leave the "item_price" field empty
    And I press the "Retrieve Item" button
    Then I should see "pills" in the "item_name" field
    And I should see "to take" in the "item_description" field
    And I should see "50" in the "item_quantity" field
    And I should see "1" in the "item_price" field

Scenario: Update an Item
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I paste the "shopcart_id_item" field
    Then I should see the message "Success"
    When I set the "item_name" to "pistol"
    And I set the "item_description" to "to shoot"
    And I set the "item_quantity" to "1"
    And I set the "item_price" to "5000"
    And I press the "Create Item" button
    Then I should see the message "Success"

    # Read to Verify
    When I leave the "item_name" field empty
    And I leave the "item_description" field empty
    And I leave the "item_quantity" field empty
    And I leave the "item_price" field empty
    And I press the "Retrieve Item" button
    Then I should see "pistol" in the "item_name" field
    And I should see "to shoot" in the "item_description" field
    And I should see "1" in the "item_quantity" field
    And I should see "5000" in the "item_price" field

Scenario: Delete an Item
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "shopcart_id" field
    And I paste the "shopcart_id_item" field
    Then I should see the message "Success"

    When I press the "Delete Item" button
    And I paste the "shopcart_id_item" field
    # Then I should see the flash message "Success" for item
    And I should not see "knife" in the item results

Scenario: List Items
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"

    When I copy the "shopcart_id" field
    And I paste the "shopcart_id_item" field
    And I press the "Search" button
    Then I should see the flash message "Success" for item
    And I should see "knife" in the item results