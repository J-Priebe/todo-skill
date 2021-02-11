Feature: List items on to do list
  Scenario: Asking for an empty list
    Given an english speaking user
      When the user says "what's on my to do list"
      Then "todo-skill" should reply with dialog from "empty_list.dialog"

  Scenario: List multiple items
    Given an english speaking user
        And item stuff is on to do list
        And item go to the gym is on to do list
      When the user says "what's on my to do list"
      Then "todo-skill" should reply with dialog from "item_description.dialog"
          But mycroft reply should contain "stuff"
          But mycroft reply should contain "go to the gym"

  Scenario: List item and ignore completed or deleted items
    Given an english speaking user
        And item appointment is on to do list
        And item stuff has been completed
        And item things has been deleted
      When the user says "what's on my to do list"
      Then "todo-skill" should reply with dialog from "item_description.dialog"
          But mycroft reply should contain "appointment"
          But mycroft reply should not contain "stuff"
          But mycroft reply should not contain "things"
