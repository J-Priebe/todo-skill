Feature: Add item on to do list
  Scenario: Add to list
    Given an english speaking user
      When the user says "put go to the gym on my to do list"
      Then "todo-skill" should reply with dialog from "item_added.dialog"
          But mycroft reply should contain "go to the gym"
