from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder

from . import db

class Todo(MycroftSkill):
    '''
    What's on my todo list?
    - lists all active tasks

    What should I do today?
    - suggests a todo item that has been on your list 
      the longest

    Delete/Remove/Archive item # from my to do list

    Mark item # as complete/Complete item # on my todo list

    Give me stats on my todo list
    - # of tasks completed
    - average completion time


    Because ToDos are so generic, and can basically span
    the entirety of language, I think Padacious is a better choice
    for intent parsing. Otherwise it will collide with other skills 
    too frequently. We'll see
    
    '''
    def __init__(self):
        MycroftSkill.__init__(self)     
        db.init_db()

    @intent_handler('list_items.intent')
    def handle_list_items(self, message):
        items = db.get_active_items()
        self.log.info('ITEMS:')
        self.log.info(items)
        # todo factor into dialog file
        self.speak_dialog('Here is your current to-do list')
        # row_number/partitioning requires version 3.x of sqlite3, 
        # so we simply enumerate in code
        for (i, item) in enumerate(items):
            self.speak_dialog(
                # e.g., Item 1: Take out the trash
                f'Item {i + 1}: {item[0]}'
            )

    @intent_handler('add_item.intent')
    def handle_add_item(self, message):
        item_description = message.data.get('item')
        db.add_item(item_description)
        self.speak_dialog(f'I have added {item_description} to your list.')

    # @intent_handler(IntentBuilder('suggest')) # Adapt
    @intent_handler('suggest_item.intent') # Padacious
    def handle_suggest_item(self, message):
        self.speak_dialog('suggest')
        items = db.get_active_items()
        # now we suggest the longest running item

    @intent_handler('delete_item.intent')
    def handle_delete_item(self, message):
        item_number = message.data.get('item_number')
        item_description = message.data.get('item_description')

        # TODO: confirmation converse
        success = False
        if item_number:
            success = db.delete_item_by_row_number(item_number)
        elif item_description:
            success = db.delete_item_by_description(item_description)
        
        if success:
            self.speak_dialog('I deleted that for you')
        else:
            self.speak_dialog('Sorry, I could not do that for you')


    @intent_handler('complete_item.intent')
    def handle_complete_item(self, message):
        db.complete_item()

    @intent_handler('report.intent')
    def handle_report(self, message):
        num_completed = db.get_num_completed_items()
        # average time to completion


    # TODO help request