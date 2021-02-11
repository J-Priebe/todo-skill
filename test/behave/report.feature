Feature: Reporting

  Scenario: Report simple
    Given an english speaking user
      When the user says "report to do"
      Then "todo-skill" should reply with dialog from "report_num_complete.dialog"
        But mycroft reply should contain "0"

  Scenario: Report completed task
    Given an english speaking user
        And item stuff has been completed
        And item things has been completed
      When the user says "report to do"
      Then "todo-skill" should reply with dialog from "report_num_complete.dialog"
          But mycroft reply should contain "2"
      Then "todo-skill" should reply with dialog from "report_averages.dialog"
          But mycroft reply should contain "2 items per week"
