Feature: Asking for help

  Scenario: Ask for to do help
    Given an english speaking user
      When the user says "to do help"
      Then "todo-skill" should reply with dialog from "help_intro.dialog"
      Then "todo-skill" should reply with dialog from "help_examples.dialog"
