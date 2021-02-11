from behave import given
from test.integrationtests.voight_kampff import wait_for_dialog, emit_utterance

@given('item {item} is on to do list')
def given_item_on_to_do_list(context, item):
    emit_utterance(
        context.bus, f'add {item} to my to do list'
    )
    wait_for_dialog(context.bus, 'item_added')
    context.bus.clear_messages()

@given('item {item} has been deleted')
def given_deleted_item(context, item):
    emit_utterance(
        context.bus, f'add {item} to my to do list'
    )
    wait_for_dialog(context.bus, 'item_added')
    emit_utterance(
       context.bus, f'delete item {item} on my to do list' 
    )
    wait_for_dialog(context.bus, 'confirm_delete')
    emit_utterance(
        context.bus, 'yes'
    )
    wait_for_dialog(context.bus, 'delete_confirmed')
    context.bus.clear_messages()


@given('item {item} has been completed')
def given_completed_item(context, item):
    emit_utterance(
        context.bus, f'add {item} to my to do list'
    )
    wait_for_dialog(context.bus, 'item_added')
    emit_utterance(
       context.bus, f'finish {item} on my to do list' 
    )
    wait_for_dialog(context.bus, 'item_complete')

    context.bus.clear_messages()