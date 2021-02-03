from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
import math
from . import db

class Todo(MycroftSkill):
    '''
    Simple to-do list manager that supports the following actions:
    - List items on you to-do list
    - Complete items
    - Delete (archive) items
    - Suggest a random item
    - Report completion statistics
    
    Uses Padicious-style intents. Because a to-do item is so generic,
    I suspect Padacious is a better choice for intent parsing. 
    Otherwise it will collide with other skills too frequently.
    '''

    def __init__(self):
        MycroftSkill.__init__(self)     
        db.init_db()


    # @intent_handler(IntentBuilder('suggest')) # Adapt-style
    @intent_handler('list_items.intent') # Padacious-style
    def handle_list_items(self, message):
        items = db.get_active_items()
        if not items:
            self.speak_dialog('empty_list')
            return
    
        self.speak_dialog('list_items')
        # row_number/partitioning requires version 3.x of sqlite3; 
        # just enumerate in code
        for (i, item) in enumerate(items):
            self.speak_dialog(
                'item_description', 
                {
                    'item_number':i+1, 
                    'item_description': item[0]
                }
            )


    @intent_handler('add_item.intent')
    def handle_add_item(self, message):
        item_description = message.data.get('item')
        db.add_item(item_description)
        self.speak_dialog('item_added', {'item_description': item_description})


    @intent_handler('suggest_item.intent') 
    def handle_suggest_item(self, message):
        suggested_item = db.get_random_active_item()
        if suggested_item is None:
            self.speak_dialog('empty_list')
        else:
            self.speak_dialog(
                'suggest_item', 
                {
                    'item_description': suggested_item
                }
            )


    @intent_handler('delete_item.intent')
    def handle_delete_item(self, message):
        identifier = message.data.get('item')
        item = self.fetch_item(identifier)
        if item is None:
            return
        
        pk, description = item
        if not self.confirm_delete(description):
            self.speak_dialog('deleted_cancelled')
            return
        
        success = db.close_item(pk, 'archived')
        if success:
            self.speak_dialog('delete_confirmed', {'item' : identifier})
        else:
            self.speak_dialog('delete_error', {'item': identifier})


    @intent_handler('complete_item.intent')
    def handle_complete_item(self, message):
        identifier = message.data.get('item')
        item = self.fetch_item(identifier)
        if item is None:
            return
        
        pk, description = item
        success = db.close_item(pk, 'complete')
        if success:
            self.speak_dialog('item_complete')
        else:
            self.speak_dialog('complete_error', {'item':identifier})


    @intent_handler('report.intent')
    def handle_report(self, message):
        '''
        Provide a report on a few to-do statistics:
        - Number of items completed
        - Average number of items completed per week
        - Average time (in days) to complete an item
        '''
        num_completed = db.get_num_completed_items()

        self.speak_dialog('report_num_completed', {'num_completed': num_completed})

        earliest_created = db.get_earliest_created_time()
        latest_completed = db.get_latest_completed_time()
        if earliest_created and latest_completed:
            weeks_delta  = math.ceil(
                (latest_completed - earliest_created).total_seconds() / 604800 # seconds per week
            )
            average_completed_per_week = round(
                num_completed / weeks_delta
            )
            average_days_to_completion = db.get_average_days_to_completion()
            self.speak_dialog(
                'report_averages',
                {
                    'average_completed_per_week': average_completed_per_week,
                    'average_days_to_completion': average_days_to_completion
                }
            )


    @intent_handler('help.intent')
    def handle_help(self, message):
        self.speak_dialog('help_intro')
        self.speak_dialog('help_examples')


    def parse_item_number(self, identifier):
        '''
        Try to parse a number from an item descriptor.
        Sometimes padacious will parse 1 as "one", 2 as "to", etc,
        so we add some explicit handling for those cases.
        '''
        tokens = identifier.split(' ')
        # multi-word identifier can't be a number
        if len(tokens) != 1:
            return None

        identifier = tokens[0]
        
        if identifier in ('one', 'won'):
            return 1
        
        if identifier in ('to', 'too', 'two'):
            return 2
        
        if identifier in ('for', 'four', 'fore'):
            return 4
        
        try: 
            return int(identifier)
        except Exception:
            return None


    def fetch_item(self, identifier):
        # attempt to parse out a number (the item's position in the list)
        # from the identifier
        item_number = self.parse_item_number(identifier)
        # truthy check also eliminates invalid nonpositive row numbers
        if item_number:
            item = db.fetch_item_by_row_number(item_number)
            if item is not None:
                return item
        
        # and fall back to matching based on a description
        item = db.fetch_item_by_description(identifier)
        if item is None:
            self.speak_dialog('item_not_found', {'item': identifier})

        return item


    def confirm_delete(self, item):
        resp = self.ask_yesno('confirm_delete', {'item': item})
        return resp == 'yes'
