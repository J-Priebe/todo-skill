Feature: Completing items

  Scenario: Complete an item by description
    Given an english speaking user
        And item stuff is on to do list
      When the user says "finish stuff on my to do list"
      Then "todo-skill" should reply with dialog from "item_complete.dialog"
          But mycroft reply should contain "stuff"

  Scenario: Complete an item by row number
    Given an english speaking user
        And item stuff is on to do list
      When the user says "complete 1 on my to do list"
      Then "todo-skill" should reply with dialog from "item_complete.dialog"
          But mycroft reply should contain "stuff"

  Scenario: Complete an item that doesn't exist
    Given an english speaking user
        And item stuff is on to do list
      When the user says "complete things on my to do list"
      Then "todo-skill" should reply with dialog from "item_not_found.dialog"

  Scenario: Complete an item by partial match
    Given an english speaking user
        And item big complicated task is on to do list
      When the user says "complete complicated thing on my to do list"
      Then "todo-skill" should reply with dialog from "item_complete.dialog"
          But mycroft reply should contain "big complicated task"
